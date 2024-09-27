from azure.storage.blob import BlobClient
from enums import ACTION_TYPE, MODIFICATION_TYPE

import azure.functions as func
import db_processor as db
import get_file_hash as hashint
import encryption as enc

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
    data_string = data_string.replace("$", "", 1)
    # Extract the necessary data from the request
    metadata = extractData(data_string)

    hash = ""

    metadata["action_type"] = action_type.value

    if action_type == ACTION_TYPE.MODIFY:
        # Check if file was renamed or moved
        curr_dir = db.get_current_path(metadata["file_id"])
        curr_file_name = db.get_current_file_name(metadata["file_id"])

        new_dir = metadata["directory"]

        if new_dir == curr_dir:
            # File was moved
            metadata["modification_data_moved"] = {
                "modification_type": MODIFICATION_TYPE.MOVED.value,
                "old_directory": curr_dir,
                "new_directory": new_dir
            }

        new_file_name = metadata["file_name"]

        if curr_file_name != new_file_name:
            metadata["modification_data_renamed"] = {
                "modification_type": MODIFICATION_TYPE.RENAME.value,
                "old_file_name": curr_file_name,
                "new_file_name": new_file_name
            }

        curr_hash = db.get_current_hash(metadata["file_id"])
        new_hash = hashint.get_hash(metadata["drive_item_id"])

        del metadata["drive_item_id"]

        if curr_hash != new_hash:
            hash = new_hash

            metadata["modification_content_modified"] = {
                "modification_type": MODIFICATION_TYPE.CONTENT_MODIFICATION.value,
                "old_hash": curr_hash,
                "new_hash": new_hash
            }
        else:
            hash = curr_hash
    
    if action_type == ACTION_TYPE.CREATE:
        hash = hashint.get_hash(metadata["drive_item_id"])

    # Encrypt metadata file
    content = json.dumps(metadata)
    encrypted_content = enc.encrypt(content)

    # Create a metadata file
    file_name = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

    # Check if file already exists
    blob = BlobClient.from_connection_string(
        conn_str       = CONNECTION_STRING,
        container_name = CONTAINER_NAME,
        blob_name      = file_name
    )

    exists = blob.exists()

    while exists == True:
        file_name = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

        blob = BlobClient.from_connection_string(
            conn_str       = CONNECTION_STRING,
            container_name = CONTAINER_NAME,
            blob_name      = file_name
        )

        exists = blob.exists()

    blob.upload_blob(encrypted_content.encode("utf-8"))

    return {
        "blob_name": file_name,
        "file_id": metadata["file_id"],
        "file_path": metadata["file_path"],
        "file_name": metadata["file_name"],
        "directory": metadata["directory"],
        "hash": hash
    }

def process_deleted(req_data: func.HttpRequest):
     # Decode the bytestring of the body of the request to obtain a string
    data_string = req_data.get_body().decode()
    # Decoded string has $ as the first character, remove it so we can parse it as a JSON
    data_string = data_string.replace("$", "", 1)
    # Extract the necessary data from the request
    metadata = extract_metadata_delete_workflow(data_string)

    metadata["action_type"] = ACTION_TYPE.DELETE.value

    file_name = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

    # Check if file already exists
    blob = BlobClient.from_connection_string(
        conn_str       = CONNECTION_STRING,
        container_name = CONTAINER_NAME,
        blob_name      = file_name
    )

    exists = blob.exists()

    while exists == True:
        file_name = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))

        blob = BlobClient.from_connection_string(
            conn_str       = CONNECTION_STRING,
            container_name = CONTAINER_NAME,
            blob_name      = file_name
        )

        exists = blob.exists()

    blob.upload_blob(json.dumps(metadata).encode("utf-8"))

    return {
        "blob_name": file_name,
        "file_id": metadata["file_id"]
    }

def extractData(req_data: str) -> dict:
    extract = {}

    data = json.loads(req_data)

    extract["file_id"] = data["ID"]

    extract["editor"] = {
        "Name": data["Editor"]["DisplayName"],
        "Email": data["Editor"]["Email"]
    }
    
    extract["modification_timestamp"] = data["Modified"]
    extract["file_name"]              = data["{FilenameWithExtension}"]
    extract["file_path"]              = data["{FullPath}"]
    extract["file_version"]           = data["{VersionNumber}"]
    extract["directory"]              = data["{Path}"]
    extract["drive_item_id"]          = data["{DriveItemId}"]

    return extract

def extract_metadata_delete_workflow(req_data: str):
    extract = {}

    data = json.loads(req_data)

    extract["file_id"] = data["ID"]
    extract["file_name"] = data["FileNameWithExtension"]
    extract["deleted_by"] = data["DeletedByUserName"]
    extract["deleted_time"] = data["TimeDeleted"]

    return extract