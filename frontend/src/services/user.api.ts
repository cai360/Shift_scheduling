import http from '../utils/http';
import type { ApiResponse } from './auth.api';

export interface UpdateMePayload {
  username?: string;
  email?: string;
}

export interface UpdatePasswordPayload {
  old_password: string;
  new_password: string;
}

export const updateMe = async (payload: UpdateMePayload) => {
  const res = await http.patch<
    ApiResponse<{ id: string; username: string; email: string }>
  >('/users/me', payload);
  return res.data.data;
};

export const updatePassword = async (payload: UpdatePasswordPayload) => {
  const res = await http.patch<ApiResponse<{ message: string }>>(
    '/users/me/password',
    payload,
  );
  return res.data.data;
};

export const deleteMe = async () => {
  await http.delete('/users/me');
};
