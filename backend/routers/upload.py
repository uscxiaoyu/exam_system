from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
from backend.services.core import parse_text_content
from backend.models import ExamConfig, ParserConfig
from backend.routers.config import get_config
from backend.routers.settings import get_parser_config

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/standard")
async def upload_standard_answer(
    file: UploadFile = File(...),
    config: ExamConfig = Depends(get_config),
    parser_config: ParserConfig = Depends(get_parser_config)
):
    try:
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("gbk")

        # Convert Pydantic models to list of dicts for the service function
        config_dicts = [s.model_dump() for s in config.sections]

        status, data = parse_text_content(content, config_dicts, parser_config.model_dump())
        if not status:
            raise HTTPException(status_code=400, detail=data)

        return {"filename": file.filename, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/students")
async def upload_student_papers(
    files: List[UploadFile] = File(...),
    config: ExamConfig = Depends(get_config),
    parser_config: ParserConfig = Depends(get_parser_config)
):
    results = []
    errors = []

    config_dicts = [s.model_dump() for s in config.sections]
    parser_config_dict = parser_config.model_dump()

    for file in files:
        try:
            content_bytes = await file.read()
            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("gbk", errors="ignore")

            status, data = parse_text_content(content, config_dicts, parser_config_dict)
            if status:
                results.append({"filename": file.filename, "data": data})
            else:
                errors.append({"filename": file.filename, "error": data})
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    return {"success": results, "errors": errors}
