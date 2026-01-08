import axios from 'axios'
import { useUserStore } from '../stores/user'

const service = axios.create({
  baseURL: 'http://localhost:8000', // Adjust if needed
  timeout: 5000
})

service.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = 'Bearer ' + userStore.token
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    return response
  },
  error => {
    return Promise.reject(error)
  }
)

export default service
