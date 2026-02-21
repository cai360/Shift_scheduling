import styles from './Index.module.css'
const IndexPage = () => {
    return (
        <div className={styles.layout}>
            <h1 className={styles.logo}>LOGO</h1>
            <h3 className={styles.title}>Shift Scheduling System</h3>
            <div className={styles.login}>
                <a className={styles.loginItem} href="/login?role=company">
                    <img src="https://picsum.photos/300/200/?random=10" />
                    <p>企業登入</p>
                </a>
                <a className={styles.loginItem} href="/login?role=employee">
                    <img src="https://picsum.photos/300/200/?random=10" />
                    <p>員工登入</p>
                </a>
            </div>
        </div>
    )
}

export default IndexPage