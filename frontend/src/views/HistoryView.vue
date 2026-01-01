<template>
  <div class="history-view">
    <el-card>
      <template #header>
         <div class="card-header">
             <span>历史考情档案</span>
             <el-button icon="Refresh" circle @click="loadExams" />
         </div>
      </template>

      <div v-if="error" class="error-msg">
         <el-alert :title="error" type="warning" show-icon :closable="false" />
      </div>

      <div v-else>
         <div class="selector">
             <el-select v-model="selectedExam" placeholder="请选择考试场次" @change="loadExamData" style="width: 300px">
                <el-option
                  v-for="exam in examList"
                  :key="exam.exam_name"
                  :label="`${exam.exam_name} (${exam.created_at || 'N/A'})`"
                  :value="exam.exam_name"
                />
             </el-select>
         </div>

         <el-table v-if="historyData.length > 0" :data="historyData" border stripe style="width: 100%; margin-top: 20px" height="600">
             <el-table-column prop="student_id" label="学号" sortable />
             <el-table-column prop="student_name" label="姓名" />
             <el-table-column prop="machine_id" label="机号" />
             <el-table-column prop="total_score" label="总分" sortable />
             <el-table-column prop="created_at" label="归档时间" />
             <!-- Dynamic score columns could be added here similar to ResultsView -->
         </el-table>

         <el-empty v-else description="请选择考试查看详情" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';
const examList = ref([]);
const selectedExam = ref('');
const historyData = ref([]);
const error = ref(null);

const loadExams = async () => {
    try {
        error.value = null;
        const res = await axios.get(`${API_BASE}/history/`);
        examList.value = res.data;
    } catch (err) {
        if (err.response && err.response.status === 503) {
            error.value = "数据库连接不可用，历史记录功能已禁用。";
        } else {
            error.value = "加载历史记录失败";
        }
    }
};

const loadExamData = async () => {
    if (!selectedExam.value) return;
    try {
        const res = await axios.get(`${API_BASE}/history/${selectedExam.value}`);
        historyData.value = res.data;
    } catch (err) {
        console.error(err);
    }
};

onMounted(() => {
    loadExams();
});
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.selector { margin-bottom: 20px; }
.error-msg { margin: 20px 0; }
</style>
