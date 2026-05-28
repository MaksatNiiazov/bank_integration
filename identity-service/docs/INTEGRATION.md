# Connecting Other Services

Domain services should validate Identity JWT tokens locally and enforce their own permissions.

## Environment

Use the same token settings in every service:

```env
IDENTITY_SECRET_KEY=dev-change-me-32-byte-secret-key-for-turkuaz-identity
IDENTITY_ALGORITHM=HS256
```

For production, keep `SECRET_KEY` in a secret manager and rotate it carefully.

## Request Flow

Frontend sends:

```text
Authorization: Bearer <identity-access-token>
```

Service verifies:

1. token signature and expiry;
2. required permission;
3. requested `branch_id` belongs to the user when the endpoint is branch-scoped.

## Permission Check

Global permission:

```text
payments.transactions.read
```

Branch-scoped permission:

```json
{
  "branch_permissions": {
    "bishkek": ["converter.orders.read"]
  }
}
```

If an endpoint receives `branch_code=bishkek`, it should accept the request only when the token has either:

```text
converter.orders.read
```

in global `permissions`, or the same permission under:

```text
branch_permissions.bishkek
```

## Registering Module Permissions

Admin registers a service:

```bash
curl -X POST http://localhost:8020/api/v1/services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"converter","name":"Converter"}'
```

Then registers permissions:

```bash
curl -X POST http://localhost:8020/api/v1/services/converter/permissions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"code":"converter.orders.read","name":"Read orders"},
    {"code":"converter.orders.write","name":"Write orders"}
  ]'
```

See `examples/fastapi_dependency.py` for a copyable FastAPI dependency.
