from enums import ACTION_TYPE

import azure.functions as func
import processor as proc
import db_processor as db
import evidence_db_processor as evidence_db

import logging

import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

LOGGING_PREFIX = "[DFR Prototype] - "

@app.function_name(name="longji-research-create")
@app.route(route="")
def longji_research_create(req: func.HttpRequest) -> func.HttpResponse:
    data_string = proc.convert_request(req)
    logging_obj = json.loads(data_string)

    f_name = logging_obj["{FilenameWithExtension}"]
    f_id = logging_obj["ID"]
    
    del data_string
    del logging_obj

    logging.info(f"{LOGGING_PREFIX}Evidence gather process started for file creation of {f_name} with file id {f_id}...")
    info = proc.extract_metadata(req, ACTION_TYPE.CREATE)
    logging.info(f"{LOGGING_PREFIX}Evidence gather process completed...")

    logging.info(f"{LOGGING_PREFIX}Storing processed evidence on evidence database...")
    evidence_db.create_record(info["blob_name"], info["evidence_hash"], info["encrypted_evidence_hash"])
    logging.info(f"{LOGGING_PREFIX}Storing evidence file information on evidence linking database...")
    db.create_record(info["file_id"], info["blob_name"], info["file_path"], info["directory"], info["file_name"], info["hash"])
    
    return func.HttpResponse(
        json.dumps({'evidence_file_name': info['blob_name']}),
        status_code = 200
    )

@app.function_name(name="longji-research-modified")
@app.route(route="")
def longji_research_modified(req: func.HttpRequest) -> func.HttpResponse:
    data_string = proc.convert_request(req)
    logging_obj = json.loads(data_string)

    f_name = logging_obj["{FilenameWithExtension}"]
    f_id = logging_obj["ID"]
    
    del data_string
    del logging_obj

    logging.info(f"{LOGGING_PREFIX}Evidence gather process started for file modification of {f_name} with id {f_id}...")
    info = proc.extract_metadata(req, ACTION_TYPE.MODIFY)

    logging.info(f"{LOGGING_PREFIX}Storing processed evidence on evidence database...")
    evidence_db.create_record(info["blob_name"], info["evidence_hash"], info["encrypted_evidence_hash"])
    logging.info(f"{LOGGING_PREFIX}Storing evidence file information on evidence linking database...")
    db.update_record(info["file_id"], info["blob_name"], info["file_path"], info["directory"], info["file_name"], info["hash"])

    return func.HttpResponse(
        json.dumps({'evidence_file_name': info['blob_name']}),
        status_code = 200
    )

@app.function_name(name="longji-research-delete")
@app.route(route="")
def longji_research_delete(req: func.HttpRequest) -> func.HttpResponse:
    data_string = proc.convert_request(req)
    logging_obj = json.loads(data_string)

    f_name = logging_obj["FileNameWithExtension"]
    f_id = logging_obj["ID"]
    
    del data_string
    del logging_obj

    logging.info(f"{LOGGING_PREFIX}Evidence gather process started for file deletion of {f_name} with file id {f_id}...")
    info = proc.process_deleted(req)

    logging.info(f"{LOGGING_PREFIX}Storing processed evidence on evidence database...")
    evidence_db.create_record(info["blob_name"], info["evidence_hash"], info["encrypted_evidence_hash"])
    logging.info(f"{LOGGING_PREFIX}Storing evidence file information on evidence linking database...")
    db.update_record(info["file_id"], info["blob_name"], "DELETED", "DELETED", "DELETED", "DELETED")

    return func.HttpResponse(
        json.dumps({'evidence_file_name': info['blob_name']}),
        status_code = 200
    )