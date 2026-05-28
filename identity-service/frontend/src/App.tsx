import { FormEvent, useEffect, useMemo, useState } from 'react';
import { AppShell, Icon } from '@turkuaz/ui';
import {
  assignRole,
  clearToken,
  createUser,
  fetchBranches,
  fetchDepartments,
  fetchMe,
  fetchRoles,
  fetchServices,
  fetchUsers,
  getToken,
  login,
  updateUserStatus,
} from './lib/api';
import type { Branch, CurrentUser, Department, Role, ServiceApp, User } from './lib/types';

type LoadState = {
  loading: boolean;
  error: string | null;
};

type DashboardData = {
  me: CurrentUser | null;
  users: User[];
  roles: Role[];
  branches: Branch[];
  departments: Department[];
  services: ServiceApp[];
};

const emptyData: DashboardData = {
  me: null,
  users: [],
  roles: [],
  branches: [],
  departments: [],
  services: [],
};

export function App() {
  const [tokenPresent, setTokenPresent] = useState(() => Boolean(getToken()));
  const [data, setData] = useState<DashboardData>(emptyData);
  const [state, setState] = useState<LoadState>({ loading: false, error: null });
  const [query, setQuery] = useState('');
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);

  async function loadData() {
    if (!getToken()) {
      setTokenPresent(false);
      return;
    }
    setState({ loading: true, error: null });
    try {
      const [me, users, roles, branches, departments, services] = await Promise.all([
        fetchMe(),
        fetchUsers(),
        fetchRoles(),
        fetchBranches(),
        fetchDepartments(),
        fetchServices(),
      ]);
      setData({ me, users, roles, branches, departments, services });
      setSelectedUserId((current) =>
        users.some((user) => user.id === current) ? current : users[0]?.id ?? null,
      );
      setTokenPresent(true);
      setState({ loading: false, error: null });
    } catch (error) {
      setState({ loading: false, error: error instanceof Error ? error.message : String(error) });
      if (!getToken()) setTokenPresent(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  function logout() {
    clearToken();
    setTokenPresent(false);
    setData(emptyData);
  }

  if (!tokenPresent) {
    return <LoginScreen onLoggedIn={() => void loadData()} />;
  }

  const filteredUsers = data.users.filter((user) => {
    const value = `${user.email} ${user.full_name} ${user.department_code || ''}`.toLowerCase();
    return value.includes(query.trim().toLowerCase());
  });
  const selectedUser = data.users.find((user) => user.id === selectedUserId) ?? data.users[0] ?? null;

  const metrics = [
    { label: 'Пользователи', value: data.users.length, icon: 'users' as const },
    { label: 'Активные', value: data.users.filter((user) => user.is_active).length, icon: 'shield' as const },
    { label: 'Роли', value: data.roles.length, icon: 'key' as const },
    { label: 'Филиалы', value: data.branches.length, icon: 'building' as const },
  ];

  const navItems = [
    {
      key: 'users',
      label: 'Пользователи',
      icon: 'users' as const,
      active: true,
      onClick: () => {
        window.location.hash = 'users';
      },
    },
    {
      key: 'roles',
      label: 'Роли',
      icon: 'key' as const,
      active: false,
      onClick: () => {
        window.location.hash = 'roles';
      },
    },
    {
      key: 'branches',
      label: 'Филиалы',
      icon: 'building' as const,
      active: false,
      onClick: () => {
        window.location.hash = 'branches';
      },
    },
    {
      key: 'services',
      label: 'Сервисы',
      icon: 'database' as const,
      active: false,
      onClick: () => {
        window.location.hash = 'services';
      },
    },
  ];

  return (
    <AppShell
      brand={{
        href: 'http://localhost:5174',
        mark: 'T',
        title: 'Turkuaz Identity',
        subtitle: data.me?.email || 'Users and access',
      }}
      navItems={navItems}
      sideLinks={[
        { href: 'http://localhost:5174', label: 'Platform', icon: 'building' },
        { href: 'http://localhost:6750', label: 'Payments', icon: 'banknote' },
        { href: '/docs', label: 'Swagger', icon: 'file' },
      ]}
      storageKey="turkuaz-identity-shell"
    >
        <header className="topbar">
          <div>
            <h1>Пользователи и доступы</h1>
            <p>Единая настройка сотрудников, ролей, филиалов и прав платформы.</p>
          </div>
          <div className="topbar-actions">
            <select className="branch-select" aria-label="Филиал" defaultValue="all">
              <option value="all">Все филиалы</option>
              {data.branches.map((branch) => (
                <option value={branch.code} key={branch.code}>
                  {branch.name}
                </option>
              ))}
            </select>
            <button className="icon-button" type="button" onClick={() => void loadData()} title="Обновить">
              <Icon name="refresh" />
            </button>
            <button className="icon-button" type="button" onClick={logout} title="Выйти">
              <Icon name="logout" />
            </button>
          </div>
        </header>

        {state.error ? <div className="notice">Identity API: {state.error}</div> : null}

        <section className="metrics-grid" aria-label="Identity metrics">
          {metrics.map((metric) => (
            <div className="metric" key={metric.label}>
              <Icon name={metric.icon} size={20} />
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </div>
          ))}
        </section>

        <section className="content-grid">
          <div className="panel user-panel" id="users">
            <div className="panel-header">
              <div>
                <h2>Пользователи</h2>
                <p>{state.loading ? 'Обновляем список...' : 'Сотрудники и их доступы по платформе.'}</p>
              </div>
              <label className="search-box">
                <Icon name="search" size={16} />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Поиск пользователя"
                />
              </label>
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Отдел</th>
                    <th>Роли</th>
                    <th>Филиалы</th>
                    <th>Статус</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user) => (
                    <tr
                      className={selectedUser?.id === user.id ? 'selected-row' : ''}
                      key={user.id}
                      onClick={() => setSelectedUserId(user.id)}
                    >
                      <td>
                        <div className="user-cell">
                          <span>{initials(user.full_name)}</span>
                          <div>
                            <strong>{user.full_name}</strong>
                            <small>{user.email}</small>
                          </div>
                        </div>
                      </td>
                      <td>{user.department_code || '-'}</td>
                      <td>
                        <BadgeList values={unique(user.role_assignments.map((item) => item.role_code))} />
                      </td>
                      <td>
                        <BadgeList
                          values={unique(user.role_assignments.map((item) => item.branch_code || 'global'))}
                        />
                      </td>
                      <td>
                        <span className={user.is_active ? 'status good' : 'status bad'}>
                          {user.is_active ? 'Активен' : 'Заблокирован'}
                        </span>
                      </td>
                      <td>
                        <button
                          className="text-button"
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            void updateUserStatus(user.id, !user.is_active).then(loadData);
                          }}
                        >
                          {user.is_active ? 'Блок' : 'Актив'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredUsers.length === 0 ? <div className="empty-state">Пользователи не найдены</div> : null}
            </div>
          </div>

          <div className="side-stack">
            <CreateUserPanel departments={data.departments} onCreated={() => void loadData()} />
            <AssignRolePanel
              user={selectedUser}
              roles={data.roles}
              branches={data.branches}
              departments={data.departments}
              onAssigned={() => void loadData()}
            />
            <DirectoryPanel data={data} />
          </div>
        </section>
    </AppShell>
  );
}

function LoginScreen({ onLoggedIn }: { onLoggedIn: () => void }) {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('admin123');
  const [state, setState] = useState<LoadState>({ loading: false, error: null });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setState({ loading: true, error: null });
    try {
      await login(email, password);
      onLoggedIn();
    } catch (error) {
      setState({ loading: false, error: error instanceof Error ? error.message : String(error) });
    }
  }

  return (
    <main className="login-shell">
      <form className="login-panel" onSubmit={(event) => void submit(event)}>
        <span className="brand-mark">T</span>
        <h1>Turkuaz Identity</h1>
        <p>Вход в управление пользователями, ролями и филиалами.</p>
        {state.error ? <div className="notice compact-notice">{state.error}</div> : null}
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" />
        </label>
        <label>
          Пароль
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" />
        </label>
        <button className="primary-button" disabled={state.loading} type="submit">
          {state.loading ? 'Входим...' : 'Войти'}
        </button>
      </form>
    </main>
  );
}

function CreateUserPanel({
  departments,
  onCreated,
}: {
  departments: Department[];
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    department_code: '',
  });
  const [state, setState] = useState<LoadState>({ loading: false, error: null });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setState({ loading: true, error: null });
    try {
      await createUser({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        department_code: form.department_code || undefined,
      });
      setForm({ email: '', password: '', full_name: '', department_code: '' });
      setState({ loading: false, error: null });
      onCreated();
    } catch (error) {
      setState({ loading: false, error: error instanceof Error ? error.message : String(error) });
    }
  }

  return (
    <section className="panel form-panel">
      <div className="panel-header compact">
        <h2>Создать пользователя</h2>
      </div>
      <form className="form-grid" onSubmit={(event) => void submit(event)}>
        {state.error ? <div className="notice compact-notice">{state.error}</div> : null}
        <label>
          ФИО
          <input
            required
            value={form.full_name}
            onChange={(event) => setForm({ ...form, full_name: event.target.value })}
          />
        </label>
        <label>
          Email
          <input
            required
            type="email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
        </label>
        <label>
          Пароль
          <input
            required
            minLength={6}
            type="password"
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </label>
        <label>
          Отдел
          <select
            value={form.department_code}
            onChange={(event) => setForm({ ...form, department_code: event.target.value })}
          >
            <option value="">Без отдела</option>
            {departments.map((department) => (
              <option value={department.code} key={department.code}>
                {department.name}
              </option>
            ))}
          </select>
        </label>
        <button className="primary-button" disabled={state.loading} type="submit">
          <Icon name="plus" size={16} />
          {state.loading ? 'Создаем...' : 'Создать'}
        </button>
      </form>
    </section>
  );
}

function AssignRolePanel({
  user,
  roles,
  branches,
  departments,
  onAssigned,
}: {
  user: User | null;
  roles: Role[];
  branches: Branch[];
  departments: Department[];
  onAssigned: () => void;
}) {
  const [roleCode, setRoleCode] = useState('');
  const [branchCode, setBranchCode] = useState('');
  const [departmentCode, setDepartmentCode] = useState('');
  const [state, setState] = useState<LoadState>({ loading: false, error: null });

  useEffect(() => {
    setRoleCode((current) => current || roles[0]?.code || '');
  }, [roles]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!user || !roleCode) return;
    setState({ loading: true, error: null });
    try {
      await assignRole(user.id, {
        role_code: roleCode,
        branch_code: branchCode || undefined,
        department_code: departmentCode || undefined,
      });
      setState({ loading: false, error: null });
      onAssigned();
    } catch (error) {
      setState({ loading: false, error: error instanceof Error ? error.message : String(error) });
    }
  }

  return (
    <section className="panel form-panel">
      <div className="panel-header compact">
        <h2>Назначить роль</h2>
      </div>
      {user ? (
        <form className="form-grid" onSubmit={(event) => void submit(event)}>
          <div className="selected-user">
            <strong>{user.full_name}</strong>
            <span>{user.email}</span>
          </div>
          {state.error ? <div className="notice compact-notice">{state.error}</div> : null}
          <label>
            Роль
            <select value={roleCode} onChange={(event) => setRoleCode(event.target.value)}>
              {roles.map((role) => (
                <option value={role.code} key={role.code}>
                  {role.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Филиал
            <select value={branchCode} onChange={(event) => setBranchCode(event.target.value)}>
              <option value="">Глобально</option>
              {branches.map((branch) => (
                <option value={branch.code} key={branch.code}>
                  {branch.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Отдел
            <select value={departmentCode} onChange={(event) => setDepartmentCode(event.target.value)}>
              <option value="">Без привязки</option>
              {departments.map((department) => (
                <option value={department.code} key={department.code}>
                  {department.name}
                </option>
              ))}
            </select>
          </label>
          <button className="primary-button" disabled={state.loading || !roleCode} type="submit">
            <Icon name="key" size={16} />
            {state.loading ? 'Назначаем...' : 'Назначить'}
          </button>
        </form>
      ) : (
        <div className="empty-state">Выберите пользователя</div>
      )}
    </section>
  );
}

function DirectoryPanel({ data }: { data: DashboardData }) {
  return (
    <section className="panel directory-panel">
      <div className="panel-header compact">
        <h2>Справочники доступа</h2>
      </div>
      <div className="directory-list" id="roles">
        <DirectoryRow label="Роли" value={data.roles.length} />
        <DirectoryRow label="Филиалы" value={data.branches.length} id="branches" />
        <DirectoryRow label="Отделы" value={data.departments.length} />
        <DirectoryRow label="Сервисы" value={data.services.length} id="services" />
      </div>
    </section>
  );
}

function DirectoryRow({ label, value, id }: { label: string; value: number; id?: string }) {
  return (
    <div className="directory-row" id={id}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function BadgeList({ values }: { values: string[] }) {
  if (values.length === 0) return <span className="muted-text">-</span>;
  return (
    <div className="badge-list">
      {values.slice(0, 3).map((value) => (
        <span className="badge" key={value}>
          {value}
        </span>
      ))}
      {values.length > 3 ? <span className="badge">+{values.length - 3}</span> : null}
    </div>
  );
}

function unique(values: (string | null)[]): string[] {
  return Array.from(new Set(values.filter(Boolean) as string[]));
}

function initials(value: string): string {
  return value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('');
}
