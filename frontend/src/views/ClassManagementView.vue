<template>
  <div class="class-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>Class Management</h2>
          <el-button type="primary" @click="showAddDialog = true">Add Class</el-button>
        </div>
      </template>

      <el-table :data="classes" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="Class Name" />
        <el-table-column prop="grade" label="Grade" />
        <el-table-column label="Actions">
          <template #default="scope">
            <el-button size="small" @click="openImportDialog(scope.row)">Import Roster</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Class Dialog -->
    <el-dialog v-model="showAddDialog" title="Add New Class">
      <el-form :model="newClass" label-width="100px">
        <el-form-item label="Class Name">
          <el-input v-model="newClass.name" placeholder="e.g. Class 101" />
        </el-form-item>
        <el-form-item label="Grade">
          <el-input v-model="newClass.grade" placeholder="e.g. Grade 10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">Cancel</el-button>
          <el-button type="primary" @click="createClass">Create</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import Student Dialog -->
    <el-dialog v-model="showImportDialog" title="Import Students">
      <p>Upload CSV or Excel file with "Name" and "Student Number" columns.</p>
      <el-upload
        class="upload-demo"
        drag
        action=""
        :http-request="handleImport"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          Drop file here or <em>click to upload</em>
        </div>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../utils/request'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const classes = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const showImportDialog = ref(false)
const currentClass = ref(null)

const newClass = ref({
  name: '',
  grade: ''
})

const fetchClasses = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/classes/')
    classes.value = res.data
  } catch (err) {
    ElMessage.error('Failed to load classes')
  } finally {
    loading.value = false
  }
}

const createClass = async () => {
  try {
    await axios.post('/api/v1/classes/', newClass.value)
    ElMessage.success('Class created')
    showAddDialog.value = false
    newClass.value = { name: '', grade: '' }
    fetchClasses()
  } catch (err) {
    ElMessage.error('Failed to create class')
  }
}

const openImportDialog = (cls) => {
  currentClass.value = cls
  showImportDialog.value = true
}

const handleImport = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)

  try {
    const res = await axios.post(`/api/v1/classes/${currentClass.value.id}/students/import`, formData)
    ElMessage.success(res.data.message)
    showImportDialog.value = false
  } catch (err) {
    ElMessage.error('Import failed: ' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  fetchClasses()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
