const ENV = import.meta.env.MODE

export const config = {
    isDev: ENV === 'development',
    apiBaseUrl:
        ENV === 'development'
            ? 'http://localhost:5050'
            : 'https://shift-scheduling-system.com',
}