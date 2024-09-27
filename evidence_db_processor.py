from pymongo import MongoClient

import os

def get_collection():
    CONN            = os.environ['CUSTOMCONNSTR_EvidenceStoreConnectionString']
    COLLECTION_NAME = os.environ['EVIDENCE_DB_COLLECTION']
    DB_NAME         = os.environ["MONGO_DB_NAME"]

    client = MongoClient(CONN)

    db         = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    return collection

def create_record(evidence_file: str, plain_hash: str, encrypt_hash: str):
    collection = get_collection()

    data_obj = {
        "evidence_file_id": evidence_file,
        "p_hash": plain_hash,
        "e_hash": encrypt_hash
    }

    collection.insert_one(data_obj)