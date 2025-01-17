import { refreshTokenApi } from './api';

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

let refreshPromise: Promise<TokenResponse> | null = null;

export const refreshToken = async (): Promise<TokenResponse> => {
  try {
    // If there's already a refresh in progress, return that promise
    if (refreshPromise) {
      return refreshPromise;
    }

    // Create new refresh promise
    refreshPromise = (async () => {
      const refresh_token = localStorage.getItem('refresh_token');
      if (!refresh_token) {
        throw new Error('No refresh token available');
      }

      const response = await refreshTokenApi(refresh_token);
      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return data;
      } else {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        throw new Error('Failed to refresh token');
      }
    })();

    const result = await refreshPromise;
    refreshPromise = null;
    return result;
  } catch (error) {
    refreshPromise = null;
    throw error;
  }
};