<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>Login</h2>
      </template>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item label="Username">
          <el-input v-model="form.username" placeholder="Username / Student ID" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" placeholder="Password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%">Login</el-button>
        </el-form-item>
      </el-form>
      <div v-if="error" class="error-msg">{{ error }}</div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const form = reactive({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')
const router = useRouter()
const userStore = useUserStore()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)

    // Call login endpoint
    const res = await axios.post('http://localhost:8000/api/v1/auth/login', formData)
    const token = res.data.access_token

    // Store token
    userStore.setToken(token)

    // Get user info to redirect correctly
    const meRes = await axios.get('http://localhost:8000/api/v1/auth/me', {
       headers: { Authorization: `Bearer ${token}` }
    })
    userStore.setUser(meRes.data)

    ElMessage.success('Login successful')

    if (meRes.data.role === 'student') {
      router.push('/student/dashboard')
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error(e)
    error.value = 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
.error-msg {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>
