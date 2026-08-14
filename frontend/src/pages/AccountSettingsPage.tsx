import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { message, Modal } from 'antd';
import { useAuthContext } from '../contexts/useAuthContext';
import { updatePassword, deleteMe } from '../services/user.api';
import AppPasswordInput from '../components/ui/AppPasswordInput';
import AppButton from '../components/ui/AppButton';
import styles from './AccountSettingsPage.module.css';

const AccountSettingsPage = () => {
  const { setUser } = useAuthContext();
  const navigate = useNavigate();

  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  const handleChangePassword = async () => {
    if (newPassword.length < 8) {
      message.error('新密碼至少需要 8 個字元');
      return;
    }
    if (newPassword !== confirmPassword) {
      message.error('兩次密碼不一致');
      return;
    }
    try {
      setPasswordLoading(true);
      await updatePassword({
        old_password: oldPassword,
        new_password: newPassword,
      });
      message.success('密碼已更新');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch {
      message.error('密碼更新失敗，請確認舊密碼是否正確');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    Modal.confirm({
      title: '確認刪除帳號',
      content: '此操作無法復原，確定要刪除您的帳號嗎？',
      okText: '確認刪除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        await deleteMe();
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        message.success('帳號已刪除');
        navigate('/login');
      },
    });
  };

  return (
    <div className={styles.layout}>
      <h2>帳號設定</h2>

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>修改密碼</h3>
        <div className={styles.field}>
          <label className={styles.label}>目前密碼</label>
          <AppPasswordInput
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            placeholder="輸入目前密碼"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>新密碼</label>
          <AppPasswordInput
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="至少 8 個字元"
          />
        </div>
        <div className={styles.field}>
          <label className={styles.label}>確認新密碼</label>
          <AppPasswordInput
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="再次輸入新密碼"
          />
        </div>
        <AppButton loading={passwordLoading} onClick={handleChangePassword}>
          更新密碼
        </AppButton>
      </section>

      <div className={styles.divider} />

      <section className={styles.section}>
        <h3 className={`${styles.sectionTitle} ${styles.dangerTitle}`}>
          確認刪除？
        </h3>
        <p className={styles.dangerDesc}>
          刪除帳號後，所有資料將移除且無法復原。
        </p>
        <AppButton intent="danger" onClick={handleDeleteAccount}>
          刪除帳號
        </AppButton>
      </section>
    </div>
  );
};

export default AccountSettingsPage;
