import http from '../utils/http';
import { ApiResponse } from './auth.api';
import type { CompanyRole } from '../types/company';

export interface Member {
  user_id: string;
  username: string;
  email: string;
  role: CompanyRole;
}

export const getMembers = async (companyId: string): Promise<Member[]> => {
  const res = await http.get<ApiResponse<Member[]>>(
    `/companies/${companyId}/users`,
  );
  return res.data.data;
};

export const updateRole = async (
  companyId: string,
  userId: string,
  role: CompanyRole,
): Promise<Member> => {
  const res = await http.patch<ApiResponse<Member>>(
    `/companies/${companyId}/users/${userId}/role`,
    { role },
  );
  return res.data.data;
};

export const transferOwner = async (
  companyId: string,
  targetId: string,
): Promise<Member> => {
  const res = await http.post<ApiResponse<Member>>(
    `/companies/${companyId}/users/${targetId}/transfer-ownership`,
  );
  return res.data.data;
};
