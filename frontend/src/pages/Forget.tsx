import AppInput from '../components/ui/AppInput';
import AppButton from '../components/ui/AppButton';
import styles from './Login.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ForgetPage = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      setLoading(true);
      //   const res = await register({
      //       email,
      //       password
      //   });

      navigate('/login');
      console.log('Forget-password Success');
    } catch (err) {
      console.error('Forget-password Failed', err);
    } finally {
      setLoading(false);
    }
  };
  return (
    <>
      <div className={styles.login}>
        <h1>忘記密碼</h1>
        <AppInput
          placeholder="電子信箱"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <AppButton loading={loading} onClick={handleRegister}>
          重置密碼
        </AppButton>
      </div>
    </>
  );
};

export default ForgetPage;
