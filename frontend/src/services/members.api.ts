import http from '../utils/http';
import { ApiResponse } from './auth.api';

export type Role = 'owner' | 'manager' | 'employee';

export interface Member {
  userId: string;
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
