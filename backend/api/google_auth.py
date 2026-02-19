from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

# defines what your app is allowed to do --> read only
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.send"
          ]


def get_google_service():
    creds = None

    # load existing credentials if present
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # check if credentials are valid
    if not creds or not creds.valid:

        # refresh token to silently fetch a new access token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # starts a temporary local server, login to Google, approve access, redirected back to localhost
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

