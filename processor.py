from azure.storage.blob import BlobClient
from enums import ACTION_TYPE, MODIFICATION_TYPE

import azure.functions as func

import json
import random
import string
import os

FILE_NAME_LENGTH = 25

# Blob storage params
CONNECTION_STRING = os.environ["CUSTOMCONNSTR_BlobStorageConnectionString"]
CONTAINER_NAME    = os.environ["BLOB_CONTAINER_NAME"]

def extract_metadata(req_data: func.HttpRequest, action_type: ACTION_TYPE) -> dict:
    # Decode the bytestring of the body of the request to obtain a string
    data_string = req_data.get_body().decode()
    # Decoded string has $ as the first character, remove it so we can parse it as a JSON
    data_string = data_string.replace('$', '', 1)
    # Extract the necessary data from the request
    metadata = extractData(data_string)

    if action_type == ACTION_TYPE.CREATE or action_type == ACTION_TYPE.DELETE:
        metadata["action_type"] = action_type.value
    else:
        # TODO: Logic for determining what type of modification
        print('a')

    # Create a metadata file
    file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

    # Check if file already exists
    blob = BlobClient.from_connection_string(
        conn_str       = CONNECTION_STRING,
        container_name = CONTAINER_NAME,
        blob_name      = file_name
    )

    exists = blob.exists()

    while exists == True:
        file_name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

        blob = BlobClient.from_connection_string(
            conn_str       = CONNECTION_STRING,
            container_name = CONTAINER_NAME,
            blob_name      = file_name
        )

        exists = blob.exists()

    blob.upload_blob(json.dumps(metadata).encode("utf-8"))

    return {
        "file_name": file_name,
        "file_id": metadata["file_id"]
    }

def extractData(req_data: str) -> dict:
    extract = {}

    data = json.loads(req_data)

    extract["file_id"] = data["ID"]

    extract["editor"] = {
        'Name': data["Editor"]["DisplayName"],
        'Email': data["Editor"]["Email"]
    }
    
    extract["modification_timestamp"] = data["Modified"]
    extract["file_name"] = data["{FilenameWithExtension}"]
    extract["file_path"] = data["{FullPath}"]
    extract["file_version"] = data["{VersionNumber}"]

    return extract