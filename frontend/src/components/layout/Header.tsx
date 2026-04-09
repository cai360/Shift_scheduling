import CompanySwitcher from './CompanySwitcher';
import styles from './Header.module.css';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const navigate = useNavigate();
  return (
    <header>
      <div className={styles.layout}>
        <div className={styles.logo} onClick={() => navigate('/home')}>
          排班管理系統
        </div>

        <div className={styles.right}>
          <CompanySwitcher />
          <div className={styles.profile}>
            <img src="https://picsum.photos/300/200/?random=10" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
