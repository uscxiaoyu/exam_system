<template>
  <div class="objective-marking-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客观题自动阅卷</span>
        </div>
      </template>

      <!-- Status Check -->
      <el-row :gutter="20" class="mb-20">
         <el-col :span="12">
             <el-result 
               :icon="hasStandardKey ? 'success' : 'warning'" 
               title="标准答案" 
               :sub-title="hasStandardKey ? '已就绪' : '未配置 (请前往系统配置)'"
             >
             </el-result>
         </el-col>
         <el-col :span="12">
             <el-result 
               :icon="hasStudents ? 'success' : 'warning'" 
               title="学生答卷" 
               :sub-title="hasStudents ? `已加载 ${examStore.students.length} 份` : '未上传 (请前往答卷上传)'"
             >
             </el-result>
         </el-col>
      </el-row>

      <!-- Action -->
      <div class="actions" v-if="canGrade">
         <el-button type="primary" size="large" @click="startGrading" :loading="examStore.loading">
            🚀 开始客观题阅卷
         </el-button>
         <p class="hint">系统将根据标准答案自动批改客观题部分，并计算总分。</p>
      </div>
      <div v-else class="actions">
         <el-button type="info" disabled size="large">请先完成数据准备</el-button>
      </div>

    </el-card>

    <!-- Preview Table -->
    <el-card class="mt-20" v-if="hasStudents">
         <template #header>待阅卷学生列表</template>
         <el-table :data="examStore.students" style="width: 100%" height="400">
             <el-table-column prop="学号" label="学号" />
             <el-table-column prop="姓名" label="姓名" />
             <el-table-column prop="机号" label="机号" />
             <el-table-column label="状态">
                <template #default="scope">
                   <el-tag v-if="scope.row.total_score !== undefined" type="success">已阅卷 ({{scope.row.total_score}}分)</el-tag>
                   <el-tag v-else type="info">待阅卷</el-tag>
                </template>
             </el-table-column>
         </el-table>
     </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useExamStore } from '../stores/examStore';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const examStore = useExamStore();
const router = useRouter();

const hasStandardKey = computed(() => {
    return examStore.standardKey && Object.keys(examStore.standardKey).length > 0;
});

const hasStudents = computed(() => {
    return examStore.students && examStore.students.length > 0;
});

const canGrade = computed(() => hasStandardKey.value && hasStudents.value);

const startGrading = async () => {
    const gradeSuccess = await examStore.batchGrade();
    if (gradeSuccess) {
        ElMessage.success('阅卷完成！');
        router.push({ name: 'results' });
    } else {
        ElMessage.error('阅卷过程中出错');
    }
};
</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.actions { text-align: center; margin-top: 20px; padding: 20px 0; border-top: 1px solid #ebeef5; }
.hint { color: #999; margin-top: 10px; font-size: 14px; }
.card-header { font-weight: bold; }
</style>
