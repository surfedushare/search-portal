from django.conf import settings

from surf.vendor.surfconext.voot.api import VootApiClient
from social_core.pipeline.partial import partial


@partial
def require_data_permissions(strategy, details, user=None, is_new=False, *args, **kwargs):
    return
    # This will need: permission validation
    # NB: this raises 500 when a partial state gets used twice (which should not happen)
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('permissions'):
        permissions = strategy.request_post()

        if permissions:
            details['permissions'] = permissions
        else:
            current_partial = kwargs.get('current_partial')
            return strategy.redirect(
                '/login/permissions?partial_token={0}'.format(current_partial.token)
            )


def get_groups(strategy, response, *args, **kwargs):
    vac = VootApiClient(api_endpoint=settings.VOOT_API_ENDPOINT)
    groups = vac.get_groups(response.get("access_token"))
    if not isinstance(groups, list):
        raise TypeError(f"VootApiClient didn't return a list but returned \"{groups}\" instead.")
    print(groups)
