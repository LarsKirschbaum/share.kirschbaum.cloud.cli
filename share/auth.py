import os.path

from requests_oauth2client import DeviceAuthorizationPoolingJob, BearerToken, PublicApp, OAuth2ClientCredentialsAuth
from requests_oauth2client import OAuth2Client

client = OAuth2Client(
    token_endpoint="https://id.elite12.de/realms/elite12/protocol/openid-connect/token",
    auth=PublicApp("cloud-share-cli"),
    device_authorization_endpoint="https://id.elite12.de/realms/elite12/protocol/openid-connect/auth/device"
)


def getTokenWithRefreshToken(refresh_token):
    return client.refresh_token(refresh_token)


def getTokenWithAuthorization():
    print("Getting new authorization")
    da_resp = client.authorize_device()
    print("Please verify with the following link: ")
    print(da_resp.verification_uri_complete)

    pool_job = DeviceAuthorizationPoolingJob(client, da_resp)
    resp = None
    while resp is None:
        resp = pool_job()
    assert isinstance(resp, BearerToken)

    with open("cache", "w") as file:
        file.write(resp.refresh_token)
    file.close()

    return resp.access_token


def get_authorization():
    token = ""
    if os.path.isfile("cache"):
        refresh_token = open("cache", "r").readline().strip()
        if refresh_token:
            token = getTokenWithRefreshToken(refresh_token)

    if not token:
        token = getTokenWithAuthorization()

    oauth = OAuth2ClientCredentialsAuth(client, token)
    return oauth
