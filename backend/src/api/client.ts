// Normalize the base URL to ensure it includes /api so builds that set
// VITE_API_BASE_URL without the /api suffix still call the correct backend
// path. We intentionally keep the base URL without a trailing slash so
// endpoints (which start with `/`) concatenate cleanly.
const _rawBase = import.meta.env.VITE_API_BASE_URL || 'https://driver-logbook.onrender.com';
let API_BASE_URL = String(_rawBase).replace(/\/+$/, ''); // strip trailing slash(es)
if (!/\/api(\/|$)/.test(API_BASE_URL)) {
  API_BASE_URL = API_BASE_URL + '/api';
}

interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private getAuthToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { requiresAuth = true, ...fetchOptions } = options;

    // Use a Headers object so we can safely set Authorization and keep typing happy
    const headers = new Headers({
      'Content-Type': 'application/json',
      ...(fetchOptions.headers as Record<string, string> | undefined),
    });

    if (requiresAuth) {
      const token = this.getAuthToken();
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      // Try to parse JSON error body, otherwise capture text for debugging
      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        try {
          body = await response.text();
        } catch {
          body = '<unreadable response body>';
        }
      }
  // Log for debugging in dev
  console.error('API request failed', { endpoint, status: response.status, body });

      // Safely extract message from a possible object body
      let message = 'Request failed';
      if (typeof body === 'string') {
        message = body;
      } else if (body && typeof body === 'object') {
        const b = body as Record<string, unknown>;
        if (typeof b.detail === 'string') message = b.detail;
        else if (typeof b.message === 'string') message = b.message;
      }

      throw new Error(message);
    }

    return response.json();
  }

  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new APIClient(API_BASE_URL);
