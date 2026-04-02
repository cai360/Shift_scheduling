import { Outlet } from 'react-router-dom';
import styles from './AuthLayout.module.css';

const AuthLayout = () => {
  return (
    <div className={styles.layout}>
      <main className={`${styles.main} ${styles.emptyMain}`}>
        <Outlet />
      </main>
    </div>
  );
};
export default AuthLayout;
