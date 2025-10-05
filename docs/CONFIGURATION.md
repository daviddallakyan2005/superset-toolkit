# Configuration Guide

This guide covers all configuration options and setup patterns for the Superset Toolkit.

## Basic Configuration

### Option 1: Environment Variables (Simplest)

```bash
export SUPERSET_URL="https://superset.yourcompany.com"
export SUPERSET_USERNAME="your-username"
export SUPERSET_PASSWORD="your-password"
export SUPERSET_SCHEMA="analytics"        # Optional, defaults to 'reports'
export SUPERSET_DATABASE_NAME="Trino"     # Optional, defaults to 'Trino'
```

```python
from superset_toolkit import SupersetClient

# Uses environment variables automatically
client = SupersetClient()
```

### Option 2: Config Class (Recommended for Production)

```python
from superset_toolkit import SupersetClient
from superset_toolkit.config import Config

config = Config(
    superset_url="https://your-superset-instance.com",
    username="your-username", 
    password="your-secure-password",
    schema="your-schema",
    database_name="your-database"
)

client = SupersetClient(config=config)
```

### Option 3: Mixed Approach

```python
# Some from env vars, some explicit
config = Config(
    superset_url="https://custom-superset.com",  # Override URL
    schema="custom_schema",                      # Override schema
    # username/password from SUPERSET_USERNAME/SUPERSET_PASSWORD env vars
)
```

## Advanced Configuration

### Context Manager Pattern (Recommended)

```python
with SupersetClient(config=config) as client:
    # All operations here
    chart_id = client.create_table_chart(...)
    
# Automatic session cleanup happens here
```

### Session Reuse for Performance

```python
import requests
from superset_toolkit import SupersetClient

# Reuse session across operations
session = requests.Session()
client = SupersetClient(config=config, session=session)

# Multiple operations with same session...
```

### Username-Based Ownership

```python
# Option 1: Set default ownership user
client = SupersetClient(username_for_ownership="analytics_team")
# All charts/dashboards created by client will be owned by analytics_team

# Option 2: Specify owner per operation
chart_id = client.create_table_chart("Report", table="sales", owner="john_doe")
```

## Configuration Reference

### Config Class Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `superset_url` | `str` | `SUPERSET_URL` env var | Superset instance URL |
| `username` | `str` | `SUPERSET_USERNAME` env var | Login username |
| `password` | `str` | `SUPERSET_PASSWORD` env var | Login password |
| `schema` | `str` | `"reports"` | Default database schema |
| `database_name` | `str` | `"Trino"` | Default database name |

### SupersetClient Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `Config` | Auto from env | Configuration object |
| `session` | `requests.Session` | New session | HTTP session to reuse |
| `username_for_ownership` | `str` | None | Default ownership username |

## Superset Server Configuration

### Required Superset Settings

Add these to your `superset_config.py` for SDK compatibility:

```python
# Enable Flask-AppBuilder Security API endpoints (REQUIRED)
FAB_ADD_SECURITY_API = True

# Enable CSRF protection for web UI but exempt API endpoints for JWT (REQUIRED)
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']  # Allow JWT-only auth for APIs

# Fix proxy headers when behind nginx/load balancer (RECOMMENDED)
ENABLE_PROXY_FIX = True

# Optional: Enhanced API features
FEATURE_FLAGS = {"DASHBOARD_CSS": True}
```

**Why these settings are needed:**
- **`FAB_ADD_SECURITY_API`**: Enables `/api/v1/security/users` endpoint for username lookup
- **`WTF_CSRF_EXEMPT_LIST`**: Allows JWT-only authentication for API endpoints  
- **`ENABLE_PROXY_FIX`**: Handles `X-Forwarded-*` headers correctly behind proxies
- **`WTF_CSRF_ENABLED`**: Maintains web UI security while enabling API access

### Permission Requirements

**For Admin Users:**
- ✅ Can access all endpoints
- ✅ Can query users via `/api/v1/security/users`
- ✅ Can create charts/dashboards for any user

**For Regular Users:**
- ✅ Can login and get JWT token
- ✅ Can create charts/dashboards (their own or specified)
- ❌ Cannot query other users via API (403 Forbidden)
- ✅ **SDK automatically uses JWT extraction for their own user ID**

## Environment-Specific Configurations

### Development Environment

```python
dev_config = Config(
    superset_url="http://localhost:8088",
    username="admin",
    password="admin",
    schema="dev_analytics"
)
```

### Production Environment

```python
import os

prod_config = Config(
    superset_url=os.getenv("PROD_SUPERSET_URL"),
    username=os.getenv("PROD_SUPERSET_USER"),
    password=os.getenv("PROD_SUPERSET_PASS"),
    schema="production_analytics",
    database_name="ProductionTrino"
)
```

### Testing Environment

```python
test_config = Config(
    superset_url="https://test-superset.com",
    username="test-admin",
    password="test-password",
    schema="test_data"
)

# Use context manager for clean testing
with SupersetClient(config=test_config) as client:
    # Run tests...
    pass  # Automatic cleanup
```

## Connection Validation

```python
# Validate connection and get system info
status = client.validate_connection()

if status['status'] == 'connected':
    print(f"✅ Connected to {status['url']}")
    print(f"👤 User ID: {status['user_id']}")
    print(f"📊 System has {status['chart_count']} charts")
else:
    print(f"❌ Connection failed: {status['message']}")
```

## Troubleshooting

### Common Configuration Issues

**1. Authentication Failures**
```python
# Error: "Login failed with status 401"
# Solution: Check username/password, verify user account is active
```

**2. 403 Forbidden on User Operations**
```python
# Error: "HTTP 403 on /api/v1/security/users: Forbidden"
# Solution: SDK automatically uses JWT extraction - no action needed
```

**3. Dataset/Database Not Found**
```python
# Error: "Database 'YourDB' not found" 
# Solution: Verify database_name matches exactly in Superset
```

**4. CSRF Token Issues**
```python
# Error: "The referrer header is missing"
# Solution: SDK automatically handles this - ensure WTF_CSRF_EXEMPT_LIST is set
```

### Debug Connection Issues

```python
from superset_toolkit.cli import simple_main

# Run built-in connection test
simple_main()
```

## Best Practices

1. **Use Config class** for explicit configuration
2. **Use context managers** for automatic cleanup
3. **Specify owners explicitly** for multi-user environments  
4. **Handle permissions gracefully** - SDK has built-in fallbacks
5. **Validate connections** before bulk operations
6. **Use batch operations** for multiple charts/dashboards
