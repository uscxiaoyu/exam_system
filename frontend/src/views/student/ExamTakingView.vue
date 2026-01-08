<template>
  <div class="exam-taking">
    <div v-if="loading">Loading Exam...</div>
    <div v-else>
      <h2>{{ exam.name }}</h2>
      <div v-for="(question, index) in exam.questions" :key="question.id" class="question-block">
        <p><strong>{{ index + 1 }}. {{ question.content }}</strong> ({{ question.score }} points)</p>

        <div v-if="question.type === 'choice'">
          <el-radio-group v-model="answers[question.id]">
            <el-radio v-for="opt in question.options" :key="opt" :label="opt">{{ opt }}</el-radio>
          </el-radio-group>
        </div>

        <div v-else-if="question.type === 'true_false'">
          <el-radio-group v-model="answers[question.id]">
            <el-radio label="True">True</el-radio>
            <el-radio label="False">False</el-radio>
          </el-radio-group>
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" size="large" @click="submitExam">Submit Exam</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import axios from '../../utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const exam = ref({})
const answers = reactive({})
const loading = ref(true)

const fetchExam = async () => {
  try {
    const response = await axios.get(`/api/v1/student/exams/${route.params.id}`)
    exam.value = response.data
    // Initialize answers
    if (exam.value.questions) {
      exam.value.questions.forEach(q => {
        answers[q.id] = ''
      })
    }
  } catch (error) {
    console.error("Failed to load exam", error)
    ElMessage.error("Failed to load exam")
  } finally {
    loading.value = false
  }
}

const submitExam = async () => {
  try {
    const response = await axios.post(`/api/v1/student/exams/${route.params.id}/submit`, answers)
    ElMessage.success(`Submitted! Score: ${response.data.score}`)
    router.push('/student/dashboard')
  } catch (error) {
    console.error("Submit failed", error)
    ElMessage.error("Failed to submit exam")
  }
}

onMounted(() => {
  fetchExam()
})
</script>

<style scoped>
.exam-taking {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.question-block {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
}
.actions {
  margin-top: 30px;
  text-align: center;
}
</style>
