from fastapi import APIRouter, HTTPException
from typing import List
import json
import os
from backend.models import ExamConfig, QuestionConfig

router = APIRouter(prefix="/api/config", tags=["config"])

CONFIG_FILE = "backend/config/exam_config.json"

# Default config
DEFAULT_CONFIG = {
    "exam_name": "2025_AI_Midterm",
    "sections": [
        {'section_id': '1', 'match_keyword': '一、单项选择题', 'name': '单选得分', 'score': 2.0, 'num_questions': 10, 'question_type': '客观题'},
        {'section_id': '2', 'match_keyword': '二、判断题', 'name': '判断得分', 'score': 2.0, 'num_questions': 10, 'question_type': '客观题'},
        {'section_id': '3', 'match_keyword': '三、选择填空题', 'name': '填空得分', 'score': 3.0, 'num_questions': 5, 'question_type': '客观题'},
        {'section_id': '4', 'match_keyword': '四、综合查询题', 'name': '综合得分', 'score': 6.0, 'num_questions': 3, 'question_type': '客观题'}
    ]
}

@router.get("/", response_model=ExamConfig)
async def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ExamConfig(**data)
        except Exception:
            return ExamConfig(**DEFAULT_CONFIG)
    return ExamConfig(**DEFAULT_CONFIG)

@router.post("/", response_model=ExamConfig)
async def save_config(config: ExamConfig):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(config.model_dump_json(indent=2))
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
