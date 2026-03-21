import styles from './Header.module.css';

const Header = () => {
  return (
    <header>
      <div className={styles.layout}>
        <a className={styles.logo} href="/home">
          排班管理系統
        </a>
        <div className={styles.img}>
          <img src="https://picsum.photos/300/200/?random=10" />
        </div>
      </div>
    </header>
  );
};

export default Header;
