import { useNavigate } from 'react-router-dom';
import CompanyOnboardingView from '../components/company/CompanyOnboardingView';

const NewCompanyPage = () => {
  const navigate = useNavigate();

  return <CompanyOnboardingView onCompleted={() => navigate('/home')} />;
};

export default NewCompanyPage;
