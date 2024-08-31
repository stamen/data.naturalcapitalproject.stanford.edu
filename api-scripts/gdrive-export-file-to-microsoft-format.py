"""Download a Google Drive File in an appropriate Microsoft format.

This script uses the Google Drive MIME type to identify the appropriate
microsoft file format to download the file as.
"""

import os
import pprint
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive",
]

# The full list of mimetypes for google drive native formats is here:
# https://developers.google.com/drive/api/guides/mime-types
MIMETYPES = {
    "application/vnd.google-apps.document":
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
    "application/vnd.google-apps.presentation":
        ("application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"),
    "application/vnd.google-apps.spreadsheet":
        ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"),
}


def main(file_id):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)

    # get metadata of file, get filename and type
    metadata = service.files().get(fileId=file_id).execute()
    pprint.pprint(metadata)

    target_mimetype, extension = MIMETYPES[metadata["mimeType"]]
    target_filename = f"{metadata['name']}{extension}"
    target_filename = target_filename.replace('/', '_')

    request = service.files().export(fileId=file_id, mimeType=target_mimetype)
    with open(target_filename, 'wb') as opened_file:
        opened_file.write(request.execute())


if __name__ == '__main__':
    main(sys.argv[1])
