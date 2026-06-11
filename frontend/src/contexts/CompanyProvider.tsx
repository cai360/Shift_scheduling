import { useEffect, useState } from 'react';
import {
  CompanyContext,
  CompanyContextType,
  MyCompany,
} from './CompanyContext';
import { useAuthContext } from './useAuthContext';
import { getMyCompanies } from '../services/company.api';

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
    const exists = companies.some(
      (company) => company.company_id === companyId,
    );
    if (!exists) {
      return;
    }
    setCurrentCompanyId(companyId);
    localStorage.setItem(COMPANY_STORAGE_KEY, companyId);
  };

  useEffect(() => {
    if (isAuthInitializing) return;
    setIsCompanyInitializing(true);

    const restoreCompanies = async () => {
      if (!user) {
        setCompanies([]);
        setCurrentCompanyId(null);
        setIsCompanyInitializing(false);
        localStorage.removeItem(COMPANY_STORAGE_KEY);
        return;
      }

      try {
        const companyList = await getMyCompanies();
        const nextCompanies = companyList;

        setCompanies(nextCompanies);

        const savedCompanyId = localStorage.getItem(COMPANY_STORAGE_KEY);

        const matchedCompany = nextCompanies.find(
          (company: MyCompany) => company.company_id === savedCompanyId,
        );

        if (matchedCompany) {
          setCurrentCompanyId(matchedCompany.company_id);
        } else if (nextCompanies.length > 0) {
          setCurrentCompanyId(nextCompanies[0].company_id);
          localStorage.setItem(
            COMPANY_STORAGE_KEY,
            nextCompanies[0].company_id,
          );
        } else {
          setCurrentCompanyId(null);
          localStorage.removeItem(COMPANY_STORAGE_KEY);
        }
      } catch {
        setCompanies([]);
        setCurrentCompanyId(null);
        localStorage.removeItem(COMPANY_STORAGE_KEY);
      } finally {
        setIsCompanyInitializing(false);
      }
    };
    restoreCompanies();
  }, [user, isAuthInitializing]);

  const value: CompanyContextType = {
    companies,
    currentCompanyId,
    setCompanies,
    setCurrentCompanyId,
    switchCompany,
    isCompanyInitializing,
  };

  return (
    <CompanyContext.Provider value={value}>{children}</CompanyContext.Provider>
  );
};
