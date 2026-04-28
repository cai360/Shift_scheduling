import http from '../utils/http';
import { ApiResponse } from './auth.api';

export interface MyCompany {
  company_id: string;
  company_name: string;
  role: string;
}

export type MyCompaniesResponse = MyCompany[];

export const getMyCompanies = async (): Promise<MyCompany[]> => {
  const res = await http.get<ApiResponse<MyCompaniesResponse>>(
    '/users/me/companies',
  );
  return res.data.data;
};
