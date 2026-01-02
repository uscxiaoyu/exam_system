<template>
  <div class="task-assignment">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>Task Assignment</h2>
          <el-select v-model="selectedExamId" placeholder="Select Exam" @change="fetchSections">
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="exam.name"
              :value="exam.id"
            />
          </el-select>
        </div>
      </template>

      <div v-if="selectedExamId">
        <el-button type="warning" @click="syncSections" style="margin-bottom: 20px">
           Sync Sections from Config
        </el-button>

        <el-table :data="sections" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="Section Name" />
          <el-table-column prop="question_range" label="Range" />
          <el-table-column label="Assigned To">
             <template #default="scope">
                <el-select
                  v-model="scope.row.marker_id"
                  placeholder="Select Teacher"
                  @change="(val) => assignMarker(scope.row, val)"
                  clearable
                >
                  <el-option label="Me (Admin)" :value="1" /> <!-- TODO: Fetch real user list -->
                </el-select>
             </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else>
        <el-empty description="Please select an exam" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '../utils/request'
import { ElMessage } from 'element-plus'

const exams = ref([])
const selectedExamId = ref(null)
const sections = ref([])
const loading = ref(false)

const fetchExams = async () => {
    try {
        const res = await axios.get('/api/history/') // Using history endpoint to get exams list
        exams.value = res.data
    } catch (err) {
        console.error(err)
    }
}

const fetchSections = async () => {
    if(!selectedExamId.value) return
    loading.value = true
    try {
        const res = await axios.get(`/api/v1/exams/${selectedExamId.value}/sections`)
        sections.value = res.data
    } catch (err) {
        ElMessage.error('Failed to load sections')
    } finally {
        loading.value = false
    }
}

const syncSections = async () => {
    // In a real app, we'd need the config JSON.
    // Here we might assume the config is already stored or we prompt for it.
    // For simplicity, let's just trigger a dummy sync or assume backend has it.
    // Actually, the endpoint requires body.
    ElMessage.info("Sync requires config JSON. Feature placeholder.")
}

const assignMarker = async (section, markerId) => {
    try {
        await axios.put(`/api/v1/sections/${section.id}/assign`, { marker_id: markerId })
        ElMessage.success("Assigned")
    } catch (err) {
        ElMessage.error("Assignment failed")
    }
}

onMounted(() => {
    fetchExams()
})
</script>
