from fastapi import APIRouter, HTTPException
from backend.models.old_models import DBConfig, LLMConfig, ParserConfig
from backend.database import reload_engine
from backend.utils.config_utils import (
    read_json, write_json,
    DB_CONFIG_FILE, LLM_CONFIG_FILE, PARSER_CONFIG_FILE
)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# --- DB Settings ---
@router.get("/db", response_model=DBConfig)
async def get_db_config():
    return read_json(DB_CONFIG_FILE, DBConfig)

@router.post("/db", response_model=DBConfig)
async def save_db_config(config: DBConfig):
    try:
        write_json(DB_CONFIG_FILE, config)
        # Attempt to reload DB connection
        reload_engine()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- LLM Settings ---
@router.get("/llm", response_model=LLMConfig)
async def get_llm_config():
    return read_json(LLM_CONFIG_FILE, LLMConfig)

@router.post("/llm", response_model=LLMConfig)
async def save_llm_config(config: LLMConfig):
    try:
        write_json(LLM_CONFIG_FILE, config)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Parser Settings ---
@router.get("/parser", response_model=ParserConfig)
async def get_parser_config():
    return read_json(PARSER_CONFIG_FILE, ParserConfig)

@router.post("/parser", response_model=ParserConfig)
async def save_parser_config(config: ParserConfig):
    try:
        write_json(PARSER_CONFIG_FILE, config)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
