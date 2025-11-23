from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def build_service_from_tokens(access_token, refresh_token, token_expiry, client_id, client_secret):
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        expiry=token_expiry
    )
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    return service

def make_oauth_flow(redirect_uri, client_secrets_file):
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow
