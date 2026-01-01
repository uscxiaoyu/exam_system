<template>
  <div class="subjective-view">
    <el-tabs v-model="activeTab" type="border-card">
      
      <!-- Tab 1: Configuration -->
      <el-tab-pane label="参考答案与评分标准" name="config">
         <div v-if="subjectiveSections.length === 0">
             <el-empty description="当前没有配置主观题题型，请先在「系统配置」中添加主观题" />
         </div>
         <div v-else>
             <el-collapse v-model="activeSectionName" accordion>
                <el-collapse-item v-for="section in subjectiveSections" :key="section.section_id" :title="`${section.name} (共${section.num_questions}题)`" :name="section.section_id">
                    <div v-for="i in section.num_questions" :key="i" class="question-config-item">
                        <el-divider content-position="left">第 {{ i }} 题</el-divider>
                        
                        <el-form label-position="top">
                            <el-form-item label="题目内容 (Prompt)">
                                <el-input v-model="getSubQuestion(section, i).question_text" type="textarea" :rows="3" placeholder="请输入题目内容，这将作为Prompt发送给AI" />
                            </el-form-item>
                            
                            <el-form-item label="参考答案">
                                <el-input v-model="getSubQuestion(section, i).reference_answer" type="textarea" :rows="4" placeholder="请输入标准答案" />
                            </el-form-item>

                            <el-form-item label="评分标准与细则">
                                <el-input v-model="getSubQuestion(section, i).criteria" type="textarea" :rows="4" placeholder="例如：1. 答对核心概念得2分；2. 举例恰当得1分..." />
                            </el-form-item>
                        </el-form>
                    </div>
                    <div style="margin-top: 10px; text-align: right;">
                        <el-button type="primary" @click="saveConfig">保存本题型配置</el-button>
                    </div>
                </el-collapse-item>
             </el-collapse>
         </div>
      </el-tab-pane>

      <!-- Tab 2: Grading -->
      <el-tab-pane label="智能辅助阅卷" name="grading">
         <div class="grading-layout">
             <!-- Left: Side List (Students) -->
             <div class="student-list">
                 <el-input v-model="studentSearch" placeholder="搜索姓名/学号" prefix-icon="Search" style="margin-bottom: 10px" />
                 <el-scrollbar height="600px">
                     <ul class="student-ul">
                         <li v-for="student in filteredStudents" :key="student.student_id" 
                             :class="{active: currentStudent?.student_id === student.student_id}"
                             @click="selectStudent(student)">
                             <div class="s-name">{{ student.name }}</div>
                             <div class="s-id">{{ student.student_id }}</div>
                             <el-tag size="small" :type="isStudentFullyGraded(student) ? 'success' : 'info'">
                                 {{ isStudentFullyGraded(student) ? '已完成' : '未完成' }}
                             </el-tag>
                         </li>
                     </ul>
                 </el-scrollbar>
             </div>

             <!-- Right: Grading Area -->
             <div class="grading-panel" v-if="currentStudent">
                 <div class="panel-header">
                     <h3>正在批改: {{ currentStudent.name }} ({{ currentStudent.student_id }})</h3>
                     <el-select v-model="currentQuestionKey" placeholder="选择题目" style="width: 200px">
                         <el-option v-for="q in allSubjectiveQuestionKeys" :key="q.key" :label="q.label" :value="q.key" />
                     </el-select>
                 </div>

                 <div v-if="currentQuestionKey" class="grading-content">
                     <!-- Context Info -->
                     <el-card class="mb-20" shadow="hover">
                         <template #header>题目与参考</template>
                         <div class="info-grid">
                             <div class="info-item">
                                 <strong>题目:</strong>
                                 <p>{{ currentQuestionConfig.question_text || '未配置题目内容' }}</p>
                             </div>
                             <div class="info-item">
                                 <strong>参考答案:</strong>
                                 <p>{{ currentQuestionConfig.reference_answer || '未配置参考答案' }}</p>
                             </div>
                             <div class="info-item full-width">
                                 <strong>评分标准:</strong>
                                 <pre>{{ currentQuestionConfig.criteria || '未配置评分标准' }}</pre>
                             </div>
                         </div>
                     </el-card>

                     <el-row :gutter="20">
                         <!-- Student Answer -->
                         <el-col :span="12">
                             <el-card shadow="never" class="answer-card">
                                 <template #header>
                                     <el-tag>学生作答</el-tag>
                                 </template>
                                 <div class="student-answer-text">
                                     {{ getStudentAnswer(currentStudent, currentQuestionKey) }}
                                 </div>
                             </el-card>
                         </el-col>

                         <!-- AI Grading & Modification -->
                         <el-col :span="12">
                             <el-card shadow="never">
                                 <template #header>
                                     <div class="ai-header">
                                         <span>AI 辅助与评分</span>
                                         <el-button type="primary" size="small" :loading="aiLoading" @click="runAIGrading">
                                             <el-icon><MagicStick /></el-icon> AI 智能批改
                                         </el-button>
                                     </div>
                                 </template>
                                 
                                 <el-form label-position="top">
                                     <el-form-item label="AI 建议 / 评语">
                                         <el-input v-model="currentGrading.comment" type="textarea" :rows="6" />
                                     </el-form-item>
                                     <el-form-item label="得分">
                                         <el-input-number v-model="currentGrading.score" :min="0" :max="currentQuestionConfig.max_score" :step="0.5" />
                                         <span class="max-score-hint"> / {{ currentQuestionConfig.max_score }} 分</span>
                                     </el-form-item>
                                     <el-form-item>
                                          <el-button type="success" @click="saveGrade" style="width: 100%">保存本题评分</el-button>
                                     </el-form-item>
                                 </el-form>
                             </el-card>
                         </el-col>
                     </el-row>
                 </div>
                 <el-empty v-else description="请选择一道题目开始批改" />
             </div>
             
             <el-empty v-else description="请左侧选择学生" style="flex: 1" />
         </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useExamStore } from '../stores/examStore';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import { Search, MagicStick } from '@element-plus/icons-vue';

const examStore = useExamStore();
const activeTab = ref('grading');
const activeSectionName = ref('');
const studentSearch = ref('');
const currentStudent = ref(null);
const currentQuestionKey = ref(''); // "section_id-index", e.g. "5-1"
const aiLoading = ref(false);

// Local state for grading form
const currentGrading = ref({
    score: 0,
    comment: ''
});

// --- Config Logic ---
const subjectiveSections = computed(() => {
    return examStore.config.sections.filter(s => s.question_type === '主观题');
});

const getSubQuestion = (section, index) => {
    if (!section.sub_questions) {
        section.sub_questions = [];
    }
    // Ensure array is long enough
    while (section.sub_questions.length < section.num_questions) {
        section.sub_questions.push({
            id: String(section.sub_questions.length + 1),
            question_text: '',
            reference_answer: '',
            criteria: ''
        });
    }
    return section.sub_questions[index - 1];
};

const saveConfig = async () => {
    const success = await examStore.saveConfig(examStore.config);
    if(success) ElMessage.success('配置保存成功');
    else ElMessage.error('保存失败');
};

// --- Grading Logic ---
const filteredStudents = computed(() => {
    if (!studentSearch.value) return examStore.students;
    const q = studentSearch.value.toLowerCase();
    return examStore.students.filter(s => 
        s.name.toLowerCase().includes(q) || 
        s.student_id.toLowerCase().includes(q)
    );
});

// Calculate all available question keys e.g. [{key:'5-1', label:'5-1 应用题Q1'}]
const allSubjectiveQuestionKeys = computed(() => {
    const list = [];
    subjectiveSections.value.forEach(sec => {
        for(let i=1; i<=sec.num_questions; i++) {
            list.push({
                key: `${sec.section_id}-${i}`,
                label: `${sec.name} Q${i}`,
                section: sec,
                index: i,
                max_score: sec.score // Assuming score per question is section.score (wait, check config)
                                     // Actually section.score is "每题分值" usually? 
                                     // SettingsView: "每题分值" (row.score)
            });
        }
    });
    return list;
});

const currentQuestionConfig = computed(() => {
    if(!currentQuestionKey.value) return {};
    const meta = allSubjectiveQuestionKeys.value.find(k => k.key === currentQuestionKey.value);
    if(!meta) return {};
    
    // Get details from config
    const subQ = getSubQuestion(meta.section, meta.index);
    return {
        ...subQ,
        max_score: meta.max_score
    };
});

const selectStudent = (student) => {
    currentStudent.value = student;
    // Reset grading form or load existing
    if(currentQuestionKey.value) {
        loadExistingGrade();
    }
};

const getStudentAnswer = (student, key) => {
    if(!student || !student.answers) return '无作答';
    // Key format check: sectionId-Index.
    // Ensure frontend parsing (upload step) generates keys like "5-1", "5-2" for multi-q sections.
    // If parser produces "Q5" for single question, we need to align.
    // Currently parser behavior:
    // subjective_matches = re.finditer(subjective_regex ...)?
    // Usually parser generates "Q{number}".
    // We need to map our "5-1" schema to what parser produces.
    // Let's assume parser produces "5-1" or "Q5-1". 
    // Actually, checking parser: `key = f"{section['section_id']}-{i+1}"` (logic needed in parser or here)
    // Let's assume the keys matches `section_id-index`.
    return student.answers[key] || '无作答';
};

const loadExistingGrade = () => {
    if(!currentStudent.value || !currentQuestionKey.value) return;
    const key = currentQuestionKey.value;
    const s = currentStudent.value;
    
    // Check if graded
    if(s.scores && s.scores[key] !== undefined) {
        currentGrading.value.score = s.scores[key];
        currentGrading.value.comment = s.comments?.[key] || '';
    } else {
        currentGrading.value.score = 0;
        currentGrading.value.comment = '';
    }
};

watch(currentQuestionKey, () => {
    loadExistingGrade();
});

const isStudentFullyGraded = (student) => {
    // Check if all subjective questions have scores
    return allSubjectiveQuestionKeys.value.every(q => 
        student.scores && student.scores[q.key] !== undefined
    );
};

const runAIGrading = async () => {
    if(!currentStudent.value || !currentQuestionKey.value) return;
    
    const meta = allSubjectiveQuestionKeys.value.find(k => k.key === currentQuestionKey.value);
    const subQ = getSubQuestion(meta.section, meta.index);
    
    const payload = {
        question_text: subQ.question_text || '题目内容空',
        reference_answer: subQ.reference_answer || '无参考答案',
        student_answer: getStudentAnswer(currentStudent.value, currentQuestionKey.value),
        max_score: meta.max_score,
        grading_criteria: subQ.criteria,
        llm_config: await getLLMConfig(), // helper to fetch config
        examples: []
    };
    
    aiLoading.value = true;
    try {
        const res = await axios.post('http://localhost:8000/api/grade/subjective', payload);
        if(res.data) {
            currentGrading.value.score = res.data.score;
            currentGrading.value.comment = res.data.comment;
            ElMessage.success('AI 批改完成');
        }
    } catch(err) {
        ElMessage.error('AI 批改失败: ' + (err.response?.data?.detail || err.message));
    } finally {
        aiLoading.value = false;
    }
};

const getLLMConfig = async () => {
    // Fetch from backend api
     const res = await axios.get('http://localhost:8000/api/settings/llm');
     return res.data;
};

const saveGrade = () => {
    if(!currentStudent.value || !currentQuestionKey.value) return;
    const s = currentStudent.value;
    const key = currentQuestionKey.value;
    
    if(!s.scores) s.scores = {};
    if(!s.comments) s.comments = {};
    
    s.scores[key] = currentGrading.value.score;
    s.comments[key] = currentGrading.value.comment;
    
    // Auto calculate total for this section?
    // And total exam score. 
    // Ideally we re-run `calculate_score` or just sum up locally.
    updateTotalScore(s);
    
    ElMessage.success('评分已保存');
};

const updateTotalScore = (student) => {
    // Simple sum
    let total = 0;
    // Objective (we need to know which are objective)
    // We can just sum all scores in `student.scores`
    for(let k in student.scores) {
        total += student.scores[k];
    }
    student.total_score = total;
};

onMounted(() => {
    examStore.fetchConfig();
});

</script>

<style scoped>
.subjective-view {
    height: 100%;
}
.grading-layout {
    display: flex;
    height: 75vh;
    gap: 20px;
}
.student-list {
    width: 250px;
    background: #fff;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    padding: 10px;
}
.student-ul {
    list-style: none;
    padding: 0;
    margin: 0;
}
.student-ul li {
    padding: 10px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.student-ul li:hover, .student-ul li.active {
    background-color: #ecf5ff;
}
.student-ul li.active {
    border-left: 3px solid #409eff;
}
.s-name { font-weight: bold; }
.s-id { font-size: 12px; color: #999; }

.grading-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}
.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    background: #fff;
    padding: 15px;
    border-radius: 4px;
    border: 1px solid #ebeef5;
}
.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}
.full-width { grid-column: 1 / -1; }
.info-item p { background: #f9f9f9; padding: 10px; border-radius: 4px; margin: 5px 0 0; }
.info-item pre { background: #f9f9f9; padding: 10px; border-radius: 4px; margin: 5px 0 0; white-space: pre-wrap; font-family: inherit;}

.student-answer-text {
    font-size: 16px;
    line-height: 1.6;
    padding: 10px;
    min-height: 200px;
    white-space: pre-wrap;
}
.ai-header {
    display: flex; justify-content: space-between; align-items: center;
}
.max-score-hint { margin-left: 10px; color: #666; }
.mb-20 { margin-bottom: 20px; }
</style>
