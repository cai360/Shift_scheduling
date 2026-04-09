import { createContext, useContext, useEffect, useState } from 'react';
import { useAuthContext } from './AuthContext';
import { getMyCompanies } from '../services/company.api';

export type MyCompany = {
  company_id: string;
  company_name: string;
  role: string;
};

type CompanyContextType = {
  companies: MyCompany[];
  setCompanies: (companies: MyCompany[]) => void;
  currentCompanyId: string | null;
  setCurrentCompanyId: (companyId: string | null) => void;
  switchCompany: (companyId: string) => void;
  isCompanyInitializing: boolean;
};

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

const COMPANY_STORAGE_KEY = 'currentCompanyId';

export const CompanyProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { user, isAuthInitializing } = useAuthContext();
  const [companies, setCompanies] = useState<MyCompany[]>([]);
  const [currentCompanyId, setCurrentCompanyId] = useState<string | null>(null);
  const [isCompanyInitializing, setIsCompanyInitializing] = useState(true);

  const switchCompany = (companyId: string) => {
    const exists = companies.some((company) => company.company_id === companyId);
    if (!exists) {
      return;
    }
    setCurrentCompanyId(companyId);
    localStorage.setItem(COMPANY_STORAGE_KEY, companyId);
  };

  useEffect( ()=> {
    if (isAuthInitializing) return;
    setIsCompanyInitializing(true);

    const restoreCompanies = async () => {
      if(!user) {
        setCompanies([]);
        setCurrentCompanyId(null);
        setIsCompanyInitializing(false);
        localStorage.removeItem(COMPANY_STORAGE_KEY);
        return;
      }

      try {
        const companyList = await getMyCompanies();
        const nextCompanies = companyList.data;

        setCompanies(nextCompanies);

        const savedCompanyId = localStorage.getItem(COMPANY_STORAGE_KEY);

        const matchedCompany = nextCompanies.find(
          (company:MyCompany) => company.company_id === savedCompanyId
        );

        if (matchedCompany) {
          setCurrentCompanyId(matchedCompany.company_id);
        }else if (nextCompanies.length > 0){
          setCurrentCompanyId(nextCompanies[0].company_id);
          localStorage.setItem(COMPANY_STORAGE_KEY, nextCompanies[0].company_id);
        }else {
          setCurrentCompanyId(null);
          localStorage.removeItem(COMPANY_STORAGE_KEY)
        }
      }catch (error){
        setCompanies([]);
        setCurrentCompanyId(null);
        localStorage.removeItem(COMPANY_STORAGE_KEY);
      } finally {
        setIsCompanyInitializing(false);
      }
    };
    restoreCompanies();

  }, [user, isAuthInitializing]);

  return (
    <CompanyContext.Provider
     value={{
        companies,
        currentCompanyId,
        setCompanies,
        setCurrentCompanyId,
        switchCompany,
        isCompanyInitializing,
      }}
    >
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompanyContext = () => {
  const context = useContext(CompanyContext);

  if (!context) {
    throw new Error('useCompanyContext must be used within CompanyProvider');
  }

  return context;
};