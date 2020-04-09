from django.conf import settings

from sentry_sdk import capture_message
from social_core.pipeline.partial import partial

from surf.vendor.surfconext.models import PrivacyStatement, DataGoalPermissionSerializer, DataGoalTypes
from surf.vendor.surfconext.voot.api import VootApiClient
from surf.apps.communities.models import Community, Team


@partial
def require_data_permissions(strategy, details, user=None, is_new=False, *args, **kwargs):
    # Load current privacy statement and given permissions by the user or default permission
    privacy_statement = PrivacyStatement.objects.get_latest_active()
    session_permissions = strategy.request.session.get("permissions", [])
    permissions = privacy_statement.get_privacy_settings(user=user, session_permissions=session_permissions)
    # Passing on the permissions to the pipeline
    details['permissions'] = permissions
    # Check if we need decisions on privacy permissions by the user
    # Return to the frontend if we do
    needs_privacy_confirmation = any([
        permission for permission in permissions
        if permission["is_after_login"]
    ])
    if not needs_privacy_confirmation:
        return
    is_undecided = any([
        permission for permission in permissions
        if permission["is_allowed"] is None and permission["is_after_login"]
    ])
    if is_undecided:
        current_partial = kwargs.get('current_partial')
        return strategy.redirect(
            "{}/login/permissions?partial_token={}".format(settings.FRONTEND_BASE_URL, current_partial.token)
        )


def store_data_permissions(strategy, details, user, *args, **kwargs):
    permissions = details["permissions"]
    serializer = DataGoalPermissionSerializer(many=True, context={"user": user})
    for permission in permissions:
        serializer.create(permission)


def get_groups(strategy, details, response, *args, **kwargs):
    # Cancel data processing if permission is not given
    permissions = details["permissions"]
    community_permission = next(
        (permission for permission in permissions if permission["type"] == DataGoalTypes.COMMUNITIES),
        None
    )
    if community_permission is None or not community_permission["is_allowed"]:
        details["groups"] = []
        return
    # Retrieve team data from Voot service to connect communities later
    vac = VootApiClient(api_endpoint=settings.VOOT_API_ENDPOINT)
    groups = vac.get_groups(response.get("access_token"))
    if not isinstance(groups, list):
        capture_message(f"VootApiClient didn't return a list but returned \"{groups}\" instead.")
        groups = []
    details["groups"] = groups


def assign_communities(strategy, details, user, *args, **kwargs):
    user.team_set.all().delete()
    group_urns = [group["id"] for group in details.get("groups", [])]
    teams = []
    for community in Community.objects.filter(external_id__in=group_urns):
        teams.append(Team(user=user, community=community, team_id=community.external_id))
    if len(teams):
        Team.objects.bulk_create(teams)
