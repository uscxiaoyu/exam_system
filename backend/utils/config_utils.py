import json
import os
from typing import Type, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

CONFIG_DIR = "backend/config"
DB_CONFIG_FILE = os.path.join(CONFIG_DIR, "db_config.json")
LLM_CONFIG_FILE = os.path.join(CONFIG_DIR, "llm_config.json")
PARSER_CONFIG_FILE = os.path.join(CONFIG_DIR, "parser_config.json")

# Ensure config dir exists
os.makedirs(CONFIG_DIR, exist_ok=True)

def read_json(filepath: str, model_class: Type[T]) -> T:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return model_class(**data)
        except Exception:
            return model_class()
    return model_class()

def write_json(filepath: str, model_instance: BaseModel) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(model_instance.model_dump_json(indent=2))
