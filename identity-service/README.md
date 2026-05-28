# Turkuaz Identity Service

Central identity service for Turkuaz Platform. It owns users, departments, branches, services, roles, permissions, login, and JWT access tokens.

Other modules should not keep their own human-user auth tables. They should validate Identity JWT tokens and check permissions such as:

```text
converter.orders.read
converter.orders.write
payments.transactions.read
payments.qr.create
identity.users.manage
```

## Quick Start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload
```

Swagger UI:

```text
http://localhost:8020/docs
```

Default local admin:

```text
admin@example.com / admin123
```

## Docker

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8020
```

The users/access frontend will be available at:

```text
http://localhost:5177
```

## Core API

| Method | URL | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/login` | Login and receive JWT |
| `GET` | `/api/v1/auth/me` | Current user, roles, permissions, branches |
| `POST` | `/api/v1/auth/introspect` | Validate a token and return claims |
| `GET` | `/api/v1/users` | List users |
| `POST` | `/api/v1/users` | Create user |
| `PATCH` | `/api/v1/users/{user_id}` | Update user |
| `GET` | `/api/v1/roles` | List roles |
| `POST` | `/api/v1/roles` | Create role |
| `POST` | `/api/v1/users/{user_id}/role-assignments` | Assign scoped role |
| `GET` | `/api/v1/permissions` | List permissions |
| `POST` | `/api/v1/services` | Register platform service/module |
| `POST` | `/api/v1/services/{service_code}/permissions` | Register service permissions |
| `GET` | `/api/v1/branches` | List branches |
| `GET` | `/api/v1/departments` | List departments |

## JWT Claims

Tokens include global and branch-scoped access data:

```json
{
  "sub": "1",
  "email": "admin@example.com",
  "full_name": "Platform Admin",
  "roles": ["platform_admin"],
  "permissions": ["identity.users.manage"],
  "branches": ["bishkek", "osh"],
  "branch_permissions": {
    "bishkek": ["converter.orders.read"]
  }
}
```

Downstream services can validate `Authorization: Bearer <token>` locally with the shared `SECRET_KEY` and `ALGORITHM`, then enforce their own module permissions and `branch_id` checks.

Integration details and a copyable FastAPI dependency live in [docs/INTEGRATION.md](docs/INTEGRATION.md).

## Permission Pattern

Use stable permission codes:

```text
service.resource.action
```

Examples:

```text
converter.orders.read
converter.products.write
payments.transactions.read
payments.qr.create
admin.users.manage
```

Identity stores who can do what. Domain services still own their own data and must verify access server-side.
