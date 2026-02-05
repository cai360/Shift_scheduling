// services/auth.api.ts
import http from '../utils/http'

export interface ApiResponse<T> {
  success: boolean
  data: T
}
export interface LoginTokens {
  access_token: string
  refresh_token: string
}

export interface LoginPayload {
    // 限制呼叫 API 的資料格式
    // 少打一個欄位，TS 直接報錯
    email: string
    password: string
}

export interface LoginResponse {
    // 跟 Flask 回傳格式對齊
    // 前端 IDE 會提示你有什麼資料
    access_token: string
    refresh_token: string
}

// export const login = (payload: LoginPayload) => {
//   return http.post<ApiResponse<LoginTokens>>('/auth/login', payload)
// }
export const login = (payload: LoginPayload) => {
  return http.post<LoginResponse>('/auth/login', payload)
}
