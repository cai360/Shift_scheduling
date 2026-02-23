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
      navigate('/');
      console.log('Logout Success');
    } catch (err) {
      console.error('Logout Failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Home Page</h1>
      <AppButton loading={loading} onClick={handleLogout}>
        登出
      </AppButton>
    </div>
  );
};

export default HomePage;
