const API_BASE =
  import.meta.env.VITE_API_BASE ??
  'https://breathe-esg-hw2p.onrender.com';

export { API_BASE };

export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });

  return response;
}