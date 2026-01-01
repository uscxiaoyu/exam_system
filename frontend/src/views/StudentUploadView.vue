<template>
  <div class="student-upload-view">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>批量上传学生答卷</span>
        </div>
      </template>
      
      <el-alert 
        title="上传说明" 
        type="info" 
        description="请上传 .txt 格式的学生答题卡文件。系统将自动解析文件名或内容中的学生信息。"
        show-icon
        :closable="false"
        class="mb-20"
      />

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
         <el-button type="primary" size="large" @click="startParsing" :loading="parsing" :disabled="studentFiles.length === 0">
            📥 开始解析 ({{ studentFiles.length }} 文件)
         </el-button>
      </div>
    </el-card>

    <el-row class="mt-20" v-if="examStore.students.length > 0">
        <el-col :span="24">
            <el-card>
                <template #header>
                   <div class="card-header">
                       <span>解析结果预览 ({{ examStore.students.length }} 人)</span>
                       <el-button type="success" size="small" @click="goToGrading">前往客观题阅卷</el-button>
                   </div>
                </template>
                <el-table :data="examStore.students" style="width: 100%" max-height="500" border stripe>
                    <el-table-column type="index" label="#" width="50" />
                    <el-table-column prop="学号" label="学号" sortable />
                    <el-table-column prop="姓名" label="姓名" />
                    <el-table-column prop="机号" label="机号" />
                    <el-table-column label="答题情况">
                        <template #default="scope">
                            <el-tag>{{ Object.keys(scope.row.answers || {}).length }} 题已作答</el-tag>
                        </template>
                    </el-table-column>
                </el-table>
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
import { UploadFilled } from '@element-plus/icons-vue';

const examStore = useExamStore();
const router = useRouter();
const fileList = ref([]);
const studentFiles = ref([]);
const parsing = ref(false);

const handleStudentChange = (file, fileList) => {
    // Manually manage files
    studentFiles.value.push(file.raw);
};

const startParsing = async () => {
    if (studentFiles.value.length === 0) {
        ElMessage.warning('请选择文件');
        return;
    }
    
    parsing.value = true;
    try {
        const uploadRes = await examStore.uploadStudentPapers(studentFiles.value);
        if (uploadRes) {
            ElMessage.success(`成功解析 ${examStore.students.length} 份答卷`);
        } else {
            ElMessage.error('解析失败');
        }
    } finally {
        parsing.value = false;
    }
};

const goToGrading = () => {
    router.push({ name: 'objective' });
};
</script>

<style scoped>
.mb-20 { margin-bottom: 20px; }
.mt-20 { margin-top: 20px; }
.actions { margin-top: 20px; text-align: center; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
</style>
