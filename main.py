import os
import re
import pandas as pd

# ================= 配置区域 =================
# 这里模拟了一份标准答案，实际使用时请替换为真实答案
STANDARD_ANSWERS = {
    # 一、单选题 (15题)
    '1-1': 'A', '1-2': 'B', '1-3': 'C', '1-4': 'D', '1-5': 'A',
    '1-6': 'B', '1-7': 'C', '1-8': 'D', '1-9': 'A', '1-10': 'B',
    '1-11': 'C', '1-12': 'D', '1-13': 'A', '1-14': 'B', '1-15': 'C',
    # 二、判断题 (5题)
    '2-1': 'T', '2-2': 'F', '2-3': 'T', '2-4': 'F', '2-5': 'T',
    # 三、选择填空 (8题)
    '3-1': 'A', '3-2': 'B', '3-3': 'C', '3-4': 'D', 
    '3-5': 'A', '3-6': 'B', '3-7': 'C', '3-8': 'D',
    # 四、综合查询 (6题)
    '4-1': 'SELECT', '4-2': 'FROM', '4-3': 'WHERE', 
    '4-4': 'GROUP BY', '4-5': 'HAVING', '4-6': 'ORDER BY'
}

# 各部分分值配置
SCORES_CONFIG = {
    '1': 2,  # 单选题每题分值
    '2': 2,  # 判断题每题分值
    '3': 3,  # 填空题每题分值
    '4': 6   # 综合题每题分值
}

def parse_answer_file(file_path):
    """
    解析单个学生答题卡文件
    返回: (status, data/error_msg)
    status: True(成功), False(格式错误)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
            content = '\n'.join(lines)
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f: # 尝试GBK编码
                lines = [line.strip() for line in f.readlines()]
                content = '\n'.join(lines)
        except Exception as e:
            print(e)
            return False, "文件编码无法识别"

    student_data = {}
    
    # 1. 提取头部信息 (学号、姓名、机号)
    # 正则兼容中文冒号和英文冒号
    header_pattern = re.compile(r"学号[：:]\s*(.*?)\s+姓名[：:]\s*(.*?)\s+机号[：:]\s*(.*)")
    
    # 通常头部在第一行，但也可能因为空行在第二行，这里搜索前3行
    header_match = None
    for i in range(min(3, len(lines))):
        match = header_pattern.search(lines[i])
        if match:
            header_match = match
            break
            
    if not header_match:
        return False, "头部信息（学号/姓名/机号）缺失或格式不正确"
        
    student_data['学号'] = header_match.group(1).strip()
    student_data['姓名'] = header_match.group(2).strip()
    student_data['机号'] = header_match.group(3).strip()

    # 2. 定义各题型的正则提取逻辑
    # 逻辑：找到特定大题标题后，提取其后的 "数字.答案" 格式
    
    # 大题区域标记 (部分关键字)
    sections = [
        ('1', '一、单项选择题', 15),
        ('2', '二、判断题', 5),
        ('3', '三、选择填空题', 8),
        ('4', '四、综合查询题', 6)
    ]

    current_section_idx = -1
    processed_questions = 0
    
    # 用于定位当前在哪个大题区域
    section_ranges = {} 
    
    # 简单切分内容，利用大题标题作为分隔符
    # 注意：这需要学生没有删除题目的大标题
    full_text = content
    
    last_pos = 0
    for i, (sec_code, sec_title, q_count) in enumerate(sections):
        start_idx = full_text.find(sec_title)
        if start_idx == -1:
            return False, f"缺少大题标题：{sec_title}"
        
        # 记录当前部分的开始位置，结束位置是下一个标题的开始或文本末尾
        if i < len(sections) - 1:
            next_title = sections[i+1][1]
            end_idx = full_text.find(next_title)
            if end_idx == -1: return False, f"缺少大题标题：{next_title}"
        else:
            end_idx = len(full_text)
            
        section_text = full_text[start_idx:end_idx]
        
        # 提取该区域内的所有 "数字. 答案"
        # 正则含义：匹配行首或空白后的数字，加点，捕获后面的非空白字符作为答案
        # 注意：学生可能不换行，也可能换行，这里用宽容模式
        # 针对每一行进行匹配更安全
        
        extracted_count = 0
        
        # 遍历该范围内的行进行提取
        lines_in_section = section_text.split('\n')
        for line in lines_in_section:
            # 匹配 "1. A" 或 "1.A" 或 "1. answer"
            # 忽略大小写，稍后统一处理
            matches = re.findall(r'(\d+)\.\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)?', line)
            
            for q_num, ans in matches:
                key = f"{sec_code}-{q_num}"
                # 如果答案为空（学生没填），设为空字符串
                ans = ans.strip().upper() if ans else ""
                student_data[key] = ans
                extracted_count += 1
        
        # 简单的完整性校验：提取到的题目数量是否至少覆盖了题目要求？
        # (考虑到可能存在多余的数字匹配，这里不做严格的数量相等校验，只做存在性校验)
        pass

    return True, student_data

def grade_process(folder_path):
    valid_results = []
    error_files = []
    
    # 1. 遍历文件
    print(f"正在扫描文件夹: {folder_path} ...")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                status, data = parse_answer_file(file_path)
                
                if status:
                    valid_results.append(data)
                else:
                    error_files.append((file, data))

    # 2. 阅卷核心逻辑
    graded_data_list = []
    
    for student in valid_results:
        # 基础信息
        record = {
            '学号': student['学号'], 
            '姓名': student['姓名'], 
            '机号': student['机号']
        }
        total_score = 0
        
        # 遍历标准答案进行比对
        for q_key, std_ans in STANDARD_ANSWERS.items():
            # 获取题目所属大题类型 (例如 '1-1' -> '1')
            section_type = q_key.split('-')[0]
            score_per_q = SCORES_CONFIG.get(section_type, 0)
            
            student_ans = student.get(q_key, '')
            
            # 判分：完全匹配得分，否则0分
            if student_ans == std_ans:
                score = score_per_q
            else:
                score = 0
            
            # 记录该题得分
            record[f'Q{q_key}'] = score
            total_score += score
            
        record['总分'] = total_score
        graded_data_list.append(record)

    # 3. 转换为DataFrame
    if graded_data_list:
        df = pd.DataFrame(graded_data_list)
        
        # 调整列顺序：学号姓名在前，总分在后
        cols = ['学号', '姓名', '机号'] + \
            [c for c in df.columns if c.startswith('Q')] + \
            ['总分']
        df = df[cols]
        
        # 4. 导出Excel
        output_file = '成绩汇总表.xlsx'
        df.to_excel(output_file, index=False)
        
        # 5. 统计与反馈
        print("-" * 30)
        print("阅卷完成！")
        print(f"成功处理文件数: {len(valid_results)}")
        print(f"格式错误文件数: {len(error_files)}")
        print(f"平均分: {df['总分'].mean():.2f}")
        print(f"最高分: {df['总分'].max()}")
        print("-" * 30)
        
        if error_files:
            print("以下文件需人工检查（格式不一致）：")
            for fname, reason in error_files:
                print(f" - {fname}: {reason}")
    else:
        print("未提取到任何有效数据，请检查文件夹路径或文件格式。")

if __name__ == "__main__":
    # 请修改此处为你存放txt文件的文件夹路径
    target_folder = r'./exam_papers' 
    
    # 检查路径是否存在
    if not os.path.exists(target_folder):
        # 如果没有文件夹，创建一个示例以便测试
        os.makedirs(target_folder, exist_ok=True)
        print(f"文件夹 {target_folder} 不存在，已自动创建。请放入txt文件后重试。")
    else:
        grade_process(target_folder)