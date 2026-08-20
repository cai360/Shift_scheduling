import { Spin } from 'antd';
import CompanyOnboardingView from '../components/company/CompanyOnboardingView';
import PublishedScheduleView from '../components/shifts/PublishedScheduleView';
import { useCompanyContext } from '../contexts/useCompanyContext';
import { CompanyRoles } from '../types/company';

const HomePage = () => {
  const { companies, currentCompanyId, isCompanyInitializing } =
    useCompanyContext();

  const currentCompany = companies.find(
    (company) => company.company_id === currentCompanyId,
  );
  const canManageShifts =
    currentCompany?.role === CompanyRoles.OWNER ||
    currentCompany?.role === CompanyRoles.MANAGER;

  if (isCompanyInitializing) {
    return (
      <div>
        <Spin size="large" />
      </div>
    );
  }

  if (companies.length === 0) {
    return <CompanyOnboardingView />;
  }

  if (!currentCompanyId) return null;

  return (
    <PublishedScheduleView
      key={currentCompanyId}
      companyId={currentCompanyId}
      showStatus={canManageShifts}
    />
  );
};

export default HomePage;
