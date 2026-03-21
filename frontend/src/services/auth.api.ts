import { UUID } from 'crypto';
import http from '../utils/http';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}
export interface LoginTokens {
  access_token: string;
  refresh_token: string;
}

export interface LoginPayload {
  // call api format
  email: string;
  password: string;
}

export interface RegisterPayload {
  // call api format
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  // mapping backend api format
  access_token: string;
  refresh_token: string;
}

export interface RegisterResponse {
  // mapping backend api format
  id: UUID;
  username: string;
  email: string;
  password: string;
}

// export const login = (payload: LoginPayload) => {
//   return http.post<ApiResponse<LoginTokens>>('/auth/login', payload)
// }
export const login = (payload: LoginPayload) => {
  return http.post<LoginResponse>('/auth/login', payload);
};

export const register = (payload: RegisterPayload) => {
  return http.post<RegisterResponse>('/auth/register', payload);
};
