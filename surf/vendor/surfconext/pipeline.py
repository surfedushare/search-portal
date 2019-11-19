from django.conf import settings

from sentry_sdk import capture_message
from social_core.pipeline.partial import partial

from surf.vendor.surfconext.models import DataGoalPermissionSerializer
from surf.vendor.surfconext.voot.api import VootApiClient


@partial
def require_data_permissions(strategy, details, user=None, is_new=False, *args, **kwargs):
    # Check if we need decisions on privacy permissions by the user
    # Return to the frontend if we do
    permissions = strategy.request.session.get("permissions", [])
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
            "{}/login/permissions?partial_token={}".format(settings.FRONTEND_BASE_URL, current_partial)
        )
    # Decisions are made
    # Passing on the permissions to the pipeline
    details['permissions'] = permissions


def store_data_permissions(strategy, details, user):
    permissions = details["permissions"]
    serializer = DataGoalPermissionSerializer(many=True, context={"user": user})
    for permission in permissions:
        serializer.create(permission)


def get_groups(strategy, details, response, *args, **kwargs):
    vac = VootApiClient(api_endpoint=settings.VOOT_API_ENDPOINT)
    groups = vac.get_groups(response.get("access_token"))
    if not isinstance(groups, list):
        capture_message(f"VootApiClient didn't return a list but returned \"{groups}\" instead.")
        groups = []
    details["groups"] = groups
