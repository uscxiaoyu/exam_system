import streamlit as st
import pandas as pd
import re
import io
import json
import plotly.express as px
from sqlalchemy import create_engine, text
import requests
from typing import Dict, Any, List, Tuple

# ================= 页面配置与 CSS 美化 =================
st.set_page_config(
    page_title="智能作业批改系统 Pro", 
    layout="wide", 
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* 标题区域 Hero Section */
    .hero-container {
        padding: 2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        background: -webkit-linear-gradient(to right, #ffffff, #e0e0e0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* 卡片容器增强 */
    .stCard {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }
    
    /* 按钮样式优化 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 主按钮 */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
    }
    
    /* 侧边栏美化 */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* 指标卡片优化 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #6c757d;
    }
    
    /* Tabs 样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #dee2e6;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 10px 20px;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #eef2ff;
        color: #4b6cb7;
        font-weight: bold;
        border-bottom: 2px solid #4b6cb7;
    }
    
    /* 提示框样式 */
    .stAlert {
        border-radius: 8px;
        border: none;
        font-size: 0.85rem !important; /* 缩小Alert文字 */
    }
    
    /* Caption 样式微调 */
    [data-testid="stCaptionContainer"] {
        font-size: 0.8rem !important; /* 缩小Caption文字 */
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# ================= 全局配置 =================
# ================= 全局配置 =================
# 默认配置移入 session_state 初始化中

# ================= 配置持久化功能 =================
import os
from datetime import datetime

# 配置文件路径
CONFIG_DIR = "config"
LLM_CONFIG_FILE = os.path.join(CONFIG_DIR, "llm_config.json")
EXAM_CONFIG_FILE = os.path.join(CONFIG_DIR, "exam_config.json")
EXAMPLES_DIR = os.path.join(CONFIG_DIR, "examples")

# 确保配置目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(EXAMPLES_DIR, exist_ok=True)

def save_llm_config(config: Dict[str, Any]):
    """保存LLM配置到文件"""
    try:
        with open(LLM_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存LLM配置失败: {e}")
        return False

def load_llm_config() -> Dict[str, Any]:
    """从文件加载LLM配置"""
    default_config = {
        'base_url': 'https://api.deepseek.com',
        'api_key': '',
        'model': 'deepseek-chat',
        'temperature': 0.3,
        'max_tokens': 500
    }
    
    if os.path.exists(LLM_CONFIG_FILE):
        try:
            with open(LLM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载LLM配置失败: {e}")
            return default_config
    return default_config

def save_exam_config(config: List[Dict]):
    """保存题型配置到文件"""
    try:
        with open(EXAM_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存题型配置失败: {e}")
        return False

def load_exam_config() -> List[Dict]:
    """从文件加载题型配置"""
    if os.path.exists(EXAM_CONFIG_FILE):
        try:
            with open(EXAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载题型配置失败: {e}")
    return None  # 返回None表示使用默认配置

def save_few_shot_examples(exam_name: str, examples: Dict[str, List[Dict]]):
    """保存主观题示例到文件（按考试名称和时间）"""
    if not examples:
        return False
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{exam_name}_{timestamp}.json"
        filepath = os.path.join(EXAMPLES_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
        return True, filename
    except Exception as e:
        print(f"保存示例失败: {e}")
        return False, None

def load_few_shot_examples(exam_name: str = None) -> Dict[str, List[Dict]]:
    """加载主观题示例（根据考试名称加载最新的）"""
    try:
        # 获取所有示例文件
        if not os.path.exists(EXAMPLES_DIR):
            return {}
        
        files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.json')]
        
        if not files:
            return {}
        
        # 如果指定了考试名称，只加载该考试的最新文件
        if exam_name:
            exam_files = [f for f in files if f.startswith(exam_name + '_')]
            if exam_files:
                # 按时间戳排序，取最新的
                exam_files.sort(reverse=True)
                filepath = os.path.join(EXAMPLES_DIR, exam_files[0])
            else:
                return {}
        else:
            # 没有指定考试名称，加载最新的文件
            files.sort(reverse=True)
            filepath = os.path.join(EXAMPLES_DIR, files[0])
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载示例失败: {e}")
        return {}

def list_example_files() -> List[str]:
    """列出所有示例文件"""
    try:
        if not os.path.exists(EXAMPLES_DIR):
            return []
        return sorted([f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.json')], reverse=True)
    except Exception as e:
        print(f"列出示例文件失败: {e}")
        return []

# ================= LLM 批改功能 =================

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
    
    # 构建批改prompt
    prompt = f"""请批改以下主观题：

【题目】
{question_text}

【参考答案】
{reference_answer}

【评分标准】
满分：{max_score}分
{grading_criteria if grading_criteria else '1. 准确性：答案是否涵盖了参考答案的核心要点\n2. 完整性：论述是否全面\n3. 逻辑性：条理是否清晰'}

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
        import re
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

def batch_grade_subjective(
    students_data: List[Dict], 
    standard_key: Dict,
    exam_config: List[Dict], 
    api_config: Dict[str, Any],
    progress_callback=None
) -> List[Dict]:
    """
    批量批改学生的主观题
    返回: 包含批改结果的学生数据列表
    """
    total_students = len(students_data)
    
    # 获取主观题配置
    subjective_sections = [sec for sec in exam_config if sec.get('question_type') == '主观题']
    
    for student_idx, student in enumerate(students_data):
        if progress_callback:
            progress_callback(f"正在批改: {student.get('姓名', '未知')} ({student_idx + 1}/{total_students})")
        
        for sec in subjective_sections:
            sec_id = sec.get('section_id')
            num_questions = sec.get('num_questions', 1)
            reference_answer = sec.get('reference_answer', '')
            grading_criteria = sec.get('grading_criteria', '')
            max_score = sec.get('score', 0)
            question_text = sec.get('match_keyword', '')
            
            # 遍历该大题的所有小题
            for q_num in range(1, num_questions + 1):
                q_key = f"{sec_id}-{q_num}"
                student_answer = student.get(q_key, '')
                
                if not student_answer:
                    student[f'Q{q_key}_score'] = 0.0
                    student[f'Q{q_key}_comment'] = '未作答'
                    continue
                
                # 调用LLM批改
                success, score, comment = grade_subjective_question(
                    question_text=f"{question_text} 第{q_num}题",
                    reference_answer=reference_answer,
                    student_answer=student_answer,
                    max_score=max_score,
                    grading_criteria=grading_criteria,
                    api_config=api_config
                )
                
                if success:
                    student[f'Q{q_key}_score'] = score
                    student[f'Q{q_key}_comment'] = comment
                else:
                    student[f'Q{q_key}_score'] = 0.0
                    student[f'Q{q_key}_comment'] = f'批改失败: {comment}'
    
    return students_data

# ================= 核心逻辑函数 =================


def parse_text_content(content, exam_config):
    """
    解析单个学生答题卡文本内容
    返回: (status, data/error_msg)
    """
    if not content or not content.strip():
        return False, "文件内容为空"

    student_data = {}
    lines = [line.strip() for line in content.split('\n')]
    
    # 1. 提取头部信息 (学号、姓名、机号)
    header_pattern = re.compile(r"学号[：:]\s*(.*?)\s+姓名[：:]\s*(.*?)\s+机号[：:]\s*(.*)")
    
    header_match = None
    for i in range(min(5, len(lines))): # 搜索前5行
        match = header_pattern.search(lines[i])
        if match:
            header_match = match
            break
            
    if not header_match:
        return False, "头部信息缺失 (需包含: 学号:xxx 姓名:xxx 机号:xxx)"
        
    student_data['学号'] = header_match.group(1).strip()
    student_data['姓名'] = header_match.group(2).strip()
    student_data['机号'] = header_match.group(3).strip()

    # 2. 定义各题型的正则提取逻辑
    full_text = content
    
    # 使用配置中的题目定义
    for i, section in enumerate(exam_config):
        sec_title = section['match_keyword']
        question_type = section.get('question_type', '客观题')
        start_idx = full_text.find(sec_title)
        if start_idx == -1:
            continue # 宽容模式：找不到该大题则跳过
        
        # 确定结束位置
        if i < len(exam_config) - 1:
            next_title = exam_config[i+1]['match_keyword']
            end_idx = full_text.find(next_title)
            if end_idx == -1: end_idx = len(full_text)
        else:
            end_idx = len(full_text)
            
        section_text = full_text[start_idx:end_idx]
        sec_id = section.get('section_id', str(i+1))
        
        if question_type == '客观题':
            # 客观题：提取该区域内的所有 "数字. 答案"（短答案）
            lines_in_section = section_text.split('\n')
            for line in lines_in_section:
                # 匹配 "1. A" 或 "1.A" 
                matches = re.findall(r'(\d+)\.\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)?', line)
                for q_num, ans in matches:
                    key = f"{sec_id}-{q_num}"
                    ans = ans.strip().upper() if ans else ""
                    student_data[key] = ans
        else:
            # 主观题：提取长文本答案
            lines_in_section = section_text.split('\n')
            current_q_num = None
            current_answer = []
            
            for line in lines_in_section:
                # 检查是否是新题号的开始
                q_start_match = re.match(r'^(\d+)\.\s*(.*)', line)
                if q_start_match:
                    # 保存之前题目的答案
                    if current_q_num is not None:
                        key = f"{sec_id}-{current_q_num}"
                        student_data[key] = '\n'.join(current_answer).strip()
                    
                    # 开始新题
                    current_q_num = q_start_match.group(1)
                    answer_start = q_start_match.group(2).strip()
                    current_answer = [answer_start] if answer_start else []
                elif current_q_num is not None:
                    # 续接当前题目的答案
                    if line.strip():
                        current_answer.append(line.strip())
            
            # 保存最后一题
            if current_q_num is not None:
                key = f"{sec_id}-{current_q_num}"
                student_data[key] = '\n'.join(current_answer).strip()

    return True, student_data

def calculate_score(student_data, standard_key, exam_config, llm_graded_data=None):
    """
    计算分数，包括各大题得分
    **修正：大小写无关**
    **支持主观题和客观题混合评分**
    llm_graded_data: 已经通过LLM批改的主观题数据 (可选)
    """
    record = {
        '学号': student_data['学号'], 
        '姓名': student_data['姓名'], 
        '机号': student_data['机号']
    }
    
    # 转换为查找字典: section_id -> score
    score_map = {sec.get('section_id', str(i+1)): sec['score'] for i, sec in enumerate(exam_config)}
    # 题型映射
    type_map = {sec.get('section_id', str(i+1)): sec.get('question_type', '客观题') for i, sec in enumerate(exam_config)}
    
    # 初始化各大题得分为0
    section_scores = {sec.get('section_id', str(i+1)): 0 for i, sec in enumerate(exam_config)}
    total_score = 0
    
    # 遍历标准答案进行比对
    for q_key, std_ans in standard_key.items():
        # 排除非题目字段
        if q_key in ['学号', '姓名', '机号']:
            continue
            
        # q_key 格式如 '1-1', '2-1'
        section_id = q_key.split('-')[0]
        score_per_q = score_map.get(section_id, 0)
        question_type = type_map.get(section_id, '客观题')
        
        student_ans = student_data.get(q_key, '')
        
        if question_type == '客观题':
            # 客观题：大小写无关比较
            s_ans_norm = str(student_ans).strip().upper()
            t_ans_norm = str(std_ans).strip().upper()
            
            if s_ans_norm == t_ans_norm:
                score = score_per_q
            else:
                score = 0
            
            # 记录单题得分
            record[f'Q{q_key}'] = score
        else:
            # 主观题：从llm_graded_data中获取分数
            if llm_graded_data and q_key in llm_graded_data:
                score = llm_graded_data[q_key].get('score', 0)
                comment = llm_graded_data[q_key].get('comment', '')
                record[f'Q{q_key}'] = score
                record[f'Q{q_key}_comment'] = comment
            else:
                # 如果没有LLM批改数据，标记为待批改
                score = 0  # 保持数字类型
                record[f'Q{q_key}'] = 0.0  # 统一为数字类型，避免pyarrow转换错误
                record[f'Q{q_key}_comment'] = '⏳ 待批改'  # 在评语中标注状态
        
        # 累加大题得分
        if section_id in section_scores and isinstance(score, (int, float)):
            section_scores[section_id] += score
            total_score += score
    
    # 将大题得分写入 record，使用配置中的列名
    for i, sec in enumerate(exam_config):
        sec_id = sec.get('section_id', str(i+1))
        col_name = sec['name']
        record[col_name] = section_scores.get(sec_id, 0)
        
    record['总分'] = total_score
    return record

# ================= 数据库工具函数 =================

def test_db_connection():
    """
    测试默认数据库连接是否可用
    返回: True表示数据库可连接，False表示不可用
    """
    try:
        # 尝试连接默认的本地数据库
        test_engine = create_engine(
            "mysql+pymysql://root:@localhost:3306/grade_system",
            connect_args={'connect_timeout': 2}  # 2秒超时
        )
        # 尝试执行一个简单查询
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        # 任何异常都表示数据库不可用
        return False

def get_db_engine(user, password, host, port, db_name):
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")

def save_to_mysql(df, exam_name, engine):
    try:
        data_to_save = df.copy()
        # 提取题目列和分项得分列打包JSON
        detail_cols = [c for c in data_to_save.columns if c.startswith('Q') or '得分' in c]
        
        data_to_save['details_json'] = data_to_save[detail_cols].apply(
            lambda x: json.dumps(x.to_dict(), ensure_ascii=False), axis=1
        )
        
        cols_map = {'学号': 'student_id', '姓名': 'student_name', '机号': 'machine_id', '总分': 'total_score'}
        final_df = data_to_save.rename(columns=cols_map)[['student_id', 'student_name', 'machine_id', 'total_score', 'details_json']]
        final_df['exam_name'] = exam_name
        
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM exam_records WHERE exam_name = :name"), {"name": exam_name})
            conn.commit()
            
        final_df.to_sql('exam_records', con=engine, if_exists='append', index=False)
        return True, f"成功归档 {len(final_df)} 条记录"
    except Exception as e:
        return False, str(e)

def delete_exam_record(exam_name, engine):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM exam_records WHERE exam_name = :name"), {"name": exam_name})
            conn.commit()
        return True, f"成功删除考试记录: {exam_name}"
    except Exception as e:
        return False, str(e)

# ================= UI 主程序 =================

# 头部
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎓 智能作业批改系统 Pro</div>
    <div class="hero-subtitle">自动化批阅 • 多模型智能评分 • 数据化教学分析</div>
</div>
""", unsafe_allow_html=True)

# Session State 初始化
if 'processed_data' not in st.session_state: st.session_state.processed_data = []
if 'error_files' not in st.session_state: st.session_state.error_files = {}
if 'standard_key' not in st.session_state: st.session_state.standard_key = None
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# LLM配置初始化（从文件加载）
if 'llm_config' not in st.session_state:
    st.session_state.llm_config = load_llm_config()

# 少样本学习示例数据结构初始化
if 'few_shot_examples' not in st.session_state:
    st.session_state.few_shot_examples = {}

# 主观题批改详情数据结构初始化
if 'subjective_details' not in st.session_state:
    st.session_state.subjective_details = []

# 数据库连接状态检测
if 'db_available' not in st.session_state:
    st.session_state.db_available = test_db_connection()

# 默认考试配置 Config Structure: section_id, match_keyword, name, score, num_questions, question_type
DEFAULT_CONFIG = [
    {'section_id': '1', 'match_keyword': '一、单项选择题', 'name': '单选得分', 'score': 2.0, 'num_questions': 10, 'question_type': '客观题'},
    {'section_id': '2', 'match_keyword': '二、判断题', 'name': '判断得分', 'score': 2.0, 'num_questions': 10, 'question_type': '客观题'},
    {'section_id': '3', 'match_keyword': '三、选择填空题', 'name': '填空得分', 'score': 3.0, 'num_questions': 5, 'question_type': '客观题'},
    {'section_id': '4', 'match_keyword': '四、综合查询题', 'name': '综合得分', 'score': 6.0, 'num_questions': 3, 'question_type': '客观题'}
]

# 题型配置初始化（从文件加载）
if 'exam_config' not in st.session_state:
    loaded_config = load_exam_config()
    st.session_state.exam_config = loaded_config if loaded_config else DEFAULT_CONFIG

# 初始化 DataFrame 状态以保持 Index 稳定性
if 'exam_config_df' not in st.session_state:
    st.session_state.exam_config_df = pd.DataFrame(st.session_state.exam_config)

# 初始化行数追踪，用于判断是新增行还是编辑现有行
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = len(st.session_state.exam_config_df)

# 布局 Tabs - 根据数据库可用性动态显示
if st.session_state.db_available:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 考试设置", "📂 答卷上传", "📊 批改结果", "🤖 主观题详情", "💾 数据库 & 历史"])
else:
    tab1, tab2, tab3, tab4 = st.tabs(["📝 考试设置", "📂 答卷上传", "📊 批改结果", "🤖 主观题详情"])
    tab5 = None  # 数据库不可用时不创建tab5

# --- 侧边栏：LLM配置 ---
with st.sidebar:
    st.header("🤖 LLM批改配置")
    st.caption("用于主观题自动批改")
    
    # 检查是否有主观题
    has_subjective = any(sec.get('question_type') == '主观题' for sec in st.session_state.exam_config)
    
    # 显示状态提示
    if has_subjective:
        st.success("✅ 检测到主观题配置")
    else:
        st.info("💡 提示：在配置表中将题型改为「主观题」后需要配置LLM")
    
    # API Provider 选择
    provider = st.selectbox(
        "选择API服务商", 
        ["DeepSeek",  "OpenAI", "Google (Gemini)", "Custom"],
        help="选择后将自动预填Base URL和推荐模型"
    )
    
    # 预设配置
    provider_configs = {
        "DeepSeek": {
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat"
        },
        "OpenAI": {
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o-mini"
        },
        "Google (Gemini)": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "model": "gemini-1.5-flash"
        },
        "Custom": {
            "base_url": st.session_state.llm_config['base_url'],
            "model": st.session_state.llm_config['model']
        }
    }
    
    # 自定义回调用于更新session state (当provider改变时)
    current_defaults = provider_configs.get(provider, {})
    
    # 每次provider变化或未设置时，使用默认值；否则保留用户输入
    # 为了更友好的交互，我们仅在provider不为Custom且当前值与预设不符（或者想要强制重置）时提供简单的填充
    # 这里采用简单策略：Text Input的value受provider影响，允许用户随后修改
    
    # 如果用户刚切换了provider，我们需要更新显示的值
    # Streamlit的重跑机制下，我们可以通过key来管理状态，但这里简单起见，
    # 我们根据provider选择动态设置text_input的默认value
    
    # 逻辑：如果当前选择的provider不是上次的provider，则更新默认值
    if 'last_provider' not in st.session_state:
        st.session_state.last_provider = "DeepSeek"
        
    if st.session_state.last_provider != provider:
        st.session_state.last_provider = provider
        if provider != "Custom":
            default_base_url = current_defaults['base_url']
            default_model = current_defaults['model']
        else:
            # 切换到Custom时保持当前值
            default_base_url = st.session_state.llm_config.get('base_url', '')
            default_model = st.session_state.llm_config.get('model', '')
    else:
        # 保持当前session_state中的值（如果有的话），或者是当前的输入值
        # 这里为了简化，我们直接取 llm_config 的值作为默认值，
        # 但如果用户点击了保存才更新 llm_config。
        # 这里实际上 text_input 的 value 参数只是初始值。
        
        # 更好的做法：使用 session state 的值作为 value，但如果 provider 改变了，我们可能需要重置这些值？
        # 最简单的做法：
        if provider != "Custom":
             default_base_url = current_defaults['base_url']
             default_model = current_defaults['model']
        else:
             default_base_url = st.session_state.llm_config.get('base_url', '')
             default_model = st.session_state.llm_config.get('model', '')

    # LLM配置表单（始终显示）
    llm_base_url = st.text_input(
        "API Base URL", 
        value=default_base_url,
        help="支持OpenAI兼容接口"
    )
    llm_api_key = st.text_input(
        "API Key", 
        value=st.session_state.llm_config['api_key'],
        type="password",
        help="您的API密钥"
    )
    llm_model = st.text_input(
        "Model", 
        value=default_model,
        help="例如: deepseek-chat, gpt-4o"
    )
    llm_temperature = st.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state.llm_config['temperature'],
        step=0.1,
        help="控制生成的随机性，0为确定性，1为高随机性"
    )
    
    if st.button("💾 保存LLM配置"):
        st.session_state.llm_config = {
            'base_url': llm_base_url,
            'api_key': llm_api_key,
            'model': llm_model,
            'temperature': llm_temperature,
            'max_tokens': 500
        }
        # 同步保存到文件
        if save_llm_config(st.session_state.llm_config):
            st.success("✅ LLM配置已保存并持久化!")
            st.warning("⚠️ 保存到文件失败，下次启动时可能丢失")
            
    # 连接测试
    if st.button("🔗 测试连接"):
        with st.spinner("正在连接API..."):
            success, msg = test_llm_connection(st.session_state.llm_config)
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ 连接失败: {msg}")
        
    # 显示配置状态
    if has_subjective:
        if st.session_state.llm_config['api_key']:
            st.success("✅ API Key已配置")
        else:
            st.warning("⚠️ 请配置API Key以批改主观题")
    
    st.divider()
    st.caption("💡 使用说明：在配置表中选择「主观题」→ 填写参考答案 → 配置LLM API → 批量阅卷")

# --- Tab 1: 考试设置 ---
with tab1:
    st.info("📝 考试题型与分值配置")
    exam_name_input = st.text_input("考试名称 (归档标签)", "2025_AI_Midterm")
    
    st.markdown("###### 题型配置表 (可增删改)")
    # 使用 Data Editor 允许用户修改配置
    edited_df = st.data_editor(
        st.session_state.exam_config_df,
        column_config={
            "section_id": "序号(ID)",
            "match_keyword": "识别关键字 (如: 一、单项选择题)",
            "name": "报表列名 (如: 单选得分)",
            "score": st.column_config.NumberColumn("每题分值", min_value=0, max_value=100, step=0.5),
            "num_questions": st.column_config.NumberColumn("题目数量", min_value=1, max_value=100, step=1, help="该题型包含的题目数量"),
            "question_type": st.column_config.SelectboxColumn("题型", options=["客观题", "主观题"], required=True, default="客观题")
        },
        num_rows="dynamic",
        width='stretch',
        key="config_editor_widget"
    )
    
    # 保存配置变更
    if st.button("✅ 应用配置变更"):
        # 转换为List[Dict]
        new_config = edited_df.to_dict('records')
        # 自动补充 section_id
        for i, sec in enumerate(new_config):
            sec['section_id'] = str(i+1)
        
        st.session_state.exam_config = new_config
        st.session_state.exam_config_df = edited_df
        st.session_state.last_row_count = len(edited_df)
        
        # 同步保存到文件
        if save_exam_config(new_config):
            st.success("配置已更新并持久化！")
        else:
            st.success("配置已更新！")
            st.warning("⚠️ 保存到文件失败")
        st.rerun()
    
    # --- 新增：主观题少样本示例配置 ---
    if has_subjective:
        with st.expander("🧠 主观题少样本示例配置 (Few-Shot)", expanded=False):
            st.caption("添加教师自动批改的满分/典型示例，帮助LLM学习您的评分标准")
            
            # 生成所有主观题的小题列表 (question_key: section_id-question_num)
            sub_questions = []
            for sec in st.session_state.exam_config:
                if sec.get('question_type') == '主观题':
                    sec_id = sec['section_id']
                    sec_name = sec['match_keyword']
                    num_questions = sec.get('num_questions', 1)
                    for q_num in range(1, num_questions + 1):
                        q_key = f"{sec_id}-{q_num}"
                        display_name = f"{sec_name} - 第{q_num}题"
                        sub_questions.append((q_key, display_name))
            
            if sub_questions:
                selected_question = st.selectbox("选择题目", options=sub_questions, format_func=lambda x: x[1])
                selected_q_key = selected_question[0]
                
                # 显示现有示例
                current_examples = st.session_state.few_shot_examples.get(selected_q_key, [])
                if current_examples:
                    st.markdown("###### 已添加示例：")
                    for i, ex in enumerate(current_examples):
                        with st.container():
                            st.text(f"示例 {i+1} [得分: {ex['score']}]")
                            st.caption(f"答案: {ex['student_answer'][:50]}...")
                            if st.button(f"🗑️ 删除示例 {i+1}", key=f"del_ex_{selected_q_key}_{i}"):
                                current_examples.pop(i)
                                st.session_state.few_shot_examples[selected_q_key] = current_examples
                                st.rerun()
                            st.divider()
                
                # 添加新示例表单
                st.markdown("###### 添加新示例")
                with st.form(key=f"add_ex_form_{selected_q_key}"):
                    ex_answer = st.text_area("学生示例答案", height=100)
                    c1, c2 = st.columns([1, 2])
                    ex_score = c1.number_input("教师评分", min_value=0.0, step=0.5)
                    ex_comment = c2.text_input("教师评语 (可选)")
                    
                    if st.form_submit_button("➕ 添加示例"):
                        if not ex_answer:
                            st.error("答案不能为空！")
                        else:
                            if selected_q_key not in st.session_state.few_shot_examples:
                                st.session_state.few_shot_examples[selected_q_key] = []
                            
                            st.session_state.few_shot_examples[selected_q_key].append({
                                "student_answer": ex_answer,
                                "score": ex_score,
                                "comment": ex_comment
                            })
                            st.success("示例添加成功！")
                            st.rerun()
                
                # 示例管理功能
                st.divider()
                st.markdown("###### 示例管理")
                col_save, col_load = st.columns(2)
                
                with col_save:
                    if st.button("💾 保存当前示例", width='stretch'):
                        if st.session_state.few_shot_examples:
                            result = save_few_shot_examples(exam_name_input, st.session_state.few_shot_examples)
                            if result[0]:
                                st.success(f"✅ 示例已保存: {result[1]}")
                            else:
                                st.error("❌ 保存失败")
                        else:
                            st.warning("⚠️ 没有可保存的示例")
                
                with col_load:
                    example_files = list_example_files()
                    if example_files:
                        selected_file = st.selectbox(
                            "加载历史示例", 
                            options=example_files,
                            label_visibility="collapsed",
                            key="load_examples_select"
                        )
                        if st.button("📥 加载示例", width='stretch'):
                            # 从文件名提取考试名
                            exam_name_from_file = selected_file.rsplit('_', 2)[0]
                            loaded_examples = load_few_shot_examples(exam_name_from_file)
                            if loaded_examples:
                                st.session_state.few_shot_examples = loaded_examples
                                st.success(f"✅ 已加载 {len(loaded_examples)} 个题目的示例")
                                st.rerun()
                            else:
                                st.error("❌ 加载失败")
                    else:
                        st.caption("暂无历史示例")
            else:
                st.warning("暂无配置为主观题的题目")
    
    # 如果 edited_df 有变化，提示用户保存
    if not edited_df.equals(st.session_state.exam_config_df):
        st.warning("⚠️ 配置已修改但未保存，请点击上方「应用配置变更」按钮")

    # 下载模版功能
    def generate_template(config):
        content = "学号：       姓名：         机号：\n\n"
        for item in config:
            # 获取题目数量，如果没有则默认为5
            num_q = item.get('num_questions', 5)
            score_per_q = item.get('score', 0)
            
            content += f"{item['match_keyword']}（每题{score_per_q}分，共{num_q}题）\n"
            
            # 根据题目数量生成题号
            for q_num in range(1, num_q + 1):
                content += f"{q_num}. \n"
            content += "\n"
        return content

    template_txt = generate_template(st.session_state.exam_config)
    st.download_button(
        label="📥 下载答题卡模版",
        data=template_txt,
        file_name="答题卡模版.txt",
        mime="text/plain",
        help="根据当前配置生成标准格式的答题卡模版"
    )
    
# --- Tab 2: 答卷上传 ---
with tab2:
    st.success("📂 文件上传区域")
    # 标准答案
    std_file = st.file_uploader("1. 上传标准答案 (txt)", type=['txt'], key="std")
    if std_file:
        try:
            content = std_file.getvalue().decode("utf-8")
        except:
            content = std_file.getvalue().decode("gbk")
        # 传递配置
        status, data = parse_text_content(content, st.session_state.exam_config)
        if status:
            st.session_state.standard_key = data
            st.caption(f"✅ 标准答案解析成功，共 {len(data)} 道题")
            with st.expander("查看标准答案详情"):
                st.write(data)
        else:
            st.error(f"标准答案解析失败: {data}")

    # 学生答卷
    # 清空按钮与上传组件
    c_up_header, c_up_btn = st.columns([0.7, 0.3])
    c_up_header.write("2. 上传学生答卷 (多选 txt)")
    if c_up_btn.button("🗑️ 清空列表"):
        st.session_state.uploader_key += 1
        st.session_state.processed_data = []
        st.session_state.error_files = {}
        st.rerun()
        
    student_files = st.file_uploader("2. 上传学生答卷 (多选 txt)", type=['txt'], accept_multiple_files=True, label_visibility="collapsed", key=f"stu_file_uploader_{st.session_state.uploader_key}")
    
    # 开始处理按钮
    if st.button("🚀 开始批量阅卷", type="primary", width='stretch'):
        if not st.session_state.standard_key:
            st.warning("请先上传并解析标准答案！")
        elif not student_files:
            st.warning("请上传学生答卷！")
        else:
            # 检查是否有主观题
            has_subjective = any(sec.get('question_type') == '主观题' for sec in st.session_state.exam_config)
            
            # 如果有主观题，检查LLM配置
            if has_subjective and not st.session_state.llm_config.get('api_key'):
                st.error("❌ 配置中包含主观题，但未配置LLM API Key！请在左侧边栏配置。")
            else:
                processed = []
                errors = {}
                progress_placeholder = st.empty()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 第一阶段：解析所有学生答卷
                status_text.info("📖 阶段1/2: 解析学生答卷...")
                students_data = []
                
                for idx, file in enumerate(student_files):
                    progress_bar.progress((idx + 1) / len(student_files) / 2)  # 前50%进度
                    try: 
                        content = file.getvalue().decode("utf-8")
                    except: 
                        content = file.getvalue().decode("gbk", errors='ignore')
                        
                    # 传递配置
                    status, res = parse_text_content(content, st.session_state.exam_config)
                    if status:
                        students_data.append(res)
                    else:
                        errors[file.name] = res
                
                # 第二阶段：批改（包括主观题LLM批改）
                if students_data:
                    if has_subjective:
                        status_text.info("🤖 阶段2/2: 批改主观题（调用LLM）...")
                        
                        # 清空之前的主观题详情
                        st.session_state.subjective_details = []
                        
                        # 创建进度展示容器
                        progress_detail_container = st.container()
                        
                        # 为每个学生批改主观题
                        for idx, student_data in enumerate(students_data):
                            progress_bar.progress(0.5 + (idx + 1) / len(students_data) / 2)  # 后50%进度
                            
                            # 显示当前批改学生信息
                            with progress_detail_container:
                                with st.expander(f"📝 正在批改: {student_data.get('学号')} - {student_data.get('姓名', '未知')} ({idx + 1}/{len(students_data)})", expanded=True):
                                    current_student_info = st.empty()
                            
                            # 为这个学生批改所有主观题
                            llm_graded = {}
                            for sec in st.session_state.exam_config:
                                if sec.get('question_type') == '主观题':
                                    sec_id = sec.get('section_id')
                                    num_questions = sec.get('num_questions', 1)
                                    grading_criteria = sec.get('grading_criteria', '')
                                    max_score = sec.get('score', 0)
                                    question_text = sec.get('match_keyword', '')
                                    
                                    for q_num in range(1, num_questions + 1):
                                        q_key = f"{sec_id}-{q_num}"
                                        student_answer = student_data.get(q_key, '')
                                        
                                        # 从standard_key获取参考答案
                                        reference_answer = st.session_state.standard_key.get(q_key, '')
                                        
                                        if not student_answer:
                                            llm_graded[q_key] = {'score': 0.0, 'comment': '未作答'}
                                            continue
                                        
                                        # 获取 Few-Shot 示例（按小题级别 q_key）
                                        examples = st.session_state.few_shot_examples.get(q_key, [])
                                        
                                        # 调用LLM批改
                                        success, score, comment = grade_subjective_question(
                                            question_text=f"{question_text} 第{q_num}题",
                                            reference_answer=reference_answer,
                                            student_answer=student_answer,
                                            max_score=max_score,
                                            grading_criteria=grading_criteria,
                                            api_config=st.session_state.llm_config,
                                            examples=examples
                                        )
                                        
                                        if success:
                                            llm_graded[q_key] = {'score': score, 'comment': comment}
                                            
                                            # 保存到主观题详情
                                            st.session_state.subjective_details.append({
                                                '学号': student_data.get('学号'),
                                                '姓名': student_data.get('姓名'),
                                                '题目': f"{question_text} 第{q_num}题",
                                                'q_key': q_key,
                                                '学生答案': student_answer,
                                                '参考答案': reference_answer,
                                                '评分': score,
                                                '满分': max_score,
                                                '评语': comment
                                            })
                                            
                                            # 更新进度显示
                                            with progress_detail_container:
                                                with current_student_info:
                                                    st.success(f"✅ {question_text} 第{q_num}题 - 评分: {score}/{max_score}")
                                        else:
                                            llm_graded[q_key] = {'score': 0.0, 'comment': f'批改失败: {comment}'}
                                            
                                            # 保存失败记录
                                            st.session_state.subjective_details.append({
                                                '学号': student_data.get('学号'),
                                                '姓名': student_data.get('姓名'),
                                                '题目': f"{question_text} 第{q_num}题",
                                                'q_key': q_key,
                                                '学生答案': student_answer,
                                                '参考答案': reference_answer,
                                                '评分': 0.0,
                                                '满分': max_score,
                                                '评语': f'批改失败: {comment}'
                                            })
                            
                            # 计算总分（包括客观题和主观题）- 在for sec循环外
                            rec = calculate_score(student_data, st.session_state.standard_key, st.session_state.exam_config, llm_graded)
                            processed.append(rec)
                    else:
                        # 只有客观题，快速批改
                        status_text.info("✅ 阶段2/2: 批改客观题...")
                        for idx, student_data in enumerate(students_data):
                            progress_bar.progress(0.5 + (idx + 1) / len(students_data) / 2)
                            rec = calculate_score(student_data, st.session_state.standard_key, st.session_state.exam_config)
                            processed.append(rec)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.session_state.processed_data = processed
                    st.session_state.error_files = errors
                    st.toast(f"处理完成！成功: {len(processed)}, 失败: {len(errors)}", icon="🎉")
                    st.info("请切换到【批改结果】标签页查看详情 👉")
        
        # 数据库状态提示
        st.divider()
        if not st.session_state.db_available:
            st.info("ℹ️ **默认数据库连接不可用**")
            st.caption("默认尝试连接本地 `root` 用户(无密码)。如果您有自定义配置(如密码)，请点击下方按钮手动配置。")
            
            if st.button("🔓 强制显示数据库/历史 Tab"):
                st.session_state.db_available = True
                st.rerun()

# --- Tab 3: 批改结果 ---
with tab3:
    # 异常文件显示 (优先显示)
    if st.session_state.error_files:
        st.error(f"⚠️ 发现 {len(st.session_state.error_files)} 个格式错误文件，请核查：")
        error_list = [{"文件名": k, "错误原因": v} for k, v in st.session_state.error_files.items()]
        st.table(pd.DataFrame(error_list))
        st.divider()

    if st.session_state.processed_data:
        df = pd.DataFrame(st.session_state.processed_data)
        
        # 按学号排序
        if '学号' in df.columns:
            df = df.sort_values('学号').reset_index(drop=True)
            
        # 整理列顺序
        base_cols = ['学号', '姓名', '机号', '总分']
        # 动态获取当前配置的列名
        section_cols = [sec['name'] for sec in st.session_state.exam_config if sec['name'] in df.columns]
        
        q_cols = [c for c in df.columns if c.startswith('Q')]
        final_cols = [c for c in base_cols + section_cols + q_cols if c in df.columns]
        df = df[final_cols]
        
        # 顶部指标卡
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("总人数", len(df))
        m2.metric("平均分", f"{df['总分'].mean():.1f}")
        m3.metric("最高分", df['总分'].max())
        m4.metric("及格率", f"{(len(df[df['总分']>=60])/len(df)*100):.1f}%")
        
        st.divider()
        
        # 统计分析区域
        c_chart, c_data = st.columns([1, 1.5])
        
        with c_chart:
            st.markdown("##### 🧩 班级各大题得分率")
            
            # 计算得分率 logic
            std_key = st.session_state.standard_key
            # 使用 config 初始化
            section_counts = {sec['section_id']: 0 for sec in st.session_state.exam_config}
            
            # 临时构建一个 map: match_keyword -> section_id 方便反查 (如果需要)
            # 但这里 std_key 的 key 已经是 "1-1", "2-1" 这种 id 开头的了
            
            for k in std_key.keys():
                # k: 1-1, 2-1
                sec_id = k.split('-')[0]
                if sec_id in section_counts:
                    section_counts[sec_id] += 1
            
            rates_data = []
            for sec in st.session_state.exam_config:
                sec_id = sec['section_id']
                col_name = sec['name']
                score_val = sec['score']
                
                if col_name in df.columns:
                    avg_score = df[col_name].mean()
                    full_score = section_counts.get(sec_id, 0) * score_val
                    if full_score > 0:
                        rate = avg_score / full_score
                        rates_data.append({'题型': col_name, '得分率': rate, '平均分': avg_score, '满分': full_score})
            
            if rates_data:
                rate_df = pd.DataFrame(rates_data)
                fig_rate = px.bar(
                    rate_df, x='题型', y='得分率', 
                    text=rate_df['得分率'].apply(lambda x: f"{x:.1%}"),
                    color='得分率', range_y=[0, 1.1],
                    color_continuous_scale='Greens'
                )
                fig_rate.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_rate, width='stretch')
            else:
                st.info("无法计算得分率")

            st.markdown("##### 📈 总分分布")
            fig = px.histogram(df, x="总分", nbins=10, color_discrete_sequence=['#4b6cb7'])
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=300)
            st.plotly_chart(fig, width='stretch')
            
        with c_data:
            st.markdown("##### 📋 成绩明细")
            st.dataframe(df, width='stretch', height=700)
    else:
        if not st.session_state.error_files:
            st.empty()
            st.info("👈 请在【答卷上传】页进行阅卷操作")

# --- Tab 4: 主观题详情 ---
with tab4:
    st.header("🤖 主观题批改详情")
    
    if st.session_state.subjective_details:
        st.success(f"共批改 {len(st.session_state.subjective_details)} 个主观题")
        
        # 按学生分组显示
        students = {}
        for detail in st.session_state.subjective_details:
            student_id = detail['学号']
            if student_id not in students:
                students[student_id] = {
                    '姓名': detail['姓名'],
                    '题目': []
                }
            students[student_id]['题目'].append(detail)
        
        # 显示每个学生的主观题批改详情
        for student_id, info in students.items():
            with st.expander(f"👤 {student_id} - {info['姓名']} (共{len(info['题目'])}题)"):
                for idx, detail in enumerate(info['题目'], 1):
                    st.markdown(f"### 题目 {idx}: {detail['题目']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**学生答案**")
                        st.text_area("学生答案", detail['学生答案'], height=100, disabled=True, key=f"ans_{student_id}_{idx}", label_visibility="collapsed")
                    with col2:
                        st.markdown("**参考答案**")
                        st.text_area("参考答案", detail['参考答案'], height=100, disabled=True, key=f"ref_{student_id}_{idx}", label_visibility="collapsed")
                    
                    # 显示评分结果
                    score_col1, score_col2 = st.columns([1, 3])
                    with score_col1:
                        st.metric("评分", f"{detail['评分']}/{detail['满分']}", delta=None)
                    with score_col2:
                        st.info(f"💬 **评语**: {detail['评语']}")
                    
                    st.divider()
    else:
        st.info("⚡ 请先在【答卷上传】页面上传并批改包含主观题的答卷")

# --- Tab 5: 数据库与历史 ---
if tab5 is not None:
    with tab5:
        col_db_conn, col_history = st.columns([1, 4])
        
        with col_db_conn:
            st.subheader("🔌 数据库连接")
            db_user = st.text_input("User", "root")
            db_pass = st.text_input("Password", type="password")
            db_host = st.text_input("Host", "localhost")
            db_port = st.text_input("Port", "3306")
            db_name = st.text_input("DB Name", "grade_system")
            
            st.markdown("---")
            if st.button("💾 保存当前成绩到 DB", type="primary"):
                if not st.session_state.processed_data:
                    st.warning("没有可保存的成绩数据")
                elif not db_pass:
                    st.error("请输入密码 (Password)")
                else:
                    engine = get_db_engine(db_user, db_pass, db_host, db_port, db_name)
                    try:
                        df_save = pd.DataFrame(st.session_state.processed_data)
                        success, msg = save_to_mysql(df_save, exam_name_input, engine)
                        if success: st.success(msg)
                        else: st.error(msg)
                    except Exception as e:
                        st.error(f"操作失败: {e}")

        with col_history:
            st.subheader("🕰️ 历史考情回顾")
            
            # 添加刷新按钮
            col_title, col_refresh = st.columns([0.8, 0.2])
            with col_refresh:
                refresh_clicked = st.button("🔄 刷新", help="重新加载考试列表")
            
            if db_pass:
                try:
                    engine = get_db_engine(db_user, db_pass, db_host, db_port, db_name)
                    
                    # 使用会话状态缓存考试列表，点击刷新时清除缓存
                    if refresh_clicked or 'exam_list_cache' not in st.session_state:
                        exams_df = pd.read_sql("SELECT DISTINCT exam_name FROM exam_records", engine)
                        st.session_state.exam_list_cache = exams_df
                        if refresh_clicked:
                            st.toast("✅ 考试列表已刷新！", icon="🔄")
                    else:
                        exams_df = st.session_state.exam_list_cache
                    
                    if not exams_df.empty:
                        exam_list = exams_df['exam_name'].tolist()
                        selected_exam = st.selectbox("选择考试场次:", exam_list)
                        
                        if selected_exam:
                            # 展示数据
                            hist_df = pd.read_sql(
                                text("SELECT student_id, student_name, total_score, details_json, created_at FROM exam_records WHERE exam_name=:name"), 
                                engine, 
                                params={"name": selected_exam}
                            )
                            
                            # 解析 details_json 提取分项得分
                            if not hist_df.empty and 'details_json' in hist_df.columns:
                                try:
                                    # json 解析
                                    json_data = hist_df['details_json'].apply(lambda x: json.loads(x) if x else {})
                                    details_df = pd.DataFrame(json_data.tolist())
                                    # 筛选得分列
                                    score_cols = [c for c in details_df.columns if '得分' in c]
                                    if score_cols:
                                        # 合并
                                        hist_df = pd.concat([hist_df.drop(columns=['details_json']), details_df[score_cols]], axis=1)
                                    else:
                                        hist_df = hist_df.drop(columns=['details_json'])
                                except Exception as e:
                                    st.warning(f"解析详情失败: {e}")
                            
                            st.dataframe(hist_df, width='stretch')
                            
                            # 删除功能区
                            with st.expander("🗑️ 危险区域: 删除该场考试记录"):
                                st.warning(f"确定要删除【{selected_exam}】的所有记录吗？此操作不可恢复！")
                                if st.button("确认删除", type="secondary"):
                                    success, msg = delete_exam_record(selected_exam, engine)
                                    if success:
                                        st.success(msg)
                                        # 清除缓存并刷新
                                        if 'exam_list_cache' in st.session_state:
                                            del st.session_state.exam_list_cache
                                        st.experimental_rerun()
                                    else:
                                        st.error(msg)
                    else:
                        st.info("数据库中暂无历史记录")
                except Exception as e:
                    st.warning("数据库连接未就绪或表结构不存在")