import streamlit as st
import pandas as pd
import re
import io
import json
import plotly.express as px
from sqlalchemy import create_engine, text

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
    /* 全局字体 */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    /* 标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #4b6cb7, #182848);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    /* 卡片容器样式 */
    .css-1r6slb0 {
        border-radius: 12px;
        padding: 20px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    /* 按钮样式 */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    /* 指标卡片 */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ================= 全局配置 =================
# ================= 全局配置 =================
# 默认配置移入 session_state 初始化中

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
        
        # 提取该区域内的所有 "数字. 答案"
        lines_in_section = section_text.split('\n')
        for line in lines_in_section:
            # 匹配 "1. A" 或 "1.A" 
            matches = re.findall(r'(\d+)\.\s*([a-zA-Z0-9_\u4e00-\u9fa5]+)?', line)
            for q_num, ans in matches:
                # 这里的 section['id'] 建议使用 1, 2, 3 这样的唯一标识
                # 为了兼容旧逻辑，我们假设 config 中有一列 "section_id"
                sec_id = section.get('section_id', str(i+1)) 
                key = f"{sec_id}-{q_num}"
                ans = ans.strip().upper() if ans else ""
                student_data[key] = ans

    return True, student_data

def calculate_score(student_data, standard_key, exam_config):
    """
    计算分数，包括各大题得分
    **修正：大小写无关**
    """
    record = {
        '学号': student_data['学号'], 
        '姓名': student_data['姓名'], 
        '机号': student_data['机号']
    }
    
    # 转换为查找字典: section_id -> score
    score_map = {sec.get('section_id', str(i+1)): sec['score'] for i, sec in enumerate(exam_config)}
    
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
        
        student_ans = student_data.get(q_key, '')
        
        # 判分：大小写无关比较
        s_ans_norm = str(student_ans).strip().upper()
        t_ans_norm = str(std_ans).strip().upper()
        
        if s_ans_norm == t_ans_norm:
            score = score_per_q
        else:
            score = 0
        
        # 记录单题得分
        record[f'Q{q_key}'] = score
        
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

# ================= 数据库工具函数 =================

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
st.markdown('<div class="main-title">🎓 作业自动批改系统 </div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">自动化 • 高效 • 数据化</div>', unsafe_allow_html=True)

# Session State 初始化
if 'processed_data' not in st.session_state: st.session_state.processed_data = []
if 'error_files' not in st.session_state: st.session_state.error_files = {}
if 'standard_key' not in st.session_state: st.session_state.standard_key = None
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

# 默认考试配置 Config Structure: section_id, match_keyword, name, score, num_questions
DEFAULT_CONFIG = [
    {'section_id': '1', 'match_keyword': '一、单项选择题', 'name': '单选得分', 'score': 2.0, 'num_questions': 10},
    {'section_id': '2', 'match_keyword': '二、判断题', 'name': '判断得分', 'score': 2.0, 'num_questions': 10},
    {'section_id': '3', 'match_keyword': '三、选择填空题', 'name': '填空得分', 'score': 3.0, 'num_questions': 5},
    {'section_id': '4', 'match_keyword': '四、综合查询题', 'name': '综合得分', 'score': 6.0, 'num_questions': 3}
]
if 'exam_config' not in st.session_state:
    st.session_state.exam_config = DEFAULT_CONFIG

# 初始化 DataFrame 状态以保持 Index 稳定性
if 'exam_config_df' not in st.session_state:
    st.session_state.exam_config_df = pd.DataFrame(st.session_state.exam_config)

# 初始化行数追踪，用于判断是新增行还是编辑现有行
if 'last_row_count' not in st.session_state:
    st.session_state.last_row_count = len(st.session_state.exam_config_df)

# 布局 Tabs
tab1, tab2, tab3 = st.tabs(["⚙️ 设置 & 上传", "📊 批改结果", "💾 数据库 & 历史"])

# --- Tab 1: 设置与上传 ---
with tab1:
    col_cfg, col_up = st.columns([1.5, 2])
    
    with col_cfg:
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
                "num_questions": st.column_config.NumberColumn("题目数量", min_value=1, max_value=100, step=1, help="该题型包含的题目数量")
            },
            num_rows="dynamic",
            width='stretch',
            key="config_editor_widget"
        )
        
        # 添加"应用配置"按钮，只有点击后才更新配置
        if st.button("✅ 应用配置变更", key="apply_config_btn", help="点击保存对题型配置的修改"):
            st.session_state.exam_config_df = edited_df
            st.session_state.exam_config = edited_df.to_dict('records')
            st.session_state.last_row_count = len(edited_df)
            st.success("配置已更新！")
            st.rerun()
        
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
        
    with col_up:
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
                processed = []
                errors = {}
                progress_bar = st.progress(0)
                
                for idx, file in enumerate(student_files):
                    progress_bar.progress((idx + 1) / len(student_files))
                    try: 
                        content = file.getvalue().decode("utf-8")
                    except: 
                        content = file.getvalue().decode("gbk", errors='ignore')
                        
                    # 传递配置
                    status, res = parse_text_content(content, st.session_state.exam_config)
                    if status:
                        # 传递配置
                        rec = calculate_score(res, st.session_state.standard_key, st.session_state.exam_config)
                        processed.append(rec)
                    else:
                        errors[file.name] = res
                
                st.session_state.processed_data = processed
                st.session_state.error_files = errors
                st.toast(f"处理完成！成功: {len(processed)}, 失败: {len(errors)}", icon="🎉")
                st.info("请切换到【批改结果】标签页查看详情 👉")

# --- Tab 2: 批改结果 ---
with tab2:
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
                st.plotly_chart(fig_rate, use_container_width=True)
            else:
                st.info("无法计算得分率")

            st.markdown("##### 📈 总分分布")
            fig = px.histogram(df, x="总分", nbins=10, color_discrete_sequence=['#4b6cb7'])
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_data:
            st.markdown("##### 📋 成绩明细")
            st.dataframe(df, width='stretch', height=700)
    else:
        if not st.session_state.error_files:
            st.empty()
            st.info("👈 请在【设置 & 上传】页进行阅卷操作")

# --- Tab 3: 数据库与历史 ---
with tab3:
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
        if db_pass:
            try:
                engine = get_db_engine(db_user, db_pass, db_host, db_port, db_name)
                exams_df = pd.read_sql("SELECT DISTINCT exam_name FROM exam_records", engine)
                
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
                                    st.experimental_rerun()
                                else:
                                    st.error(msg)
                else:
                    st.info("数据库中暂无历史记录")
            except Exception as e:
                st.warning("数据库连接未就绪或表结构不存在")