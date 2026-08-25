import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { useAuthContext } from '../contexts/useAuthContext';
import { updateMe } from '../services/user.api';
import { isValidEmail } from '../utils/validators';
import AppInput from '../components/ui/AppInput';
import AppButton from '../components/ui/AppButton';
import styles from './EditProfilePage.module.css';

const EditProfilePage = () => {
  const { user, restoreUser } = useAuthContext();
  const navigate = useNavigate();
  const [username, setUsername] = useState(user?.username ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [loading, setLoading] = useState(false);
  const isUnchanged = username === user?.username && email === user?.email;

  useEffect(() => {
    setUsername(user?.username ?? '');
    setEmail(user?.email ?? '');
  }, [user]);

  const handleSubmit = async () => {
    if (!username.trim()) {
      message.error('用戶名稱不能為空');
      return;
    }
    const emailError = isValidEmail(email);
    if (emailError) {
      message.error(emailError);
      return;
    }
    try {
      setLoading(true);
      await updateMe({ username, email });
      await restoreUser();
      message.success('個人資料已更新');
      navigate('/profile');
    } catch {
      message.error('更新失敗，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      className={styles.layout}
      onSubmit={(e) => {
        e.preventDefault();
        handleSubmit();
      }}
    >
      <h2>編輯個人資料</h2>
      <div className={styles.field}>
        <label htmlFor="username" className={styles.label}>
          用戶名稱
        </label>
        <AppInput
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div className={styles.field}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <AppInput
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div className={styles.actions}>
        <AppButton intent="secondary" onClick={() => navigate('/profile')}>
          取消
        </AppButton>
        <AppButton loading={loading} htmlType="submit" disabled={isUnchanged}>
          儲存
        </AppButton>
      </div>
    </form>
  );
};

export default EditProfilePage;
