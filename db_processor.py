from pymongo import MongoClient

import os

def get_collection():
    CONN = os.environ["CUSTOMCONNSTR_EvidenceStoreConnectionString"]

    client = MongoClient(CONN)

    DB_NAME         = os.environ["MONGO_DB_NAME"]
    COLLECTION_NAME = os.environ["MONGO_DB_COLLECTION"]

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    return collection

def create_record(file_id: int, blob_name: str, file_path: str, path: str, file_name: str, hash: str):
    collection = get_collection()

    data_obj = {
        "file_id": file_id,
        "current_file_path": file_path,
        "current_directory": path,
        "current_file_name": file_name,
        "evidence_files": [
            blob_name
        ],
        "content_hash": hash
    }

    collection.insert_one(data_obj)

def get_current_path(file_id: int):
    collection = get_collection()

    query_obj = {
        "file_id": file_id
    }

    doc = collection.find_one(query_obj)

    return doc["current_file_path"]

def get_current_file_name(file_id: int):
    collection = get_collection()

    query_obj = {
        "file_id": file_id
    }

    doc = collection.find_one(query_obj)

    return doc["current_file_name"]

def get_current_hash(file_id: int):
    collection = get_collection()

    query_obj = {
        "file_id": file_id
    }

    doc = collection.find_one(query_obj)

    return doc["content_hash"]

def update_record(file_id: int, blob_name: str, file_path: str = None, directory: str = None, file_name: str = None, hash: str = None):
    collection = get_collection()

    query_obj = {
        "file_id": file_id
    }

    update_obj = {
        "$push": {
            "evidence_files": blob_name
        }
    }

    if file_path != None:
        update_obj["$set"] = {
            "current_file_path": file_path
        }

    if directory != None:
        update_obj["$set"].update({
            "current_directory": directory
        })
    
    if file_name != None:
        update_obj["$set"].update({
            "current_file_name": file_name
        })

    if hash != None:
        update_obj["$set"].update({
            "content_hash": hash
        })

    collection.update_one(
        query_obj,
        update_obj
    )