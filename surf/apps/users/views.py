"""
This module contains implementation of REST API views for users app.
"""

from urllib.parse import urlparse

import logging

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from oic import rndstr
from oic.oic import Client
from oic.oic.message import AuthorizationResponse
from oic.oic.message import ProviderConfigurationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

from surf.apps.users.models import SurfConextAuth
from surf.apps.communities.models import SurfTeam
from surf.apps.users.serializers import UserDetailsSerializer
from surf.vendor.surfconext.voot.api import VootApiClient

_OIDC_CONFIG = settings.OIDC_CONFIG

_AUTH_REQUEST_TEMPLATE = {
    "scope": _OIDC_CONFIG.get("scope", []),
    "acr_values": _OIDC_CONFIG.get("acr_values", []),
    "response_type": _OIDC_CONFIG.get("response_type", ""),
    "redirect_uri": _OIDC_CONFIG.get("redirect_uri", ""),
    "client_id": _OIDC_CONFIG.get("client_id", "")
}

_OP_CONFIG = dict(
    version=_OIDC_CONFIG.get("version", "1.0"),
    issuer=_OIDC_CONFIG.get("issuer", ""),
    authorization_endpoint=_OIDC_CONFIG.get("authorization_endpoint", ""),
    userinfo_endpoint=_OIDC_CONFIG.get("userinfo_endpoint", ""),
    token_endpoint=_OIDC_CONFIG.get("token_endpoint", ""),
    jwks_uri=_OIDC_CONFIG.get("jwks_uri", ""))

_OP_INFO = ProviderConfigurationResponse(**_OP_CONFIG)

logger = logging.getLogger(__name__)


def login_handler(request, **kwargs):
    """
    This method handle user log in.
    It redirects user to SurfConext OpenID Connect authorization flow
    """
    query_string = "&".join(["{}={}".format(k, v)
                             for k, v in request.GET.items()])

    return redirect("/login/surfconext/?{}".format(query_string))


class LogoutAPIView(APIView):
    """
    View class that provides user log out.
    """

    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()

        return Response(dict(detail="Successfully logged out."))


class UserDetailsAPIView(APIView):
    """
    View class that provides detail information about current user .
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        res = UserDetailsSerializer().to_representation(request.user)
        return Response(res)


def auth_begin_handler(request):
    """
    This method starts OpenID Connect Authorization flow
    :param request:
    :return: redirect URL of authorization endpoint
    """

    redirect_url = request.GET.get('redirect_url', None)
    if not _check_redirect_url(redirect_url):
        raise AuthenticationFailed("Unallowed redirect_url")

    request.session["redirect_url"] = redirect_url
    request.session["state"] = rndstr()
    request.session["nonce"] = rndstr()

    request_args = {
        "state": request.session["state"],
        "nonce": request.session["nonce"],
    }
    request_args.update(_AUTH_REQUEST_TEMPLATE)

    client = _create_oidc_client()
    auth_req = client.construct_AuthorizationRequest(request_args=request_args)
    login_url = auth_req.request(client.authorization_endpoint)
    return redirect(login_url)


def auth_complete_handler(request):
    """
    This method is called by authorization provider and finishes
    OpenID Connect Authorization flow
    :param request:
    :return: redirect URL to frontend endpoint with access token in cookies
    """

    client = _create_oidc_client()
    auth_response = _parse_authentication_response(request.session,
                                                   request.GET,
                                                   client)
    auth_code = auth_response.get("code", "")
    token_response = _make_token_request(request.session, auth_code, client)
    access_token = token_response.get("access_token", "")
    user = _update_or_create_user(access_token, client)
    request.user = user

    redirect_url = request.session.get("redirect_url")
    if redirect_url:
        if not _check_redirect_url(redirect_url):
            raise AuthenticationFailed("Unallowed redirect_url")

        # add access_token to redirect_url
        if '?' not in redirect_url:
            redirect_url = "{}?".format(redirect_url)
        redirect_url = "{}&access_token={}".format(redirect_url,
                                                   user.auth_token.key)

        response = redirect(redirect_url)
        response.set_cookie("access_token", user.auth_token.key)
        return response

    return JsonResponse(dict(access_token=user.auth_token.key))


def _update_or_create_user(access_token, client):
    userinfo = client.do_user_info_request(access_token=access_token)

    sca = SurfConextAuth.update_or_create_user(
        userinfo.get("preferred_username", ""),
        userinfo.get("sub", ""),
        access_token)

    Token.objects.filter(user=sca.user).delete()
    token = Token.objects.create(user=sca.user)
    sca.user.auth_token = token

    _update_or_create_user_communities(sca.user, access_token)

    return sca.user


_MEMBERSHIP_TYPE_MEMBER = "member"
_MEMBERSHIP_TYPE_ADMIN = "admin"


def _update_or_create_user_communities(user, access_token):
    """
    Create or update SurfTeam instances according to SURFconext groups of user
    :param user: user instance
    :param access_token: token to access to SURFconext
    :return:
    """
    vac = VootApiClient(api_endpoint=settings.VOOT_API_ENDPOINT)
    groups = vac.get_groups(access_token)
    if isinstance(groups, list):
        raise TypeError(f"VootApiClient didn't return a list but returned \"{groups}\" instead.")
    teams = []
    admin_teams = []
    for g in groups:
        try:
            membership = g["membership"]["basic"]
            if membership == _MEMBERSHIP_TYPE_ADMIN:
                t, _ = SurfTeam.objects.get_or_create(
                    external_id=g["id"],
                    defaults=dict(name=g["displayName"],
                                  description=g["description"]))
                teams.append(t)
                admin_teams.append(t)

            elif membership == _MEMBERSHIP_TYPE_MEMBER:
                t = SurfTeam.objects.get(external_id=g["id"])
                teams.append(t)

        except (KeyError, SurfTeam.DoesNotExist):
            pass

    user.teams.set(teams)
    user.admin_teams.set(admin_teams)


def _create_oidc_client():
    """
    Create OIDC client to Auth Provider
    :return: OIDC client
    """

    client = Client(client_id=_OIDC_CONFIG.get("client_id", ""),
                    verify_ssl=_OIDC_CONFIG.get("verify_ssl", True),
                    client_authn_method=CLIENT_AUTHN_METHOD)

    client.set_client_secret(_OIDC_CONFIG.get("client_secret", ""))
    client.handle_provider_config(_OP_INFO, _OP_CONFIG.get("issuer", ""))
    return client


def _parse_authentication_response(session, auth_response, client):
    """
    Parse and check data received from Auth Provider after
    authorization code request
    :param session: user session
    :param auth_response: received data
    :param client: OIDC client
    :return: parsed response data
    """

    query_string = []
    for k, v in auth_response.items():
        if isinstance(v, list):
            v = "+".join(v)
        query_string.append("=".join([k, v]))
    query_string = "&".join(query_string)

    auth_response = client.parse_response(AuthorizationResponse,
                                          info=query_string,
                                          sformat="urlencoded")

    if "error" in auth_response:
        err_msg = "Authentication flow error. {}".format(
            auth_response["error"])
        raise AuthenticationFailed(err_msg)

    state = session.get("state")
    if not state or (auth_response["state"] != session["state"]):
        raise AuthenticationFailed("The OIDC state does not match.")

    nonce = session.get("nonce")
    if "id_token" in auth_response and \
                    auth_response["id_token"].get("nonce") != nonce:
        raise AuthenticationFailed("The OIDC nonce does not match.")

    return auth_response


def _make_token_request(session, auth_code, client):
    """
    Request token by authorization code
    :param session: user session
    :param auth_code: authorization code
    :param client: OIDC client
    :return: received data after token request
    """

    args = {
        "code": auth_code,
        "redirect_uri": _OIDC_CONFIG.get("redirect_uri", ""),
        "client_id": client.client_id,
        "client_secret": client.client_secret
    }

    scope = _OIDC_CONFIG.get("scope", ["openid"])
    scope = " ".join(scope)
    token_response = client.do_access_token_request(
        scope=scope,
        state=session.get("state", ""),
        request_args=args)

    return token_response


ALL = '*'


def _check_redirect_url(redirect_url):
    """
    Check if redirect url in list of allowed endpoints
    :param redirect_url: redirect url
    :return: True if redirect url is allowed, False otherwise
    """
    if not redirect_url:
        return True

    allowed_endpoints = settings.ALLOWED_REDIRECT_ENDPOINTS

    if ALL in allowed_endpoints:
        return True

    try:
        endpoint = urlparse(redirect_url).netloc

    except Exception:
        logger.exception("invalid redirect_url: {}".format(redirect_url))
        return False

    if not endpoint:
        return False

    return endpoint in allowed_endpoints
