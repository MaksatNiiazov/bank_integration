# Turkuaz Platform

Central portal and aggregation layer for Turkuaz internal services.

It gives management and admins one product surface while Converter, Payments, Reports, Warehouse, and future modules stay independently deployable.

## Structure

```text
apps/api   Platform API: service registry, health aggregation, dashboard summary
apps/web   Platform web portal: dashboard, services, admin entry points
```

## Quick Start

API:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload
```

Web:

```bash
cd apps/web
npm install
npm run dev
```

Open:

```text
http://localhost:5174
```

## Service Registry

`platform-api` reads `PLATFORM_SERVICES_JSON`. If it is not set, it uses local defaults for Identity, Converter, Payments, Reports, and Warehouse.

Example:

```env
PLATFORM_SERVICES_JSON=[
  {"code":"identity","name":"Identity","department":"Platform","base_url":"http://localhost:8020","health_path":"/api/v1/health","launch_url":"http://localhost:8020/docs","required_permission":"identity.users.read"},
  {"code":"converter","name":"Converter","department":"Operations","base_url":"http://localhost:8000","health_path":"/api/v1/health","launch_url":"http://localhost:5173","required_permission":"converter.orders.read"}
]
```

The portal must tolerate failed modules. A failed health check returns `unavailable` for that service while the rest of the dashboard continues to load.
