import { message } from 'antd';
import AppButton from '../components/ui/AppButton';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    try {
      setLoading(true);
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      navigate('/login');
      message.success(`登出成功`);
    } catch (err) {
      message.error(`登出失敗`);
      console.error('Logout Failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Home Page</h1>
      <AppButton loading={loading} onClick={() => navigate('/new-company')}>
        新公司
      </AppButton>
      <AppButton loading={loading} onClick={handleLogout}>
        登出
      </AppButton>
    </div>
  );
};

export default HomePage;
