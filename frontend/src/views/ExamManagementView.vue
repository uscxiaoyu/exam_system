<template>
  <div class="exam-management">
    <div class="header">
      <h2>Exam Management</h2>
      <el-button type="primary" @click="showCreateDialog = true">Create Exam</el-button>
    </div>

    <el-table :data="exams" style="width: 100%; margin-top: 20px;">
      <el-table-column prop="name" label="Exam Name" />
      <el-table-column prop="status" label="Status" />
      <el-table-column prop="class_id" label="Class ID" />
      <el-table-column label="Actions">
        <template #default="scope">
           <el-button size="small" @click="editExam(scope.row)">Edit</el-button>
           <el-button size="small" type="danger" @click="deleteExam(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showCreateDialog" :title="isEditing ? 'Edit Exam' : 'Create Exam'" width="70%">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Class ID">
          <el-input v-model.number="form.class_id" type="number" />
        </el-form-item>
        <el-form-item label="Status">
           <el-select v-model="form.status">
             <el-option label="Draft" value="draft" />
             <el-option label="Publishing" value="publishing" />
             <el-option label="Finished" value="finished" />
           </el-select>
        </el-form-item>
        <el-form-item label="Times">
           <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            start-placeholder="Start Date"
            end-placeholder="End Date"
           />
        </el-form-item>

        <h3>Questions</h3>
        <div v-for="(q, idx) in form.questions" :key="idx" class="question-editor">
          <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
             <strong>Question {{ idx + 1 }}</strong>
             <el-button type="danger" icon="Delete" circle @click="removeQuestion(idx)" />
          </div>
          <el-form-item label="Type">
            <el-select v-model="q.type">
              <el-option label="Multiple Choice" value="choice" />
              <el-option label="True/False" value="true_false" />
            </el-select>
          </el-form-item>
          <el-form-item label="Content">
            <el-input v-model="q.content" type="textarea" />
          </el-form-item>
          <el-form-item label="Score">
             <el-input v-model.number="q.score" type="number" />
          </el-form-item>

          <template v-if="q.type === 'choice'">
             <el-form-item label="Options">
               <div v-for="(opt, optIdx) in q.options" :key="optIdx" style="display: flex; margin-bottom: 5px;">
                 <el-input v-model="q.options[optIdx]" placeholder="Option text" />
                 <el-button @click="q.options.splice(optIdx, 1)" icon="Delete" circle style="margin-left: 5px;" />
               </div>
               <el-button size="small" @click="q.options.push('')">+ Add Option</el-button>
             </el-form-item>
          </template>

          <el-form-item label="Correct Answer">
             <el-input v-model="q.answer" placeholder="Match option text EXACTLY" />
          </el-form-item>
          <hr />
        </div>
        <el-button @click="addQuestion">+ Add Question</el-button>

      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveExam">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import axios from '../utils/request'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const exams = ref([])
const showCreateDialog = ref(false)
const isEditing = ref(false)
const userStore = useUserStore()

const form = reactive({
  id: null,
  name: '',
  class_id: null,
  status: 'draft',
  questions: [],
  start_time: null,
  end_time: null
})

const dateRange = ref([])

// Sync dateRange with form
watch(dateRange, (val) => {
  if (val && val.length === 2) {
    form.start_time = val[0]
    form.end_time = val[1]
  } else {
    form.start_time = null
    form.end_time = null
  }
})

const fetchExams = async () => {
  try {
     const res = await axios.get('/api/v1/exams/')
     exams.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const addQuestion = () => {
  form.questions.push({
    id: Date.now().toString(),
    type: 'choice',
    content: '',
    options: ['A', 'B', 'C', 'D'],
    answer: '',
    score: 5
  })
}

const removeQuestion = (idx) => {
  form.questions.splice(idx, 1)
}

const saveExam = async () => {
  try {
    const payload = { ...form }
    if (isEditing.value && form.id) {
       await axios.put(`/api/v1/exams/${form.id}`, payload)
    } else {
       await axios.post('/api/v1/exams/', payload)
    }
    showCreateDialog.value = false
    fetchExams()
    ElMessage.success("Exam saved")
  } catch (e) {
    ElMessage.error("Error saving exam")
    console.error(e)
  }
}

const editExam = (exam) => {
  isEditing.value = true
  form.id = exam.id
  form.name = exam.name
  form.class_id = exam.class_id
  form.status = exam.status
  form.questions = exam.questions || []
  if (exam.start_time && exam.end_time) {
     dateRange.value = [exam.start_time, exam.end_time]
  } else {
     dateRange.value = []
  }
  showCreateDialog.value = true
}

const deleteExam = async (id) => {
  if (!confirm("Delete this exam?")) return
  try {
    await axios.delete(`/api/v1/exams/${id}`)
    fetchExams()
    ElMessage.success("Deleted")
  } catch(e) {
    ElMessage.error("Error deleting")
  }
}

watch(showCreateDialog, (val) => {
  if (!val) {
    // Reset
    isEditing.value = false
    form.id = null
    form.name = ''
    form.class_id = null
    form.questions = []
    dateRange.value = []
  }
})

onMounted(fetchExams)
</script>

<style scoped>
.exam-management {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.question-editor {
  background: #f9f9f9;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
}
</style>
