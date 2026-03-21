import { Input, type InputProps } from 'antd';

const AppPasswordInput = (props: InputProps) => {
  return <Input.Password {...props} />;
};

export default AppPasswordInput;

// export const AppConfirmPasswordInput = (props: InputProps) => {
//   return <Input.Password {...props} />;
// };
