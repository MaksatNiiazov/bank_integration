export type RoleAssignment = {
  id: number;
  role_code: string;
  branch_code: string | null;
  department_code: string | null;
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  department_code: string | null;
  is_active: boolean;
  created_at: string;
  role_assignments: RoleAssignment[];
};

export type Role = {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_system: boolean;
  is_active: boolean;
  permissions: string[];
};

export type Branch = {
  id: number;
  code: string;
  name: string;
  description: string | null;
  is_active: boolean;
};

export type Department = Branch;

export type ServiceApp = {
  id: number;
  code: string;
  name: string;
  description: string | null;
  base_url: string | null;
  is_active: boolean;
};

export type CurrentUser = {
  id: number;
  active: boolean;
  email: string;
  full_name: string;
  roles: string[];
  permissions: string[];
  branches: string[];
  branch_permissions: Record<string, string[]>;
  department: string | null;
};
