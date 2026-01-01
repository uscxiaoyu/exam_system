from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

class QuestionConfig(BaseModel):
    section_id: str
    match_keyword: str
    name: str
    score: float
    num_questions: int
    question_type: str  # "客观题" or "主观题"
    grading_criteria: Optional[str] = None
    reference_answer: Optional[str] = None # For configuration purposes, standard answer key is usually separate

class ExamConfig(BaseModel):
    exam_name: str
    sections: List[QuestionConfig]

class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.3
    max_tokens: int = 500

class FewShotExample(BaseModel):
    student_answer: str
    score: float
    comment: Optional[str] = None

class SubjectiveGradingRequest(BaseModel):
    question_key: str # e.g. "1-1"
    question_text: str
    reference_answer: str
    student_answer: str
    max_score: float
    grading_criteria: Optional[str] = None
    llm_config: LLMConfig
    examples: Optional[List[FewShotExample]] = None

class GradingResult(BaseModel):
    score: float
    comment: str

class DBConfig(BaseModel):
    user: str = "root"
    password: str = ""
    host: str = "localhost"
    port: int = 3306
    db_name: str = "grade_system"

class ParserConfig(BaseModel):
    # Default header regex: matches "学号: xxx 姓名: xxx 机号: xxx"
    # Note: Regex backslashes need to be handled carefully in JSON/String
    header_regex: str = r"学号[：:]\s*(.*?)\s+姓名[：:]\s*(.*?)\s+机号[：:]\s*(.*)"
    # Default question regex: matches "1. A" or "1.A"
    question_regex: str = r"(\d+)\.\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)?"

class StudentData(BaseModel):
    student_id: str = Field(alias='学号')
    name: str = Field(alias='姓名')
    machine_id: str = Field(alias='机号')
    answers: Dict[str, str] # key: "1-1", value: "A" or text
    scores: Dict[str, float] = {}
    comments: Dict[str, str] = {}
    section_scores: Dict[str, float] = {}
    total_score: float = 0.0
