import { message } from 'antd';
import AppInput from '../components/ui/AppInput';
import AppButton from '../components/ui/AppButton';
import AppPasswordInput from '../components/ui/AppPasswordInout';
import styles from './Login.module.css';
import { login } from '../services/auth.api';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { validateLogin } from '../utils/validator';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {

      setLoading(true);

    const errorMsg = validateLogin({ email, password });

      const res = await login({
        email,
        password,
      });

      const { access_token, refresh_token } = res.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      navigate('/home');
      message.success(`登入成功`);
      console.log('Login Success', res);
    } catch (err) {
      message.error(`登入失敗 ${err}`);
      console.error('Login Failed', err);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <div className={styles.layout}>
        <h1 className={styles.logo}>LOGO</h1>
        <h3 className={styles.title}>Shift Scheduling System</h3>
        <div className={styles.loginBlock}>
          <AppInput
            placeholder="帳號"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <AppPasswordInput
            placeholder="密碼"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <AppButton loading={loading} onClick={handleLogin}>
            登入
          </AppButton>
          <div className={styles.loginFooter}>
            <AppButton onClick={() => navigate('/forget-password')}>
              忘記密碼
            </AppButton>
            <AppButton onClick={() => navigate('/register')}>
              註冊帳號
            </AppButton>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;
