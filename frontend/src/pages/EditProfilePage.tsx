import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message } from 'antd';
import { useAuthContext } from '../contexts/useAuthContext';
import { updateMe } from '../services/user.api';
import AppInput from '../components/ui/AppInput';
import AppButton from '../components/ui/AppButton';
import styles from './EditProfilePage.module.css';

const EditProfilePage = () => {
  const { user, restoreUser } = useAuthContext();
  const navigate = useNavigate();
  const [username, setUsername] = useState(user?.username ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
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
    <div className={styles.layout}>
      <h2>編輯個人資料</h2>
      <div className={styles.field}>
        <label className={styles.label}>用戶名稱</label>
        <AppInput
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div className={styles.field}>
        <label className={styles.label}>Email</label>
        <AppInput value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>
      <div className={styles.actions}>
        <AppButton intent="secondary" onClick={() => navigate('/profile')}>
          取消
        </AppButton>
        <AppButton loading={loading} onClick={handleSubmit}>
          儲存
        </AppButton>
      </div>
    </div>
  );
};

export default EditProfilePage;
