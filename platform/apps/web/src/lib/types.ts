export type ServiceStatus = 'ok' | 'unavailable' | 'unknown';

export type ServiceHealth = {
  code: string;
  name: string;
  department: string;
  description: string | null;
  status: ServiceStatus;
  base_url: string;
  launch_url: string | null;
  required_permission: string | null;
  checked_at: string;
  latency_ms: number | null;
  error: string | null;
};

export type DepartmentSummary = {
  department: string;
  services_total: number;
  services_ok: number;
  services_unavailable: number;
  status: ServiceStatus;
};

export type ActivityItem = {
  id: string;
  title: string;
  service_code: string;
  tone: 'info' | 'success' | 'warning' | 'danger';
  created_at: string;
};

export type DashboardResponse = {
  generated_at: string;
  services: ServiceHealth[];
  departments: DepartmentSummary[];
  activity: ActivityItem[];
};
