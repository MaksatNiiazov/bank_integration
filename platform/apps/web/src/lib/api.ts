import type { DashboardResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchDashboard(): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/platform/dashboard`, {
    headers: { Accept: 'application/json' },
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || `HTTP ${response.status}`);
  }
  return data as DashboardResponse;
}
