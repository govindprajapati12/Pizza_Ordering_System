const BASE_URL = 'http://localhost:8000';

export const refreshTokenApi = (refresh_token: string) => {
  return fetch(`${BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token }),
  });
};

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No access token');
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    try {
      const { access_token } = await refreshToken();
      
      // Retry the original request with new token
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${access_token}`,
        },
      });
    } catch (error) {
      throw new Error('Authentication failed');
    }
  }

  return response;
};