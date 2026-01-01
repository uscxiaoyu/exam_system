from fastapi import APIRouter, HTTPException
import json
import os
from backend.models import DBConfig, LLMConfig, ParserConfig
from backend.database import reload_engine

router = APIRouter(prefix="/api/settings", tags=["settings"])

CONFIG_DIR = "backend/config"
DB_CONFIG_FILE = os.path.join(CONFIG_DIR, "db_config.json")
LLM_CONFIG_FILE = os.path.join(CONFIG_DIR, "llm_config.json")
PARSER_CONFIG_FILE = os.path.join(CONFIG_DIR, "parser_config.json")

# Ensure config dir exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Helper to read/write JSON
def read_json(filepath, model_class):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return model_class(**data)
        except Exception:
            return model_class()
    return model_class()

def write_json(filepath, model_instance):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(model_instance.model_dump_json(indent=2))

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
