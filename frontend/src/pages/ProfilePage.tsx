import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts/useAuthContext';
import AppButton from '../components/ui/AppButton';
import styles from './ProfilePage.module.css';

const ProfilePage = () => {
  const { user } = useAuthContext();
  const navigate = useNavigate();

  return (
    <div className={styles.layout}>
      <h2>個人資料</h2>
      <div className={styles.avatar}>{user?.username?.[0]?.toUpperCase()}</div>
      <div className={styles.field}>
        <span className={styles.label}>用戶名稱</span>
        <span className={styles.value}>{user?.username}</span>
      </div>
      <div className={styles.field}>
        <span className={styles.label}>Email</span>
        <span className={styles.value}>{user?.email}</span>
      </div>
      <AppButton intent="secondary" onClick={() => navigate('/profile/edit')}>
        編輯個人資料
      </AppButton>
    </div>
  );
};

export default ProfilePage;
