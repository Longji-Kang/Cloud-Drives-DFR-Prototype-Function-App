from msal import ConfidentialClientApplication
import requests
import hashlib
import os

API_CONNECTION_PARAMS = {
    'client_id': os.environ['CLIENT_ID'],
    'authority': os.environ['MS_AUTHORITY'],
    'secret': os.environ['CLIENT_SECRET']
}

SCOPES = [
    'https://graph.microsoft.com/.default'
]

# Shared Documents drive ID
ROOT_DRIVE_ID = os.environ['ROOT_DRIVE_ID']

def getContentHash(file_id: str, token: str) -> str:
    # https://graph.microsoft.com/v1.0/drives/<drive-id>/items/<item-id>/content
    url = f'https://graph.microsoft.com/v1.0/drives/{ROOT_DRIVE_ID}/items/{file_id}/content'

    bearer = f'Bearer {token}'

    response = requests.get(
        url,
        headers = {
            'Authorization': bearer
        }
    )

    hash_obj = hashlib.md5(response.text.encode())

    return hash_obj.hexdigest()

def get_hash(file_id: str) -> str: 
    msal_app = ConfidentialClientApplication(
        client_id = API_CONNECTION_PARAMS['client_id'],
        client_credential = API_CONNECTION_PARAMS['secret'],
        authority = API_CONNECTION_PARAMS['authority']
    )
    # Request should have 
    # {
    #   'drive_item_id': '<some_id>'
    # }

    # Get token for API calls
    result = msal_app.acquire_token_for_client(
        scopes = SCOPES
    )

    token = result['access_token']

    hash = getContentHash(file_id, token)

    print(hash)

    return hash

def hash_string(content: str) -> str:
    hash_obj = hashlib.md5(content.encode("utf-8"))

    return hash_obj.hexdigest()