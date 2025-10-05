# Superset Server Setup Guide

This guide covers the required Superset server configuration for the SDK to work properly.

## Required Superset Configuration

Add these settings to your `superset_config.py` file:

```python
# ============================================================================
# REQUIRED SETTINGS FOR SUPERSET TOOLKIT SDK
# ============================================================================

# Enable Flask-AppBuilder Security API endpoints (REQUIRED)
# This enables /api/v1/security/users endpoint for username resolution
FAB_ADD_SECURITY_API = True

# Enable CSRF protection for web UI but exempt API endpoints (REQUIRED)
# This allows JWT-only authentication for API calls while maintaining web security
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']

# Fix proxy headers when behind nginx/load balancer (RECOMMENDED)
# Essential when Superset is behind a reverse proxy/ingress
ENABLE_PROXY_FIX = True

# Optional: Enhanced features
FEATURE_FLAGS = {"DASHBOARD_CSS": True}
```

## Why These Settings Are Needed

### `FAB_ADD_SECURITY_API = True`
- **Purpose**: Enables the `/api/v1/security/users` endpoint
- **SDK Usage**: Required for username to user ID resolution
- **Impact**: Without this, username-based operations will fail

### `WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']`
- **Purpose**: Exempts API endpoints from CSRF token requirements
- **SDK Usage**: Allows pure JWT authentication for API calls
- **Impact**: Without this, all API calls will require session cookies

### `ENABLE_PROXY_FIX = True`
- **Purpose**: Handles `X-Forwarded-*` headers correctly
- **SDK Usage**: Ensures proper URL generation and client IP detection
- **Impact**: Required when Superset is behind nginx/load balancer

## User Permissions

### Admin Users
- ✅ Can access all endpoints and features
- ✅ Can query any user via `/api/v1/security/users`
- ✅ Can create charts/dashboards for any user
- ✅ Can migrate resources between users

### Regular Users
- ✅ Can login and get JWT tokens  
- ✅ Can create charts/dashboards
- ✅ Can specify any username as owner (if they know it)
- ❌ Cannot query other users (403 Forbidden - handled gracefully by SDK)
- ❌ Cannot migrate users (lacks permissions)

## SDK Behavior by User Type

### Admin User Experience
```python
with SupersetClient(config=admin_config) as client:
    # Full functionality available
    chart_id = client.create_table_chart("Report", table="data", owner="any_user")
    users = client.get_charts(owner="any_user")  # Works
    client.migrate_user_resources("user1", "user2")  # Works
```

### Regular User Experience  
```python
with SupersetClient(config=regular_config) as client:
    # Chart creation works
    chart_id = client.create_table_chart("My Report", table="my_data")  # Works
    chart_id = client.create_table_chart("Team Report", table="data", owner="teammate")  # Works
    
    # User ID extraction from JWT works
    user_id = client.user_id  # ✅ Extracted from JWT token
    
    # Querying others fails gracefully
    try:
        charts = client.get_charts(owner="other_user")  # 403 Forbidden
    except AuthenticationError:
        pass  # SDK handles this gracefully
```

## Kubernetes/Helm Configuration

If deploying via Helm, add these to your `values.yaml`:

```yaml
configOverrides:
  superset_config.py: |
    # Required for Superset Toolkit SDK
    FAB_ADD_SECURITY_API = True
    WTF_CSRF_ENABLED = True
    WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']
    ENABLE_PROXY_FIX = True
    
    # Optional enhancements
    FEATURE_FLAGS = {"DASHBOARD_CSS": True}
```

## Testing Your Configuration

Use the SDK's built-in validation:

```python
from superset_toolkit import SupersetClient

with SupersetClient() as client:
    status = client.validate_connection()
    
    if status['status'] == 'connected':
        print(f"✅ SDK compatible: {status['message']}")
        print(f"   User ID: {status['user_id']}")
        print(f"   Charts available: {status['chart_count']}")
    else:
        print(f"❌ Configuration issue: {status['message']}")
```

## Troubleshooting Configuration Issues

### Issue: "HTTP 404 on /api/v1/security/users"

**Cause**: `FAB_ADD_SECURITY_API = True` not set or not working

**Solution**:
1. Add `FAB_ADD_SECURITY_API = True` to `superset_config.py`
2. Restart Superset pods/containers
3. Verify with: `curl -H "Authorization: Bearer $TOKEN" $SUPERSET_URL/api/v1/security/users`

### Issue: "The referrer header is missing"

**Cause**: CSRF protection blocking API calls

**Solution**:
1. Add `WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']` to config
2. Restart Superset
3. Verify JWT-only API calls work

### Issue: "Connection failed" with proxy

**Cause**: `ENABLE_PROXY_FIX = True` not set

**Solution**:
1. Add `ENABLE_PROXY_FIX = True` to config
2. Ensure proxy passes proper headers (`X-Forwarded-For`, etc.)

### Issue: "User lookup works for admin but not regular users"

**This is expected behavior**:
- ✅ Admin users can query `/api/v1/security/users`
- ❌ Regular users get 403 Forbidden (normal security restriction)
- ✅ SDK automatically uses JWT extraction for regular users

## Security Considerations

1. **JWT Token Security**: Tokens contain user ID in `sub` field - this is standard
2. **CSRF Exemption**: Only applies to API endpoints, web UI remains protected
3. **Proxy Headers**: Only enable `ENABLE_PROXY_FIX` if behind trusted proxy
4. **User Permissions**: Regular users can still create resources but can't query others

## Production Deployment Checklist

- [ ] `FAB_ADD_SECURITY_API = True` added to config
- [ ] `WTF_CSRF_EXEMPT_LIST = ['/api/v1/*']` added to config  
- [ ] `ENABLE_PROXY_FIX = True` added if behind proxy
- [ ] Superset restarted after configuration changes
- [ ] SDK connection validation passes
- [ ] Test with both admin and regular user accounts
- [ ] Verify username resolution works for admin users
- [ ] Verify JWT extraction works for all users

---

**With proper configuration, the Superset Toolkit provides robust, permission-aware automation for all user types.**
