import { Button, type ButtonProps } from 'antd';
import styles from './AppButton.module.css';

type Intent = 'primary' | 'secondary' | 'danger' | 'neutral';

interface AppButtonProps extends ButtonProps {
  intent?: Intent;
  className?: string;
}

const AppButton = ({
  intent = 'primary',
  className,
  ...props
}: AppButtonProps) => {
  return (
    <Button
      size="large"
      className={`${styles[intent]} ${className ?? ''}`}
      {...props}
    />
  );
};
export default AppButton;
