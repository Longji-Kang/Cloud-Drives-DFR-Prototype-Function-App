from pymongo import MongoClient
from pymongo.collection import Collection

import os

def get_database():
    CONN = os.environ["CUSTOMCONNSTR_EvidenceStoreConnectionString"]

    client = MongoClient(CONN)

    return client

def create_record(file_id: int, blob_name: str, collection: Collection):
    data_obj = {
        "file_id": file_id,
        "evidence_files": [
            blob_name
        ]
    }

    collection.insert_one(data_obj)

def add_evidence(query_obj: dict, blob_name: str, collection: Collection):
    update_obj = {
        "$push": {
            "evidence_files": blob_name
        }
    }

    collection.update_one(
        query_obj,
        update_obj
    )

def update_record(file_id: int, blob_name: str):
    client = get_database()

    DB_NAME         = os.environ["MONGO_DB_NAME"]
    COLLECTION_NAME = os.environ["MONGO_DB_COLLECTION"]

    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    query_obj = { "file_id": file_id }

    

    if collection.count_documents(query_obj) == 0:
        # No record for file id, create one
        create_record(file_id, blob_name, collection)
    else:
        # Already a record, update it with latest evidence file name
        add_evidence(query_obj, blob_name, collection)