import json
import requests
import re
from typing import Dict, Any, List, Tuple

def call_llm_api(prompt: str, api_config: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    调用LLM API进行批改
    返回: (success, response_text/error_msg)
    """
    try:
        url = f"{api_config['base_url'].rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": api_config.get('model', 'gpt-4o-mini'),
            "messages": [
                {"role": "system", "content": "你是一位专业的教师，负责批改学生的主观题答案。请根据题目、参考答案和评分标准，给出客观公正的评分。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": api_config.get('temperature', 0.3),
            "max_tokens": api_config.get('max_tokens', 500)
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']
        return True, content

    except Exception as e:
        return False, f"API调用失败: {str(e)}"

def test_llm_connection(api_config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    测试LLM API连接
    """
    try:
        url = f"{api_config['base_url'].rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_config['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": api_config.get('model', 'gpt-4o-mini'),
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 5
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return True, "连接成功"
    except Exception as e:
        return False, str(e)

def grade_subjective_question(
    question_text: str,
    reference_answer: str,
    student_answer: str,
    max_score: float,
    grading_criteria: str,
    api_config: Dict[str, Any],
    examples: List[Dict] = None
) -> Tuple[bool, float, str]:
    """
    批改单个主观题
    返回: (success, score, comment)
    """
    # 构建 Few-Shot 示例部分
    few_shot_text = ""
    if examples:
        few_shot_text = "【参考示例 (Few-Shot)】\n以下是教师提供的评分参考示例，请学习其评分尺度和评语风格：\n\n"
        for i, ex in enumerate(examples):
            few_shot_text += f"示例 {i+1}:\n[学生答案]: {ex['student_answer']}\n[评分]: {ex['score']}\n[评语]: {ex['comment']}\n\n"

    
    # Python 3.11 f-string compatibility: define default criteria outside
    default_criteria = '1. 准确性：答案是否涵盖了参考答案的核心要点\n2. 完整性：论述是否全面\n3. 逻辑性：条理是否清晰'
    criteria_text = grading_criteria if grading_criteria else default_criteria

    # 构建批改prompt
    prompt = f"""请批改以下主观题：

【题目】
{question_text}

【参考答案】
{reference_answer}

【评分标准】
满分：{max_score}分
{criteria_text}

{few_shot_text}

【学生答案】
{student_answer}

【批改要求】
1. 请仔细对比学生答案与参考答案及评分标准
2. 给出0到{max_score}之间的分数（可以是小数）
3. **必须给出详细的评分理由**，说明得分点和扣分点

请严格按照以下JSON格式返回结果：
{{"score": 分数, "comment": "详细评语，包含得分理由和建议"}}
"""

    success, response = call_llm_api(prompt, api_config)
    if not success:
        return False, 0.0, response

    # 解析LLM返回的结果
    try:
        # 尝试提取JSON
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response)
        if json_match:
            result_json = json.loads(json_match.group())
            score = float(result_json.get('score', 0))
            comment = result_json.get('comment', '无评语')
            # 确保分数在合理范围内
            score = max(0, min(score, max_score))
            return True, score, comment
        else:
            # 如果没有找到JSON，尝试从文本中提取分数
            score_match = re.search(r'(\d+\.?\d*)\s*分', response)
            if score_match:
                score = float(score_match.group(1))
                score = max(0, min(score, max_score))
                return True, score, response
            else:
                return False, 0.0, f"无法解析LLM响应: {response}"
    except Exception as e:
        return False, 0.0, f"解析失败: {str(e)}"
