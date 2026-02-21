import axios from 'axios'
// import { config } from '../env'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  withCredentials: true, // Flask session / cookie will be used
})

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

http.interceptors.response.use(
  (response) => {
    // only handle success
    return response.data
  },
  (error) => {
    // all error output
    return Promise.reject(error)
  }
)

export default http
