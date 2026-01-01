<template>
  <div class="results-view">
    <!-- Summary Metrics -->
    <el-row :gutter="20">
       <el-col :span="6">
          <el-card shadow="hover">
             <template #header>总人数</template>
             <div class="metric">{{ totalStudents }}</div>
          </el-card>
       </el-col>
       <el-col :span="6">
          <el-card shadow="hover">
             <template #header>平均分</template>
             <div class="metric">{{ averageScore.toFixed(1) }}</div>
          </el-card>
       </el-col>
       <el-col :span="6">
          <el-card shadow="hover">
             <template #header>最高分</template>
             <div class="metric">{{ maxScore }}</div>
          </el-card>
       </el-col>
       <el-col :span="6">
          <el-card shadow="hover">
             <template #header>及格率</template>
             <div class="metric">{{ passRate }}%</div>
          </el-card>
       </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" class="mt-20">
       <el-col :span="12">
          <el-card>
             <div ref="chartDom" style="width: 100%; height: 300px;"></div>
          </el-card>
       </el-col>
       <el-col :span="12">
           <el-card>
              <div class="actions-panel">
                 <el-button type="success" @click="saveToDB">💾 保存成绩到数据库</el-button>
                 <el-button type="primary" @click="exportExcel">📤 导出 Excel 表格</el-button>
                 <el-button type="warning" @click="triggerSubjectiveGrading" v-if="hasSubjective">🤖 LLM 主观题批改</el-button>
              </div>
           </el-card>
       </el-col>
    </el-row>

    <!-- Detail Table -->
    <el-card class="mt-20">
       <template #header>
          <div class="card-header">
             <span>成绩明细</span>
             <el-input v-model="search" placeholder="搜索姓名/学号" style="width: 200px" />
          </div>
       </template>
       <el-table :data="filteredData" border stripe height="500">
          <el-table-column prop="学号" label="学号" sortable />
          <el-table-column prop="姓名" label="姓名" />
          <el-table-column prop="机号" label="机号" />

          <el-table-column v-for="col in sectionColumns" :key="col" :prop="col" :label="col" sortable />

          <el-table-column prop="总分" label="总分" sortable fixed="right" width="100">
             <template #default="scope">
                <span :style="{ fontWeight: 'bold', color: scope.row['总分'] < 60 ? 'red' : 'green' }">
                   {{ scope.row['总分'] }}
                </span>
             </template>
          </el-table-column>

           <el-table-column label="操作" fixed="right" width="100">
              <template #default="scope">
                 <el-button link type="primary" size="small" @click="viewDetails(scope.row)">详情</el-button>
              </template>
           </el-table-column>
       </el-table>
    </el-card>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="答卷详情" width="70%">
        <div v-if="currentStudent">
            <h3>{{ currentStudent['姓名'] }} ({{ currentStudent['学号'] }})</h3>

            <div v-for="qKey in Object.keys(currentStudent).filter(k => k.startsWith('Q') && !k.endsWith('_comment'))" :key="qKey">
               <div class="question-item">
                   <div class="q-header">
                       <strong>{{ qKey }}</strong>:
                       <span class="score-tag">得分: {{ currentStudent[qKey] }}</span>
                   </div>
                   <!-- Check if there is a comment (Subjective) -->
                   <div v-if="currentStudent[qKey + '_comment']" class="comment-box">
                       <div><strong>评语:</strong> {{ currentStudent[qKey + '_comment'] }}</div>
                   </div>
               </div>
            </div>
        </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useExamStore } from '../stores/examStore';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';

const examStore = useExamStore();
const search = ref('');
const chartDom = ref(null);
const detailVisible = ref(false);
const currentStudent = ref(null);

const results = computed(() => examStore.gradingResults);

const totalStudents = computed(() => results.value.length);
const averageScore = computed(() => {
    if (totalStudents.value === 0) return 0;
    return results.value.reduce((acc, curr) => acc + (curr['总分'] || 0), 0) / totalStudents.value;
});
const maxScore = computed(() => {
     if (totalStudents.value === 0) return 0;
     return Math.max(...results.value.map(s => s['总分'] || 0));
});
const passRate = computed(() => {
    if (totalStudents.value === 0) return 0;
    const passed = results.value.filter(s => (s['总分'] || 0) >= 60).length;
    return ((passed / totalStudents.value) * 100).toFixed(1);
});

const sectionColumns = computed(() => {
    if (results.value.length === 0) return [];
    // Extract dynamic columns from first record, excluding base info and total
    const exclude = ['学号', '姓名', '机号', '总分'];
    return Object.keys(results.value[0]).filter(k => !exclude.includes(k) && !k.startsWith('Q'));
});

const filteredData = computed(() => {
    if (!search.value) return results.value;
    return results.value.filter(item =>
        (item['姓名'] && item['姓名'].includes(search.value)) ||
        (item['学号'] && item['学号'].includes(search.value))
    );
});

const hasSubjective = computed(() => {
    return examStore.config.sections.some(s => s.question_type === '主观题');
});

// Chart initialization
let myChart = null;
const initChart = () => {
    if (!chartDom.value) return;
    myChart = echarts.init(chartDom.value);
    const scores = results.value.map(s => s['总分'] || 0);

    // Histogram buckets
    // Simple implementation
    const buckets = ['0-59', '60-69', '70-79', '80-89', '90-100'];
    const counts = [0, 0, 0, 0, 0];
    scores.forEach(s => {
        if (s < 60) counts[0]++;
        else if (s < 70) counts[1]++;
        else if (s < 80) counts[2]++;
        else if (s < 90) counts[3]++;
        else counts[4]++;
    });

    const option = {
        title: { text: '成绩分布' },
        tooltip: {},
        xAxis: { data: buckets },
        yAxis: {},
        series: [{
            name: '人数',
            type: 'bar',
            data: counts,
            itemStyle: { color: '#409eff' }
        }]
    };
    myChart.setOption(option);
};

onMounted(() => {
    if (results.value.length > 0) {
        initChart();
    }
});

watch(results, () => {
    if (results.value.length > 0) {
        // Wait for DOM update
        setTimeout(initChart, 100);
    }
}, { deep: true });

const viewDetails = (row) => {
    currentStudent.value = row;
    detailVisible.value = true;
};

const saveToDB = async () => {
    const res = await examStore.saveToDB();
    if (res.success) ElMessage.success(res.message);
    else ElMessage.error(res.message);
};

const exportExcel = async () => {
    const res = await examStore.exportResults(results.value);
    if (!res.success) ElMessage.error(res.message);
};

const triggerSubjectiveGrading = async () => {
    // This is a simplified demo. In reality, we should iterate over students and subjective questions.
    // For now, let's just show a message or do a partial implementation
    ElMessage.info("正在后台调用 LLM 进行主观题批改...请稍候刷新页面查看结果 (Demo Mode: 调用第一个学生的第一个主观题)");

    // Find first subjective question
    const subjSec = examStore.config.sections.find(s => s.question_type === '主观题');
    if (!subjSec) return;

    const qKey = `${subjSec.section_id}-1`; // First question of that section
    const qText = `${subjSec.match_keyword} 第1题`;

    // For demonstration, grade first student
    if (examStore.students.length > 0) {
        const student = examStore.students[0];
        const ans = student[qKey];
        if (ans) {
             const res = await examStore.gradeSubjective(qKey, qText, "参考答案在此...", ans, 10);
             ElMessage.success(`批改完成: 得分 ${res.score}, 评语: ${res.comment}`);
             // Need to update local state to reflect this change
        }
    }
};

</script>

<style scoped>
.metric { font-size: 24px; font-weight: bold; color: #409eff; text-align: center; }
.mt-20 { margin-top: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.actions-panel { display: flex; flex-direction: column; gap: 10px; align-items: center; justify-content: center; height: 100%;}
.question-item { border-bottom: 1px solid #eee; padding: 10px 0; }
.q-header { display: flex; justify-content: space-between; }
.score-tag { font-weight: bold; color: #67c23a; }
.comment-box { background: #f0f9eb; padding: 8px; margin-top: 5px; border-radius: 4px; font-size: 13px; color: #555; }
</style>
