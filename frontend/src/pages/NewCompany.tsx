import { useState } from 'react';
import { message } from 'antd';
import styles from './NewCompany.module.css';
import AppInput from '../components/ui/AppInput';
// import AppPasswordInput from '../components/ui/AppPasswordInout';
import AppButton from '../components/ui/AppButton';
import { useNavigate } from 'react-router-dom';
import { createCompany, joinCompany } from '../services/auth.api';

type Mode = 'create' | 'join' | null;

const NewCompanyPage = () => {
  const [mode, setMode] = useState<Mode>(null);
  const [name, setName] = useState('');
  const [companyId, setCompanyId] = useState('');
  const [description, setDescription] = useState('');
  // const [email, setEmail] = useState('');
  // const [password, setPassword] = useState('');
  // const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleBackgroundClick = () => {
    setMode(null);
  };

  const create = async () => {
    // TODO: input empty validation
    try {
      setLoading(true);

      const res = await createCompany({
        name,
        description,
      });

      message.success(`公司建立成功：${res.data.name}`);
      navigate('/home');
    } catch (err) {
      message.error(`公司建立失敗 ${err}`);
      console.error('Create Failed', err);
    } finally {
      setLoading(false);
    }
  };

  const join = async () => {
    // TODO: input empty validation
    try {
      setLoading(true);

      const res = await joinCompany(companyId);

      message.success(`加入公司成功：${res.data.company_id}`);
      navigate('/home');
    } catch (err) {
      message.error(`加入公司失敗 ${err}`);
      console.error('Join Failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.layout} onClick={handleBackgroundClick}>
      <div className={styles.cardContainer}>
        <div
          className={`${styles.card} ${
            mode === 'create' ? styles.activeCard : ''
          } ${mode === 'join' ? styles.fadeOut : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            setMode('create');
          }}
        >
          <img src="https://picsum.photos/300/200/?random=10" />
          <p>創建企業</p>
        </div>

        <div
          className={`${styles.card} ${
            mode === 'join' ? `${styles.activeCard} ${styles.join}` : ''
          } ${mode === 'create' ? styles.fadeOut : ''}`}
          onClick={(e) => {
            e.stopPropagation();
            setMode('join');
          }}
        >
          <img src="https://picsum.photos/300/200/?random=11" />
          <p>加入企業</p>
        </div>
      </div>

      <div
        className={`${styles.inputSection} ${mode ? styles.showInput : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        {mode === 'create' && (
          <>
            <AppInput
              placeholder="公司名稱"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <AppInput
              placeholder="公司描述"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <div className={styles.button}>
              <AppButton
                className={styles.back}
                onClick={handleBackgroundClick}
              >
                返回
              </AppButton>
              <AppButton intent="primary" loading={loading} onClick={create}>
                創建
              </AppButton>
            </div>
          </>
        )}

        {mode === 'join' && (
          <>
            <AppInput
              placeholder="公司ID"
              value={companyId}
              onChange={(e) => setCompanyId(e.target.value)}
            />
            <div className={styles.button}>
              <AppButton
                className={styles.back}
                onClick={handleBackgroundClick}
              >
                返回
              </AppButton>
              <AppButton intent="primary" loading={loading} onClick={join}>
                加入
              </AppButton>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NewCompanyPage;
