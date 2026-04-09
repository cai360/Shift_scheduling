import http from '../utils/http';


export interface MyCompany {
    company_id: string;
    company_name: string;
    role: string;
}

export type MyCompaniesResponse = MyCompany[];

export const getMyCompanies = () => {
    return http.get<MyCompaniesResponse>('/users/me/companies');
}
