<template>
  <div class="config-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>考试基本信息</span>
          <el-button type="primary" @click="saveSettings">保存配置</el-button>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="考试名称">
          <el-input v-model="examStore.config.exam_name" placeholder="例如: 2025_期末考试" />
        </el-form-item>
      </el-form>

      <el-divider content-position="left">题型配置</el-divider>

      <el-table :data="examStore.config.sections" border style="width: 100%">
        <el-table-column prop="section_id" label="ID" width="60" />
        <el-table-column label="识别关键字" min-width="180">
          <template #default="scope">
            <el-input v-model="scope.row.match_keyword" />
          </template>
        </el-table-column>
        <el-table-column label="报表列名" min-width="120">
          <template #default="scope">
            <el-input v-model="scope.row.name" />
          </template>
        </el-table-column>
        <el-table-column label="每题分值" width="120">
          <template #default="scope">
            <el-input-number v-model="scope.row.score" :min="0" :step="0.5" />
          </template>
        </el-table-column>
        <el-table-column label="题目数量" width="120">
          <template #default="scope">
            <el-input-number v-model="scope.row.num_questions" :min="1" />
          </template>
        </el-table-column>
        <el-table-column label="题型" width="140">
          <template #default="scope">
            <el-select v-model="scope.row.question_type">
              <el-option label="客观题" value="客观题" />
              <el-option label="主观题" value="主观题" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center">
          <template #default="scope">
            <el-button type="danger" icon="Delete" circle @click="removeSection(scope.$index)" />
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 10px">
        <el-button @click="addSection" icon="Plus">添加题型</el-button>
      </div>

    </el-card>

    <div class="mt-20" v-if="hasSubjective">
       <el-alert title="检测到主观题：请在「系统配置」页面配置 LLM (大语言模型) 以启用智能批改" type="info" show-icon :closable="false" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useExamStore } from '../stores/examStore';
import { ElMessage } from 'element-plus';

const examStore = useExamStore();

const hasSubjective = computed(() => {
    return examStore.config.sections.some(s => s.question_type === '主观题');
});

onMounted(() => {
  examStore.fetchConfig();
});

const addSection = () => {
  examStore.config.sections.push({
    section_id: String(examStore.config.sections.length + 1),
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
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mt-20 {
    margin-top: 20px;
}
</style>
