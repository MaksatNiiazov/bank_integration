import { useEffect, useMemo, useState } from 'react';
import { StatusDot } from './components/StatusDot';
import { fetchDashboard } from './lib/api';
import type { DashboardResponse, ServiceHealth } from './lib/types';

type IconName =
  | 'activity'
  | 'arrow'
  | 'building'
  | 'card'
  | 'database'
  | 'dashboard'
  | 'refresh'
  | 'shield'
  | 'sliders'
  | 'users';

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const common = {
    fill: 'none',
    stroke: 'currentColor',
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    strokeWidth: 2,
  };
  const paths: Record<IconName, React.ReactNode> = {
    activity: <path d="M4 12h4l2-6 4 12 2-6h4" />,
    arrow: (
      <>
        <path d="M7 17 17 7" />
        <path d="M9 7h8v8" />
      </>
    ),
    building: (
      <>
        <path d="M5 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16" />
        <path d="M3 21h18" />
        <path d="M9 7h1M14 7h1M9 11h1M14 11h1M9 15h1M14 15h1" />
      </>
    ),
    card: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="M3 10h18" />
      </>
    ),
    database: (
      <>
        <ellipse cx="12" cy="5" rx="8" ry="3" />
        <path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
        <path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" />
      </>
    ),
    dashboard: (
      <>
        <rect x="3" y="3" width="7" height="8" rx="1" />
        <rect x="14" y="3" width="7" height="5" rx="1" />
        <rect x="14" y="12" width="7" height="9" rx="1" />
        <rect x="3" y="15" width="7" height="6" rx="1" />
      </>
    ),
    refresh: (
      <>
        <path d="M20 12a8 8 0 0 1-13.7 5.7" />
        <path d="M4 12A8 8 0 0 1 17.7 6.3" />
        <path d="M7 18H4v-3" />
        <path d="M17 6h3v3" />
      </>
    ),
    shield: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />,
    sliders: (
      <>
        <path d="M4 7h8M16 7h4M4 17h4M12 17h8" />
        <circle cx="14" cy="7" r="2" />
        <circle cx="10" cy="17" r="2" />
      </>
    ),
    users: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
        <circle cx="9.5" cy="7" r="4" />
        <path d="M17 11a3 3 0 0 0 0-6" />
        <path d="M21 21v-2a4 4 0 0 0-3-3.8" />
      </>
    ),
  };
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" {...common}>
      {paths[name]}
    </svg>
  );
}

const fallbackDashboard: DashboardResponse = {
  generated_at: new Date().toISOString(),
  services: [
    {
      code: 'identity',
      name: 'Identity',
      department: 'Platform',
      description: 'Users, roles, branches, permissions',
      status: 'unknown',
      base_url: 'http://localhost:8020',
      launch_url: 'http://localhost:8020/docs',
      required_permission: 'identity.users.read',
      checked_at: new Date().toISOString(),
      latency_ms: null,
      error: 'Platform API is not connected',
    },
  ],
  departments: [
    {
      department: 'Platform',
      services_total: 1,
      services_ok: 0,
      services_unavailable: 0,
      status: 'unknown',
    },
  ],
  activity: [
    {
      id: 'fallback',
      title: 'Platform API пока недоступен',
      service_code: 'platform',
      tone: 'warning',
      created_at: new Date().toISOString(),
    },
  ],
};

function AppShell({ children, onRefresh }: { children: React.ReactNode; onRefresh: () => void }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/">
          <span className="brand-mark">T</span>
          <span>
            <strong>Turkuaz Platform</strong>
            <small>Company operations</small>
          </span>
        </a>

        <nav className="nav-list" aria-label="Platform navigation">
          <a className="nav-link nav-link-active" href="#overview">
            <Icon name="dashboard" />
            Обзор
          </a>
          <a className="nav-link" href="#services">
            <Icon name="database" />
            Сервисы
          </a>
          <a className="nav-link" href="#departments">
            <Icon name="building" />
            Отделы
          </a>
          <a className="nav-link" href="#admin">
            <Icon name="shield" />
            Администрирование
          </a>
        </nav>

        <div className="sidebar-footer">
          <span>Среда</span>
          <strong>Development</strong>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <h1>Центральный портал</h1>
            <p>Единая витрина отделов, сервисов и административного доступа.</p>
          </div>
          <div className="topbar-actions">
            <select aria-label="Филиал" className="branch-select" defaultValue="all">
              <option value="all">Все филиалы</option>
              <option value="head_office">Head Office</option>
              <option value="bishkek">Бишкек</option>
            </select>
            <button className="icon-button" type="button" onClick={onRefresh} title="Обновить">
              <Icon name="refresh" />
            </button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}

export function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse>(fallbackDashboard);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadDashboard() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchDashboard();
      setDashboard(data);
    } catch (err) {
      setDashboard(fallbackDashboard);
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  const metrics = useMemo(() => {
    const total = dashboard.services.length;
    const online = dashboard.services.filter((service) => service.status === 'ok').length;
    const unavailable = dashboard.services.filter((service) => service.status === 'unavailable').length;
    const departments = new Set(dashboard.services.map((service) => service.department)).size;
    return [
      { label: 'Сервисы', value: total, icon: 'database' as const },
      { label: 'Работают', value: online, icon: 'shield' as const },
      { label: 'Недоступны', value: unavailable, icon: 'activity' as const },
      { label: 'Отделы', value: departments, icon: 'building' as const },
    ];
  }, [dashboard.services]);

  return (
    <AppShell onRefresh={() => void loadDashboard()}>
      {error ? <div className="notice">Platform API: {error}. Показано резервное состояние.</div> : null}

      <section className="metrics-grid" id="overview" aria-label="Ключевые показатели">
        {metrics.map((metric) => (
          <div className="metric" key={metric.label}>
            <Icon name={metric.icon} size={20} />
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
          </div>
        ))}
      </section>

      <section className="content-grid">
        <div className="panel services-panel" id="services">
          <div className="panel-header">
            <div>
              <h2>Сервисы компании</h2>
              <p>{loading ? 'Обновляем статусы...' : 'Модули работают независимо друг от друга.'}</p>
            </div>
          </div>
          <div className="service-list">
            {dashboard.services.map((service) => (
              <ServiceRow service={service} key={service.code} />
            ))}
          </div>
        </div>

        <div className="side-stack">
          <section className="panel" id="departments">
            <div className="panel-header compact">
              <h2>Отделы</h2>
            </div>
            <div className="department-list">
              {dashboard.departments.map((department) => (
                <div className="department-row" key={department.department}>
                  <div>
                    <strong>{department.department}</strong>
                    <span>
                      {department.services_ok}/{department.services_total} работают
                    </span>
                  </div>
                  <StatusDot status={department.status} />
                </div>
              ))}
            </div>
          </section>

          <section className="panel" id="admin">
            <div className="panel-header compact">
              <h2>Администрирование</h2>
            </div>
            <div className="quick-actions">
              <button type="button">
                <Icon name="users" size={17} />
                Пользователи
              </button>
              <button type="button">
                <Icon name="sliders" size={17} />
                Роли и права
              </button>
              <button type="button">
                <Icon name="building" size={17} />
                Филиалы
              </button>
              <button type="button">
                <Icon name="card" size={17} />
                Доступы сервисов
              </button>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header compact">
              <h2>Активность</h2>
            </div>
            <div className="activity-list">
              {dashboard.activity.map((item) => (
                <div className={`activity-item activity-${item.tone}`} key={item.id}>
                  <span />
                  <p>{item.title}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </AppShell>
  );
}

function ServiceRow({ service }: { service: ServiceHealth }) {
  return (
    <article className="service-row">
      <div className="service-icon">{service.code.slice(0, 2).toUpperCase()}</div>
      <div className="service-main">
        <div className="service-title">
          <h3>{service.name}</h3>
          <StatusDot status={service.status} />
        </div>
        <p>{service.description || service.department}</p>
        <div className="service-meta">
          <span>{service.department}</span>
          <span>{service.required_permission || 'permission not set'}</span>
          <span>{service.latency_ms === null ? 'no latency' : `${service.latency_ms} ms`}</span>
        </div>
      </div>
      {service.launch_url ? (
        <a className="open-link" href={service.launch_url} target="_blank" rel="noreferrer">
          Открыть
          <Icon name="arrow" size={16} />
        </a>
      ) : null}
    </article>
  );
}
