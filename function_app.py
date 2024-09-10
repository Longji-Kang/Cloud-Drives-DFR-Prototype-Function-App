from enums import ACTION_TYPE

import azure.functions as func
import processor as proc
import db_processor as db
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="longji-research-create")
@app.route(route="")
def longji_research_create(req: func.HttpRequest) -> func.HttpResponse:
    info = proc.extract_metadata(req, ACTION_TYPE.CREATE)

    db.update_record(info["file_id"], info["file_name"])

    return func.HttpResponse(
        f'success',
        status_code = 200
    )

@app.function_name(name="longji-research-modified")
@app.route(route="")
def longji_research_modified(req: func.HttpRequest) -> func.HttpResponse:
    info = proc.extract_metadata(req, ACTION_TYPE.MODIFY)

    db.update_record(info["file_id"], info["file_name"])

    return func.HttpResponse(
        f'success',
        status_code = 200
    )

@app.function_name(name="longji-research-delete")
@app.route(route="")
def longji_research_delete(req: func.HttpRequest) -> func.HttpResponse:
    info = proc.extract_metadata(req, ACTION_TYPE.DELETE)

    db.update_record(info["file_id"], info["file_name"])

    return func.HttpResponse(
        f'success',
        status_code = 200
    )