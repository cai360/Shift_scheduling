import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true, // Flask session / cookie will be used
});

let refreshPromise: Promise<string> | null = null;
let onUnauthorized: (() => void) | null = null;

export const setUnauthorizedHandler = (handler: () => void) => {
  onUnauthorized = handler;
};

const clearAuthTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

const refreshAccessToken = async (): Promise<string> => {
  const refreshToken = localStorage.getItem('refresh_token');

  if (!refreshToken) {
    throw new Error('No refresh token found');
  }

  const response = await axios.post(
    `${API_BASE_URL}/auth/refresh`,
    { refresh_token: refreshToken },
    { withCredentials: true },
  );

  const { access_token } = response.data.data;

  if (!access_token) {
    throw new Error('No access token returned from refresh API');
  }

  localStorage.setItem('access_token', access_token);

  return access_token;
};

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error),
);

http.interceptors.response.use(
  (response) => {
    // only handle success
    return response;
  },
  async (error) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const status = error.response?.status;

    if (!originalRequest) {
      return Promise.reject(error);
    }

    const isRefreshRequest = originalRequest.url?.includes('/auth/refresh');
    if (status === 401 && !originalRequest._retry && !isRefreshRequest) {
      originalRequest._retry = true;

      try {
        if (!refreshPromise) {
          refreshPromise = refreshAccessToken().finally(() => {
            refreshPromise = null;
          });
        }

        const newAccessToken = await refreshPromise;

        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        return http(originalRequest);
      } catch (refreshError) {
        clearAuthTokens();
        onUnauthorized?.();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default http;
