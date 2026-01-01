<template>
  <div class="settings-view">
    <el-tabs type="border-card">

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
      <el-tab-pane label="答题卡模板配置">
         <template #label>
           <span class="custom-tabs-label">
             <el-icon><Document /></el-icon>
             <span> 模板配置</span>
           </span>
        </template>

        <el-row :gutter="20">
           <el-col :span="14">
               <el-form label-width="120px" label-position="top">
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
           </el-col>
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
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useExamStore } from '../stores/examStore';

const examStore = useExamStore();
const API_BASE = 'http://localhost:8000/api/settings';

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

// Load Configs
const loadConfigs = async () => {
    try {
        const [llmRes, dbRes, parserRes] = await Promise.all([
            axios.get(`${API_BASE}/llm`),
            axios.get(`${API_BASE}/db`),
            axios.get(`${API_BASE}/parser`)
        ]);
        llmConfig.value = llmRes.data;
        dbConfig.value = dbRes.data;
        parserConfig.value = parserRes.data;
    } catch (err) {
        ElMessage.error('加载配置失败');
    }

    // Ensure exam config is loaded for template preview
    await examStore.fetchConfig();
};

onMounted(() => {
    loadConfigs();
});

// Save Actions
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
</style>
