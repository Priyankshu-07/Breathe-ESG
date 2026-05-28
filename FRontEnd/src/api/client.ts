import { API_BASE } from '../contexts/AuthContext';

export function getHeaders(token: string | null) {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Token ${token}` } : {}),
  };
}

export async function apiFetch(
  path: string,
  token: string | null,
  options: RequestInit = {}
) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...getHeaders(token),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401) {
    localStorage.removeItem('breathe_token');
    localStorage.removeItem('breathe_user');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  return response;
}