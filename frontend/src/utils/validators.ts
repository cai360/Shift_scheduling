export const isValidEmail = (email: string): string | null =>
  /\S+@\S+\.\S+/.test(email) ? null : 'Email 格式錯誤';

export const isPasswordMatch = (
  password: string,
  confirmPassword: string,
): boolean => {
  return password === confirmPassword;
};

export const validateLogin = ({
  email,
  password,
}: {
  email: string;
  password: string;
}): string | null => {
  const emailError = isValidEmail(email);
  if (emailError) return emailError;

  if (!password) return '請輸入密碼';

  return null;
};

export const validateRegister = ({
  email,
  password,
  confirmPassword,
}: {
  email: string;
  password: string;
  confirmPassword: string;
}): string | null => {
  const emailError = isValidEmail(email);
  if (emailError) return emailError;

  if (!isPasswordMatch(password, confirmPassword)) return '兩次密碼不一致';

  return null;
};
