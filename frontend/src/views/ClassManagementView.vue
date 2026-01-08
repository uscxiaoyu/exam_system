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
    
    <el-table-column label="Actions" width="350">
          <template #default="scope">
            <el-button size="small" @click="openImportDialog(scope.row)">Import Roster</el-button>
            <el-button size="small" type="success" @click="syncUsers(scope.row)">Create Accounts</el-button>
            <el-button size="small" type="info" @click="viewGrades(scope.row)">View Grades</el-button>
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

    <!-- Grades Dialog -->
    <el-dialog v-model="showGradesDialog" title="Class Grades" width="80%">
       <div style="margin-bottom: 20px;">
          <h3>{{ currentClass?.name }} - Gradebook</h3>
       </div>
       <el-table :data="gradebook.students" border height="500">
          <el-table-column prop="number" label="Student ID" width="120" fixed />
          <el-table-column prop="name" label="Name" width="120" fixed />
          <el-table-column 
             v-for="exam in gradebook.exams" 
             :key="exam.id" 
             :label="exam.name"
             width="150"
          >
             <template #default="scope">
                {{ scope.row.grades[exam.id] !== undefined ? scope.row.grades[exam.id] : '-' }}
             </template>
          </el-table-column>
          <el-table-column label="Actions" min-width="100" fixed="right">
              <template #default="scope">
                  <el-button size="small" type="danger" @click="removeStudent(scope.row)">Delete</el-button>
              </template>
          </el-table-column>
       </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../utils/request'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const classes = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const showImportDialog = ref(false)
const showGradesDialog = ref(false)
const currentClass = ref(null)

const gradebook = ref({ exams: [], students: [] })

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

const syncUsers = async (cls) => {
  try {
    await ElMessageBox.confirm(
      `Create login accounts for all students in ${cls.name}? Default password will be "123456".`,
      'Confirm Create Accounts',
      {
        confirmButtonText: 'Create',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )
    
    const res = await axios.post('/api/v1/students/sync-users', { class_id: cls.id })
    ElMessage.success(res.data.message)
  } catch (err) {
    if (err !== 'cancel') {
       ElMessage.error('Failed to sync users')
    }
  }
}

const viewGrades = async (cls) => {
  currentClass.value = cls
  try {
     const res = await axios.get(`/api/v1/classes/${cls.id}/grades`)
     gradebook.value = res.data
     showGradesDialog.value = true
  } catch (e) {
     ElMessage.error("Failed to load grades")
  }
}

const removeStudent = async (student) => {
   ElMessage.warning("Delete Student feature requires backend update to return Student ID.")
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
