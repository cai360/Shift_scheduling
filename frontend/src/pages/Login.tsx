import AppInput from '../components/ui/AppInput'
import AppButton from '../components/ui/AppButton'
import AppPasswordInput from '../components/ui/AppPasswordInout'
import styles from './Login.module.css'
import { login } from '../services/auth.api'
import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

const LoginPage = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const role = searchParams.get('role')


    const handleLogin = async () => {
        try {
            setLoading(true)
            console.log(email, password)
            const res = await login({
                email,
                password,
            })

            const { access_token, refresh_token } = res.data
            localStorage.setItem('token', access_token)
            localStorage.setItem('refresh_token', refresh_token)

            navigate('/home')
            console.log('登入成功', res)
        } catch (err) {
            console.error('登入失敗', err)
        } finally {
            setLoading(false)
        }
    }
    return (
        <>
            <div className={styles.login}>
                <h1>{role === 'company' ? '企業' : '員工'}登入</h1>
                <AppInput placeholder="帳號" value={email} onChange={(e) => setEmail(e.target.value)}/>
                <AppPasswordInput placeholder="密碼" value={password} onChange={(e) => setPassword(e.target.value)}/>
                <AppButton loading={loading} onClick={handleLogin}>登入</AppButton>
            </div>
        </>
    )
}

export default LoginPage
