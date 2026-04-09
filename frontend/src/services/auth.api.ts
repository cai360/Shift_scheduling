import { UUID } from 'crypto';
import http from '../utils/http';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}
export interface MePayload {
  id: string;
  username: string;
  email: string;
  created_at: string;
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

export interface CreateCompanyPayload {
  name: string;
  description: string;
}

// mapping backend api format
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
}

export interface CreateCompanyResponse {
  id: UUID;
  name: string;
  is_active: boolean;
  description: string;
}

export interface JoinCompanyResponse {
  company_id: UUID;
  user_id: UUID;
  role: string;
}

// export const login = (payload: LoginPayload) => {
//   return http.post<ApiResponse<LoginTokens>>('/auth/login', payload)
// }

export const getMe = () => {
  return http.get<MePayload>('/users/me');
};

export const login = (payload: LoginPayload) => {
  return http.post<LoginResponse>('/auth/login', payload);
};

export const register = (payload: RegisterPayload) => {
  return http.post<RegisterResponse>('/auth/register', payload);
};

export const createCompany = (payload: CreateCompanyPayload) => {
  return http.post<CreateCompanyResponse>('/companies', payload);
};

export const joinCompany = (companyId: string) => {
  return http.post<JoinCompanyResponse>(`/companies/${companyId}/join`);
};
