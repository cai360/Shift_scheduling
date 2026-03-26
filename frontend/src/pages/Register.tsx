import { message } from 'antd';
import AppInput from '../components/ui/AppInput';
import AppButton from '../components/ui/AppButton';
import AppPasswordInput from '../components/ui/AppPasswordInout';
import styles from './Register.module.css';
import { register } from '../services/auth.api';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { validateRegister } from '../utils/validator';

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const isValidEmail = (email: string) => {
    return /\S+@\S+\.\S+/.test(email);
  };
  const handleRegister = async () => {
    // if (password !== confirmPassword) {
    //   setError('兩次密碼不一致');
    //   return;
    // }

    // if (!isValidEmail(email)) {
    //   setError('Email 格式錯誤');
    //   return;
    // }
    const errorMsg = validateRegister({ email, password, confirmPassword });

    if (errorMsg) {
      setError(errorMsg);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const res = await register({
        email,
        password,
        username: email,
      });

      navigate('/login');
      message.success(`註冊成功`);
      console.log('Register Success', res);
    } catch (err) {
      message.error(`註冊失敗 ${err}`);
      console.error('Register Failed', err);
      setError('註冊失敗: ' + err);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <div className={styles.layout}>
        <img src="https://picsum.photos/300/200/?random=10" />
        <h1>註冊帳號</h1>
        <div className={styles.block}>
          <AppInput
            placeholder="電子信箱"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <AppPasswordInput
            placeholder="密碼"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <AppPasswordInput
            placeholder="確認密碼"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          {error && <p className={styles.error}>{error}</p>}

          <div className={styles.button}>
            <AppButton
              className={styles.back}
              onClick={() => navigate('/login')}
            >
              返回
            </AppButton>
            <AppButton loading={loading} onClick={handleRegister}>
              註冊
            </AppButton>
          </div>
        </div>
      </div>
    </>
  );
};

export default RegisterPage;
