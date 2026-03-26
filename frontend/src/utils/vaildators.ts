
export const isValidEmail = (email: string): boolean => {
    return /\S+@\S+\.\S+/.test(email);
};
  

export const isPasswordMatch = ( password: string, confirmPassword: string ): boolean => {
    return password === confirmPassword;
};
  
export const validateLogin = ({
    email,
    password,
  }: {
    email: string;
    password: string;
  }): string | null => {
    if (!isValidEmail(email)) {
        return 'Email 格式錯誤';
    }

    if (!password) {
        return '請輸入密碼';
    }  
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
    if (!isValidEmail(email)) {
        return 'Email 格式錯誤';
    }

    if (!isPasswordMatch(password, confirmPassword)) {
        return '兩次密碼不一致';
    }

    return null;
};