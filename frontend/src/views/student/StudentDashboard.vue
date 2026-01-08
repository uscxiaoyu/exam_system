<template>
  <div class="student-dashboard">
    <h2>Available Exams</h2>
    <div v-if="loading">Loading...</div>
    <div v-else>
      <el-table :data="exams" style="width: 100%">
        <el-table-column prop="name" label="Exam Name" />
        <el-table-column prop="start_time" label="Start Time" />
        <el-table-column prop="end_time" label="End Time" />
        <el-table-column prop="status" label="Status">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'completed' ? 'success' : 'primary'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action">
          <template #default="scope">
            <el-button
              v-if="scope.row.status !== 'completed'"
              type="primary"
              @click="takeExam(scope.row.id)"
            >
              Start Exam
            </el-button>
            <el-button
              v-else
              type="default"
              disabled
            >
              Completed (Score: {{ scope.row.score }})
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import axios from '../../utils/request'

const exams = ref([])
const loading = ref(true)
const router = useRouter()
const userStore = useUserStore()

const fetchExams = async () => {
  try {
    const response = await axios.get('/api/v1/student/exams/')
    exams.value = response.data
  } catch (error) {
    console.error("Failed to fetch exams", error)
  } finally {
    loading.value = false
  }
}

const takeExam = (id) => {
  router.push(`/student/exam/${id}`)
}

onMounted(() => {
  fetchExams()
})
</script>

<style scoped>
.student-dashboard {
  padding: 20px;
}
</style>
