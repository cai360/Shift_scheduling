import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/useAuthContext';
import styles from './UserMenu.module.css';

const UserMenu = () => {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuthContext();
  const navigate = useNavigate();
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const go = (path: string) => {
    navigate(path);
    setOpen(false);
  };

  const initial = user?.username?.[0]?.toUpperCase() ?? '?';

  return (
    <div className={styles.wrapper} ref={menuRef}>
      <button
        type="button"
        className={styles.avatar}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="user-menu"
      >
        {initial}
      </button>
      {open && (
        <div id="user-menu" className={styles.menu}>
          <div className={styles.menuHeader}>
            <div className={styles.menuName}>{user?.username}</div>
            <div className={styles.menuEmail}>{user?.email}</div>
          </div>
          <div className={styles.divider} />
          <button className={styles.item} onClick={() => go('/profile')}>
            個人資料
          </button>
          <button className={styles.item} onClick={() => go('/profile/edit')}>
            編輯個人資料
          </button>
          <button
            className={styles.item}
            onClick={() => go('/account-settings')}
          >
            帳號設定
          </button>
          <div className={styles.divider} />
          <button
            className={`${styles.item} ${styles.danger}`}
            onClick={handleLogout}
          >
            登出
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
