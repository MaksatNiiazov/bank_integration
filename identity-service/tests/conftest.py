from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-identity-service"
os.environ["AUTO_CREATE_SCHEMA"] = "true"
os.environ["AUTO_CREATE_ADMIN"] = "true"
os.environ["DEFAULT_ADMIN_EMAIL"] = "admin@example.com"
os.environ["DEFAULT_ADMIN_PASSWORD"] = "admin123"
