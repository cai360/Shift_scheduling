import http from '../utils/http';
import { ApiResponse } from './auth.api';

export type Role = 'owner' | 'manager' | 'employee';

export interface Member {
  user_id: string;
  username: string;
  email: string;
  role: Role;
}

export const getMembers = async (companyId: string): Promise<Member[]> => {
  const res = await http.get<ApiResponse<Member[]>>(
    `/companies/${companyId}/users`,
  );
  return res.data;
};

export const updateRole = async (
  companyId: string,
  userId: string,
  role: string,
): Promise<Member> => {
  const res = await http.patch<ApiResponse<Member>>(
    `/companies/${companyId}/users/${userId}/role`,
    { role },
  );
  return res.data;
};
