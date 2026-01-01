import re
from typing import Dict, List, Tuple, Any

def parse_text_content(content: str, exam_config: List[Dict]) -> Tuple[bool, Any]:
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


def calculate_score(student_data: Dict, standard_key: Dict, exam_config: List[Dict], llm_graded_data: Dict = None) -> Dict:
    """
    计算分数，包括各大题得分
    llm_graded_data: 已经通过LLM批改的主观题数据 (可选)
    """
    record = {
        '学号': student_data.get('学号', ''),
        '姓名': student_data.get('姓名', ''),
        '机号': student_data.get('机号', '')
    }

    # 转换为查找字典: section_id -> score
    score_map = {sec.get('section_id', str(i+1)): sec['score'] for i, sec in enumerate(exam_config)}
    # 题型映射
    type_map = {sec.get('section_id', str(i+1)): sec.get('question_type', '客观题') for i, sec in enumerate(exam_config)}

    # 初始化各大题得分为0
    section_scores = {sec.get('section_id', str(i+1)): 0 for i, sec in enumerate(exam_config)}
    total_score = 0

    # 遍历标准答案进行比对
    # 注意：这里需要以标准答案为准，同时也需要处理主观题（可能不在standard_key中如果没上传的话，但通常应该在）
    # 如果standard_key是从文件解析来的，那么所有题目都应该在里面

    for q_key, std_ans in standard_key.items():
        # 排除非题目字段
        if q_key in ['学号', '姓名', '机号']:
            continue

        # q_key 格式如 '1-1', '2-1'
        if '-' not in q_key:
            continue

        section_id = q_key.split('-')[0]
        score_per_q = score_map.get(section_id, 0)
        question_type = type_map.get(section_id, '客观题')

        student_ans = student_data.get(q_key, '')
        score = 0
        comment = ""

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
                score = 0.0
                record[f'Q{q_key}'] = 0.0
                record[f'Q{q_key}_comment'] = '⏳ 待批改'

        # 累加大题得分
        if section_id in section_scores:
            section_scores[section_id] += score
            total_score += score

    # 将大题得分写入 record，使用配置中的列名
    for i, sec in enumerate(exam_config):
        sec_id = sec.get('section_id', str(i+1))
        col_name = sec['name']
        record[col_name] = section_scores.get(sec_id, 0)

    record['总分'] = total_score
    return record
