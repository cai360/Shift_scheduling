// utils/http.ts
// 所有 HTTP 行為，只有一個出口
// baseURL
// cookie / session
// JWT
// 錯誤處理
// timeout

import axios from 'axios'
// import { config } from '../env'

const http = axios.create({
  // baseURL: config.apiBaseUrl,
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  withCredentials: true, // Flask session / cookie 會用到
})

http.interceptors.request.use(
  (config) => {
    // 之後 JWT / token 都加在這
    // 未來可以在這裡加 token
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
    // 只回傳後端真正的資料
    console.log(response)
    return response.data
  },
  (error) => {
    // 統一錯誤出口
    return Promise.reject(error)
  }
)

export default http
