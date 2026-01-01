<template>
  <div class="settings-view">
    <el-tabs type="border-card">

      <!-- Exam Config (Merged) -->
      <el-tab-pane label="答题卡配置">
        <template #label>
           <span class="custom-tabs-label">
             <el-icon><Edit /></el-icon>
             <span> 答题卡配置</span>
           </span>
        </template>
        
        <el-row :gutter="20">
            <!-- Left Column: Settings -->
            <el-col :span="14">
                <el-form label-width="120px">
                    <el-form-item label="考试名称">
                      <el-input v-model="examStore.config.exam_name" placeholder="例如: 2025_期末考试" />
                    </el-form-item>
                </el-form>

                <el-divider content-position="left">题型配置</el-divider>

                <el-table :data="examStore.config.sections" border style="width: 100%">
                    <el-table-column prop="section_id" label="ID" width="60" />
                    <el-table-column label="识别关键字" min-width="150">
                      <template #default="scope">
                        <el-input v-model="scope.row.match_keyword" />
                      </template>
                    </el-table-column>
                    <el-table-column label="报表列名" min-width="100">
                      <template #default="scope">
                        <el-input v-model="scope.row.name" />
                      </template>
                    </el-table-column>
                    <el-table-column label="每题分值" width="100">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.score" :min="0" :step="0.5" controls-position="right" style="width: 100%" />
                      </template>
                    </el-table-column>
                    <el-table-column label="数量" width="100">
                      <template #default="scope">
                        <el-input-number v-model="scope.row.num_questions" :min="1" controls-position="right" style="width: 100%" />
                      </template>
                    </el-table-column>
                    <el-table-column label="题型" width="110">
                      <template #default="scope">
                        <el-select v-model="scope.row.question_type">
                          <el-option label="客观题" value="客观题" />
                          <el-option label="主观题" value="主观题" />
                        </el-select>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="60" align="center">
                      <template #default="scope">
                        <el-button type="danger" icon="Delete" circle size="small" @click="removeSection(scope.$index)" />
                      </template>
                    </el-table-column>
                </el-table>

                <div style="margin-top: 10px; margin-bottom: 20px;">
                    <el-button @click="addSection" icon="Plus">添加题型</el-button>
                </div>

                <el-form-item>
                    <el-button type="primary" @click="saveSettings">保存考试配置</el-button>
                </el-form-item>
                
                <div class="mt-20" v-if="hasSubjective">
                   <el-alert title="检测到主观题：请在「LLM 配置」页面配置 LLM (大语言模型) 以启用智能批改" type="info" show-icon :closable="false" />
                </div>
            </el-col>

            <!-- Right Column: Template Preview -->
            <el-col :span="10">
               <el-card>
                  <template #header>
                     <div class="card-header">
                        <span>答题卡模板预览</span>
                        <el-button size="small" @click="downloadTemplate">下载模板</el-button>
                     </div>
                  </template>
                  <pre class="template-preview">{{ templatePreview }}</pre>
               </el-card>
            </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Standard Answer Settings -->
      <el-tab-pane label="标准答案配置">
         <template #label>
           <span class="custom-tabs-label">
             <el-icon><List /></el-icon>
             <span> 标准答案</span>
           </span>
         </template>

         <el-row :gutter="20">
            <el-col :span="12">
               <el-card shadow="hover">
                  <template #header>上传标准答案文件</template>
                  <el-upload
                    class="upload-demo"
                    drag
                    action="#"
                    :auto-upload="false"
                    :limit="1"
                    :on-change="handleStandardChange"
                    accept=".txt"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      Drop file here or <em>click to upload</em>
                    </div>
                  </el-upload>
               </el-card>
            </el-col>
            <el-col :span="12">
                <el-card shadow="hover">
                   <template #header>
                      <div class="card-header">
                        <span>当前标准答案预览</span>
                        <div>
                            <el-button v-if="standardKeyCount > 0" type="primary" size="small" @click="saveStandardKeyManual">保存修改</el-button>
                            <el-tag v-if="standardKeyCount > 0" type="success" style="margin-left: 10px">{{ standardKeyCount }} 题已解析</el-tag>
                            <el-tag v-else type="info">未配置</el-tag>
                        </div>
                      </div>
                   </template>
                   <el-input 
                     v-model="editableStandardKeyJson" 
                     type="textarea" 
                     :rows="15" 
                     placeholder="上传后此处显示解析结果 (JSON格式)，支持手动修改"
                   />
                </el-card>
            </el-col>
         </el-row>
      </el-tab-pane>

      <!-- LLM Settings -->
      <el-tab-pane label="LLM 配置">
        <template #label>
           <span class="custom-tabs-label">
             <el-icon><Cpu /></el-icon>
             <span> LLM 配置</span>
           </span>
        </template>

        <el-form label-width="120px" style="max-width: 600px">
          <el-alert title="配置大语言模型以启用主观题智能批改" type="info" show-icon :closable="false" class="mb-20" />

          <el-form-item label="供应商">
             <el-select v-model="selectedProvider" @change="handleProviderChange">
                <el-option
                   v-for="p in providers"
                   :key="p.value"
                   :label="p.label"
                   :value="p.value"
                />
             </el-select>
          </el-form-item>

          <el-form-item label="Base URL">
            <el-input v-model="llmConfig.base_url" placeholder="https://api.deepseek.com" />
          </el-form-item>
          <el-form-item label="API Key">
            <el-input v-model="llmConfig.api_key" type="password" show-password placeholder="sk-..." />
          </el-form-item>
          <el-form-item label="模型名称">
            <el-input v-model="llmConfig.model" placeholder="deepseek-chat" />
          </el-form-item>
          <el-form-item label="Temperature">
             <el-slider v-model="llmConfig.temperature" :min="0" :max="1" :step="0.1" show-input />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveLLM">保存 LLM 配置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- DB Settings -->
      <el-tab-pane label="数据库配置">
         <template #label>
           <span class="custom-tabs-label">
             <el-icon><Coin /></el-icon>
             <span> 数据库配置</span>
           </span>
        </template>

        <el-form label-width="120px" style="max-width: 600px">
          <el-alert title="配置 MySQL 数据库以启用历史成绩归档" type="info" show-icon :closable="false" class="mb-20" />

          <el-form-item label="Host">
            <el-input v-model="dbConfig.host" placeholder="localhost" />
          </el-form-item>
          <el-form-item label="Port">
            <el-input-number v-model="dbConfig.port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item label="User">
            <el-input v-model="dbConfig.user" placeholder="root" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="dbConfig.password" type="password" show-password />
          </el-form-item>
          <el-form-item label="DB Name">
            <el-input v-model="dbConfig.db_name" placeholder="grade_system" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveDB">保存并测试连接</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Template/Parser Settings -->
      <el-tab-pane label="匹配规则配置">
         <template #label>
           <span class="custom-tabs-label">
             <el-icon><Document /></el-icon>
             <span> 匹配规则</span>
           </span>
        </template>

        <el-form label-width="120px" label-position="top" style="max-width: 800px">
          <el-alert title="配置解析答题卡时的正则表达式 (高级)" type="warning" show-icon :closable="false" class="mb-20" />

          <el-form-item label="头部提取正则 (Header Regex)">
             <el-input v-model="parserConfig.header_regex" type="textarea" :rows="2" />
             <div class="help-text">需包含3个捕获组，分别对应：学号、姓名、机号</div>
          </el-form-item>

          <el-form-item label="题目提取正则 (Question Regex)">
             <el-input v-model="parserConfig.question_regex" type="textarea" :rows="2" />
             <div class="help-text">需包含2个捕获组：题号 (数字) 和 答案</div>
          </el-form-item>

          <el-form-item>
             <el-button type="primary" @click="saveParser">保存解析规则</el-button>
          </el-form-item>
       </el-form>
      </el-tab-pane>


    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useExamStore } from '../stores/examStore';
import { Cpu, Coin, Document, Edit, Plus, Delete, List, UploadFilled } from '@element-plus/icons-vue';

const examStore = useExamStore();
const API_BASE = 'http://localhost:8000/api/settings';

// Standard Answer Logic
const editableStandardKeyJson = ref('');

const handleStandardChange = async (file) => {
    const success = await examStore.uploadStandardAnswer(file.raw);
    if (success) ElMessage.success('标准答案解析成功');
    else ElMessage.error('标准答案解析失败');
};

const filterStandardKey = (keyObj) => {
    if (!keyObj) return {};
    const filtered = { ...keyObj };
    delete filtered['学号'];
    delete filtered['姓名'];
    delete filtered['机号'];
    return filtered;
};

watch(() => examStore.standardKey, (newVal) => {
    if (newVal) {
        editableStandardKeyJson.value = JSON.stringify(filterStandardKey(newVal), null, 4);
    } else {
        editableStandardKeyJson.value = '';
    }
}, { immediate: true });

const saveStandardKeyManual = () => {
    try {
        const parsed = JSON.parse(editableStandardKeyJson.value);
        // Validate?
        examStore.standardKey = parsed;
        ElMessage.success('标准答案已手动更新');
    } catch (e) {
        ElMessage.error('JSON 格式错误，无法保存');
    }
};

const standardKeyCount = computed(() => {
    // Count only questions, not empty base fields if they exist?
    // actually base fields are removed in our filtered view, but might exist in store.
    // Let's count filtered keys.
    if (!examStore.standardKey) return 0;
    const keys = Object.keys(examStore.standardKey);
    const exclude = ['学号', '姓名', '机号'];
    return keys.filter(k => !exclude.includes(k)).length;
});


// Config State
const llmConfig = ref({
    base_url: '', api_key: '', model: '', temperature: 0.3
});
const dbConfig = ref({
    host: 'localhost', port: 3306, user: 'root', password: '', db_name: 'grade_system'
});
const parserConfig = ref({
    header_regex: '', question_regex: ''
});

// LLM Providers
const providers = [
    { label: 'DeepSeek (推荐)', value: 'deepseek', url: 'https://api.deepseek.com', defaultModel: 'deepseek-chat' },
    { label: 'OpenAI', value: 'openai', url: 'https://api.openai.com/v1', defaultModel: 'gpt-4-turbo' },
    { label: 'Moonshot (Kimi)', value: 'moonshot', url: 'https://api.moonshot.cn/v1', defaultModel: 'moonshot-v1-8k' },
    { label: 'Gemini (OpenAI Compatible)', value: 'gemini', url: 'https://generativelanguage.googleapis.com/v1beta/openai/', defaultModel: 'gemini-1.5-flash' },
    { label: 'Custom / Other', value: 'custom', url: '', defaultModel: '' }
];
const selectedProvider = ref('custom');

// Watch provider change to update URL
const handleProviderChange = (val) => {
    const p = providers.find(p => p.value === val);
    if (p && p.value !== 'custom') {
        llmConfig.value.base_url = p.url;
        if (p.defaultModel && !llmConfig.value.model) {
             llmConfig.value.model = p.defaultModel;
        }
    }
};

// Merged Exam Config Logic
const hasSubjective = computed(() => {
    return examStore.config.sections.some(s => s.question_type === '主观题');
});

const addSection = () => {
  const ids = examStore.config.sections.map(s => Number(s.section_id) || 0);
  const maxId = ids.length > 0 ? Math.max(...ids) : 0;
  
  examStore.config.sections.push({
    section_id: String(maxId + 1),
    match_keyword: '新题型',
    name: '得分',
    score: 5,
    num_questions: 1,
    question_type: '客观题'
  });
};

const removeSection = (index) => {
  examStore.config.sections.splice(index, 1);
};

const saveSettings = async () => {
  const success = await examStore.saveConfig(examStore.config);
  if (success) {
    ElMessage.success('配置已保存');
  } else {
    ElMessage.error('保存失败');
  }
};

// Load Configs
const loadConfigs = async () => {
    try {
        const [llmRes, dbRes, parserRes] = await Promise.all([
            axios.get(`${API_BASE}/llm`),
            axios.get(`${API_BASE}/db`),
            axios.get(`${API_BASE}/parser`)
        ]);
        llmConfig.value = llmRes.data;
        
        // Auto-detect provider
        const matched = providers.find(p => p.url === llmConfig.value.base_url);
        selectedProvider.value = matched ? matched.value : 'custom';

        dbConfig.value = dbRes.data;
        parserConfig.value = parserRes.data;
    } catch (err) {
        ElMessage.error('加载系统配置失败'); 
    }

    // Ensure exam config is loaded for template preview AND now for the Exam Config tab
    await examStore.fetchConfig();
};

onMounted(() => {
    loadConfigs();
});

// Save Actions (System)
const saveLLM = async () => {
    try {
        await axios.post(`${API_BASE}/llm`, llmConfig.value);
        ElMessage.success('LLM 配置已保存');
    } catch (err) {
        ElMessage.error('保存失败');
    }
};

const saveDB = async () => {
    try {
        await axios.post(`${API_BASE}/db`, dbConfig.value);
        ElMessage.success('数据库配置已保存，已尝试重连');
    } catch (err) {
        ElMessage.error('保存失败');
    }
};

const saveParser = async () => {
    try {
        await axios.post(`${API_BASE}/parser`, parserConfig.value);
        ElMessage.success('解析规则已保存');
    } catch (err) {
        ElMessage.error('保存失败');
    }
};

// Template Logic
const templatePreview = computed(() => {
    const config = examStore.config.sections;
    if (!config) return 'Loading...';

    // Generate a sample header based on regex is hard, so we use a standard one
    let text = "学号：2023001       姓名：张三         机号：01\n\n";

    config.forEach(item => {
        text += `${item.match_keyword}（每题${item.score}分，共${item.num_questions}题）\n`;
        for (let i = 1; i <= item.num_questions; i++) {
            text += `${i}. \n`;
        }
        text += "\n";
    });

    return text;
});

const downloadTemplate = () => {
    const blob = new Blob([templatePreview.value], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '答题卡模板.txt';
    a.click();
    window.URL.revokeObjectURL(url);
};

</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.custom-tabs-label .el-icon { vertical-align: middle; }
.custom-tabs-label span { vertical-align: middle; margin-left: 4px; }
.help-text { font-size: 12px; color: #999; line-height: 1.5; margin-top: 5px; }
.template-preview {
    background: #f4f4f5;
    padding: 15px;
    border-radius: 4px;
    font-family: monospace;
    white-space: pre-wrap;
    max-height: 500px;
    overflow-y: auto;
    font-size: 14px;
    border: 1px solid #dcdfe6;
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
