from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

from oic import rndstr
from oic.oic import Client
from oic.oic.message import AuthorizationResponse
from oic.oic.message import ProviderConfigurationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

_verify_ssl = settings.OIDC_CONFIG.get("verify_ssl", False)
_response_type = settings.OIDC_CONFIG.get("response_type", "")
_redirect_uri = settings.OIDC_CONFIG.get("redirect_uri", "")
_client_id = settings.OIDC_CONFIG.get("client_id", "")
_client_secret = settings.OIDC_CONFIG.get("client_secret", "")

_behaviour = {
    "scope": settings.OIDC_CONFIG.get("scope", []),
    "acr_values": settings.OIDC_CONFIG.get("acr_values", [])
}

op_config = dict(
    version=settings.OIDC_CONFIG.get("version", "1.0"),
    issuer=settings.OIDC_CONFIG.get("issuer", ""),

    authorization_endpoint=settings.OIDC_CONFIG.get(
        "authorization_endpoint", ""),

    userinfo_endpoint=settings.OIDC_CONFIG.get("userinfo_endpoint", ""),
    token_endpoint=settings.OIDC_CONFIG.get("token_endpoint", ""),
    jwks_uri=settings.OIDC_CONFIG.get("jwks_uri", ""))

op_info = ProviderConfigurationResponse(**op_config)


def auth_begin_handler(request):
    session = request.session

    redirect_url = request.GET.get('redirect_url', None)
    session["redirect_url"] = redirect_url
    session["state"] = rndstr()
    session["nonce"] = rndstr()

    request_args = {
        "response_type": _response_type,
        "state": session["state"],
        "nonce": session["nonce"],
        "redirect_uri": _redirect_uri,
        "client_id": _client_id
    }
    request_args.update(_behaviour)

    client = _create_oidc_client()
    auth_req = client.construct_AuthorizationRequest(request_args=request_args)
    login_url = auth_req.request(client.authorization_endpoint)
    return redirect(login_url)


def auth_complete_handler(request):
    qs = request.GET
    session = request.session

    request_args = {
        "response_type": _response_type,
        "state": session["state"],
        "nonce": session["nonce"],
        "redirect_uri": _redirect_uri,
        "client_id": _client_id
    }
    request_args.update(_behaviour)

    client = _create_oidc_client()
    auth_response = _parse_authentication_response(request.session, qs, client)
    auth_code = auth_response["code"]
    token_response = _make_token_request(session, auth_code, client)
    print("!!! token_response: {}".format(token_response))
    access_token = token_response["access_token"]
    userinfo = _make_userinfo_request(session, access_token, client)
    print("!!! userinfo: {}".format(userinfo))

    # TODO handle errors
    # TODO read user profile/teams/communities
    # TODO create/update user details
    # TODO create user token

    redirect_url = session.get("redirect_url")
    if redirect_url:
        response = redirect(redirect_url)
        response.set_cookie("access_token", access_token)
        return response

    return JsonResponse(dict(access_token=access_token))


def _create_oidc_client():
    client = Client(client_id=_client_id,
                    verify_ssl=_verify_ssl,
                    client_authn_method=CLIENT_AUTHN_METHOD)

    client.set_client_secret(_client_secret)
    client.handle_provider_config(op_info, op_config["issuer"])
    return client


def _parse_authentication_response(session, auth_response, client):
    query_string = []
    for k, v in auth_response.items():
        if isinstance(v, list):
            v = "+".join(v)
        query_string.append("=".join([k, v]))
    query_string = "&".join(query_string)

    auth_response = client.parse_response(AuthorizationResponse,
                                          info=query_string,
                                          sformat="urlencoded")

    if auth_response["state"] != session["state"]:
        raise Exception("The OIDC state does not match.")

    if "id_token" in auth_response and \
                    auth_response["id_token"]["nonce"] != session["nonce"]:
        raise Exception("The OIDC nonce does not match.")

    return auth_response


def _make_token_request(session, auth_code, client):
    args = {
        "code": auth_code,
        "redirect_uri": _redirect_uri,
        "client_id": client.client_id,
        "client_secret": client.client_secret
    }

    token_response = client.do_access_token_request(
        scope="openid",
        state=session["state"],
        request_args=args)

    return token_response


def _make_userinfo_request(session, access_token, client):
    userinfo_response = client.do_user_info_request(
        access_token=access_token)
    return userinfo_response
