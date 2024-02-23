"""Iterate over a google drive folder.

Follow authentication steps at https://developers.google.com/drive/api/quickstart/python




"""
import importlib.util
import os.path
import shutil
import sys
import tempfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

modulename = 'createorupdatedataset'
spec = importlib.util.spec_from_file_location(modulename, 'create-or-update-dataset.py')
createorupdatedataset = importlib.util.module_from_spec(spec)
sys.modules[modulename] = createorupdatedataset
spec.loader.exec_module(createorupdatedataset)

# If modifying these scopes, delete the file token.json.
SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive",
]


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    temp_dir = tempfile.mkdtemp()
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

    try:
        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        #results = (
        #        service.files()
        #        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        #        .execute()
        #)
        #items = results.get("files", [])

        # List out files in the drive identified by this driveId.
        # Parameters needed are NOT obvious, but at least the API error messages
        # are fairly clear.
        results = service.files().list(driveId="0AITmurlcDNxBUk9PVA",
                                       includeItemsFromAllDrives=True,
                                       corpora='drive',
                                       supportsAllDrives=True).execute()

        items_by_filename = {
            item['name']: item for item in results.get("files", [])
        }

        # Determine which files have associated YML files.
        non_yml_files = [
            item for item in results.get("files", []) if not
            item['name'].endswith(".yml")]

        # process each file that has an associated yml file
        for non_yml_file in non_yml_files:
            try:
                yml_file = items_by_filename[f'{non_yml_file["name"]}.yml']
            except KeyError:
                continue

            filepath = os.path.join(temp_dir, yml_file['name'])
            with open(filepath, 'wb') as new_yml_file:
                new_yml_file.write(
                    service.files().get_media(
                        fileId=yml_file['id'],
                        supportsAllDrives=True).execute())

            # upload the yml to CKAN
            createorupdatedataset.main(filepath, private=True,
                                       group="natural-capital-footprint-impact-data")

        # Download the YML
        # Verify that the download link is correctly stated in the YML
        # Do the upload as a private object to CKAN.

        items = results.get("files", [])
        print(items)

        if not items:
            print("No files found.")
            return
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']})")
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

    print(os.listdir(temp_dir))
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
