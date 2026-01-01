<template>
  <div class="upload-view">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>1. 上传标准答案</span>
            </div>
          </template>
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

          <div v-if="examStore.standardKey" class="success-info">
             <el-alert title="标准答案解析成功" type="success" :closable="false" show-icon />
             <div class="json-preview">
                {{ Object.keys(examStore.standardKey).length }} items loaded.
             </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>2. 上传学生答卷 (批量)</span>
            </div>
          </template>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            multiple
            :on-change="handleStudentChange"
            :file-list="fileList"
            accept=".txt"
          >
             <el-icon class="el-icon--upload"><upload-filled /></el-icon>
             <div class="el-upload__text">
              Drop files here or <em>click to upload</em>
            </div>
          </el-upload>

          <div class="actions">
             <el-button type="primary" size="large" @click="startGrading" :loading="examStore.loading">
                🚀 开始解析与阅卷
             </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row class="mt-20" v-if="examStore.students.length > 0">
        <el-col :span="24">
            <el-card>
                <template #header>解析结果预览 ({{ examStore.students.length }} 人)</template>
                <el-table :data="examStore.students.slice(0, 5)" style="width: 100%">
                    <el-table-column prop="学号" label="学号" />
                    <el-table-column prop="姓名" label="姓名" />
                    <el-table-column prop="机号" label="机号" />
                </el-table>
                <div v-if="examStore.students.length > 5" class="more-info">...以及更多</div>
            </el-card>
        </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useExamStore } from '../stores/examStore';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const examStore = useExamStore();
const router = useRouter();
const fileList = ref([]);
const studentFiles = ref([]);

const handleStandardChange = async (file) => {
    const success = await examStore.uploadStandardAnswer(file.raw);
    if (success) ElMessage.success('标准答案上传成功');
    else ElMessage.error('标准答案解析失败');
};

const handleStudentChange = (file, fileList) => {
    // Manually manage files to support batch upload trigger later
    studentFiles.value.push(file.raw);
};

const startGrading = async () => {
    if (!examStore.standardKey) {
        ElMessage.warning('请先上传标准答案');
        return;
    }
    if (studentFiles.value.length === 0) {
        ElMessage.warning('请选择学生答卷文件');
        return;
    }

    // 1. Upload Student Files
    const uploadRes = await examStore.uploadStudentPapers(studentFiles.value);
    if (!uploadRes) {
        ElMessage.error('文件上传失败');
        return;
    }

    // 2. Batch Grade (Objective)
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
.mt-20 { margin-top: 20px; }
.actions { margin-top: 20px; text-align: right; }
.success-info { margin-top: 10px; }
.more-info { text-align: center; color: #999; padding: 10px;}
</style>
