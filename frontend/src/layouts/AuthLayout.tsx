import { Outlet } from 'react-router-dom';
import styles from './AuthLayout.module.css';
import Footer from '../components/layout/Footer';

const AuthLayout = () => {
  return (
    <div className={styles.layout}>
      <main className={styles.main}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default AuthLayout;
