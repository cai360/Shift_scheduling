import { createContext } from 'react';
import { CompanyRole } from '../types/company';

export type MyCompany = {
  company_id: string;
  company_name: string;
  role: CompanyRole;
};

export type CompanyContextType = {
  companies: MyCompany[];
  setCompanies: (companies: MyCompany[]) => void;
  currentCompanyId: string | null;
  setCurrentCompanyId: (companyId: string | null) => void;
  switchCompany: (companyId: string) => void;
  isCompanyInitializing: boolean;
};

export const CompanyContext = createContext<CompanyContextType | undefined>(
  undefined,
);
