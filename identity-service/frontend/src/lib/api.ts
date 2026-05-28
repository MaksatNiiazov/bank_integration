import type { Branch, CurrentUser, Department, Role, ServiceApp, User } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const TOKEN_KEY = 'identity_access_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function requestJson<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401) clearToken();
    throw new Error(data?.detail || data?.message || `HTTP ${response.status}`);
  }
  return data as T;
}

export async function login(email: string, password: string): Promise<void> {
  const data = await requestJson<{ access_token: string }>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
}

export function fetchMe(): Promise<CurrentUser> {
  return requestJson<CurrentUser>('/api/v1/auth/me');
}

export function fetchUsers(): Promise<User[]> {
  return requestJson<User[]>('/api/v1/users');
}

export function fetchRoles(): Promise<Role[]> {
  return requestJson<Role[]>('/api/v1/roles');
}

export function fetchBranches(): Promise<Branch[]> {
  return requestJson<Branch[]>('/api/v1/branches');
}

export function fetchDepartments(): Promise<Department[]> {
  return requestJson<Department[]>('/api/v1/departments');
}

export function fetchServices(): Promise<ServiceApp[]> {
  return requestJson<ServiceApp[]>('/api/v1/services');
}

export function createUser(payload: {
  email: string;
  password: string;
  full_name: string;
  department_code?: string;
}): Promise<User> {
  return requestJson<User>('/api/v1/users', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function assignRole(
  userId: number,
  payload: { role_code: string; branch_code?: string; department_code?: string },
): Promise<User> {
  return requestJson<User>(`/api/v1/users/${userId}/role-assignments`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateUserStatus(userId: number, isActive: boolean): Promise<User> {
  return requestJson<User>(`/api/v1/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  });
}
