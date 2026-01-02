from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
from backend.services.core import parse_text_content
from backend.models.old_models import ExamConfig, ParserConfig
from backend.routers.config import get_config
from backend.routers.settings import get_parser_config
from backend.services.storage import get_storage_service, BaseStorage

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/standard")
async def upload_standard_answer(
    file: UploadFile = File(...),
    config: ExamConfig = Depends(get_config),
    parser_config: ParserConfig = Depends(get_parser_config),
    storage: BaseStorage = Depends(get_storage_service)
):
    try:
        content_bytes = await file.read()

        # Save file to storage
        file.file.seek(0)
        filename = f"standard_{file.filename}"
        storage.save_file(file.file, filename)

        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("gbk")

        # Convert Pydantic models to list of dicts for the service function
        config_dicts = [s.model_dump() for s in config.sections]

        status, data = parse_text_content(content, config_dicts, parser_config.model_dump())
        if not status:
            raise HTTPException(status_code=400, detail=data)

        return {"filename": file.filename, "storage_path": filename, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/students")
async def upload_student_papers(
    files: List[UploadFile] = File(...),
    config: ExamConfig = Depends(get_config),
    parser_config: ParserConfig = Depends(get_parser_config),
    storage: BaseStorage = Depends(get_storage_service)
):
    results = []
    errors = []

    config_dicts = [s.model_dump() for s in config.sections]
    parser_config_dict = parser_config.model_dump()

    for file in files:
        try:
            content_bytes = await file.read()

            # Save file
            file.file.seek(0)
            saved_filename = f"student_{file.filename}"
            storage.save_file(file.file, saved_filename)

            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("gbk", errors="ignore")

            status, data = parse_text_content(content, config_dicts, parser_config_dict)
            if status:
                results.append({"filename": file.filename, "storage_path": saved_filename, "data": data})
            else:
                errors.append({"filename": file.filename, "error": data})
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})

    return {"success": results, "errors": errors}
