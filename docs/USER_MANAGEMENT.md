# User Management Guide

Complete guide to username-aware operations and user management in Superset Toolkit.

## Overview

The Superset Toolkit provides **username-first operations** that handle user ID resolution automatically, with robust permission handling for both admin and regular users.

## Key Features

- 🎯 **Username-Aware Functions**: All chart/dashboard functions accept `username` parameter
- 🔧 **JWT-Based User ID Extraction**: Works for any authenticated user  
- 🛡️ **Permission-Aware Fallbacks**: Graceful handling of 403 Forbidden errors
- 👥 **Multi-User Support**: Create resources for any user regardless of login
- 🧹 **Resource Management**: Query, migrate, and cleanup user resources

## User ID Resolution Methods

The SDK tries multiple methods automatically:

### 1. JWT Token Extraction (Primary - Works for All Users)

```python
# SDK automatically extracts user ID from JWT token after login
# Works for both admin and regular users, no permissions required
client = SupersetClient()
print(f"Current user ID: {client.user_id}")  # Extracted from JWT
```

**How it works:**
- JWT token contains user ID in the `sub` field
- No API calls required after authentication
- Works regardless of user permissions

### 2. Username Lookup via API (Fallback - Admin Only)

```python
# For admin users who can access /api/v1/security/users
user_id = client.resolve_user_id("john_doe")
```

**Permission requirements:**
- ✅ Admin users: Can look up any username
- ❌ Regular users: Get 403 Forbidden (SDK handles this gracefully)

### 3. Smart 403 Fallback 

```python
# When regular user tries to look up their own username:
# 1. API returns 403 Forbidden
# 2. SDK assumes self-lookup and uses JWT user ID
# 3. Operation continues successfully

# Example: TEST user creating chart for themselves
chart_id = create_table_chart(
    session, base_url, "My Chart", dataset_id,
    username="TEST"  # Works even though TEST user can't query users API
)
```

## Username-Aware Operations

### Chart Creation

All chart functions support the `username` parameter:

```python
from superset_toolkit.charts import create_table_chart, create_pie_chart

# Table chart for specific user
chart_id = create_table_chart(
    client.session, client.base_url,
    "Sales Report", dataset_id,
    username="sales_analyst",  # No manual user ID resolution!
    columns=["region", "amount"]
)

# Pie chart for another user
pie_chart = create_pie_chart(
    client.session, client.base_url,
    "Sales by Region", dataset_id, 
    username="data_scientist",
    metric={"aggregate": "SUM", "column": {"column_name": "amount"}},
    groupby=["region"]
)
```

### Client Methods (Recommended)

```python
with SupersetClient() as client:
    # Create for specific user
    chart_id = client.create_table_chart(
        name="User Report",
        table="sales_data",
        owner="john_doe"  # Username automatically resolved
    )
    
    # Create for authenticated user (no owner specified)  
    dashboard_id = client.create_dashboard(
        title="My Dashboard",
        slug="my-dash"
        # No owner = uses authenticated user
    )
```

## User Resource Management

### Query Resources by User

```python
with SupersetClient() as client:
    # Get all charts owned by a user
    user_charts = client.get_charts(owner="data_analyst")
    print(f"User has {len(user_charts)} charts")
    
    # Get all dashboards owned by a user
    user_dashboards = client.get_dashboards(owner="data_analyst") 
    
    # Get comprehensive user summary
    summary = client.get_user_summary("data_analyst")
    print(f"Complete summary: {summary['summary']}")
    print(f"Charts: {[c['slice_name'] for c in summary['charts']['items']]}")
```

### User Resource Migration

```python
# Transfer ownership between users
migration_result = client.migrate_user_resources(
    from_user="departing_analyst",
    to_user="new_analyst", 
    dry_run=False
)

print(f"Migrated {migration_result['migrated']} resources")
```

### User Cleanup Operations

```python
# Clean up all resources for a user
cleanup_result = client.cleanup_user("temp_contractor", dry_run=False)

print(f"Deleted:")
print(f"  Charts: {len(cleanup_result['chart_ids'])}")  
print(f"  Dashboards: {len(cleanup_result['dashboard_ids'])}")
```

## Ownership Patterns

### Pattern 1: No Owner Specified (Session User)

```python
# Uses authenticated user automatically
chart_id = client.create_table_chart(
    name="My Report",
    table="data"
    # No owner = uses whoever is logged in
)
```

### Pattern 2: Explicit Current User

```python
# Get current user explicitly
current_user_id = client.resolve_current_user_id()

# Use in operations (though usually not necessary)
chart_id = client.create_table_chart(
    name="Current User Report", 
    table="data",
    owner="admin"  # Explicit username
)
```

### Pattern 3: Specific User

```python
# Create for any user (admin permissions may be required)
chart_id = client.create_table_chart(
    name="Team Report",
    table="team_data", 
    owner="team_lead"  # Specific username
)
```

## Multi-User Workflows

### Batch Operations with Different Owners

```python
# Create charts for different users in batch
chart_definitions = [
    {"name": "Sales Report", "table": "sales", "owner": "sales_team"},
    {"name": "Marketing Report", "table": "campaigns", "owner": "marketing_team"},  
    {"name": "Finance Report", "table": "revenue", "owner": "finance_team"}
]

chart_ids = client.create_charts_batch(chart_definitions)
```

### Dashboard with Mixed Ownership

```python
# Create dashboard owned by manager with charts from different teams
result = client.create_dashboard_with_charts(
    dashboard_title="Executive Summary",
    slug="executive-summary",
    chart_configs=[
        {"name": "Sales Overview", "table": "sales", "owner": "sales_team"},
        {"name": "Marketing Metrics", "table": "campaigns", "owner": "marketing_team"}
    ],
    owner="executive_team"  # Dashboard ownership separate from chart ownership
)
```

## Permission Scenarios

### Admin User Capabilities

```python
# Admin users can do everything
with SupersetClient(config=admin_config) as admin_client:
    # Query any user
    user_summary = admin_client.get_user_summary("any_username")
    
    # Create for any user  
    chart_id = admin_client.create_table_chart("Report", table="data", owner="any_user")
    
    # Migrate between users
    admin_client.migrate_user_resources("old_user", "new_user")
```

### Regular User Capabilities

```python
# Regular users have limited but still powerful capabilities
with SupersetClient(config=regular_user_config) as user_client:
    # Can create charts/dashboards (owned by themselves or others)
    chart_id = user_client.create_table_chart("My Report", table="my_data")
    
    # Can create for other users (if they know the username)
    chart_id = user_client.create_table_chart("Team Report", table="team_data", owner="teammate")
    
    # Cannot query other users (403 Forbidden - handled gracefully)
    # Cannot migrate users (lacks permissions)
```

## Error Handling

### Permission-Related Errors

```python
try:
    # This might fail for regular users
    summary = client.get_user_summary("other_user")
except AuthenticationError as e:
    if "403" in str(e):
        print("User lacks permissions to query other users")
        # SDK automatically handles this in most cases
    else:
        print(f"Authentication issue: {e}")
```

### Graceful Degradation

The SDK is designed to **work with whatever permissions the user has**:

- **Admin users**: Full functionality
- **Regular users**: Chart/dashboard creation still works
- **Limited users**: Fallback to safe defaults (user_id=1)

## Best Practices

1. **Use admin accounts** for automation/batch operations
2. **Use specific usernames** when creating resources for others
3. **Handle permission errors gracefully** - SDK provides fallbacks
4. **Use context managers** for production deployments
5. **Validate connections** before bulk operations:

```python
status = client.validate_connection()
if status['status'] != 'connected':
    raise Exception(f"Connection failed: {status['message']}")
```

## Testing Different User Types

```python
# Test with different user permission levels
users_to_test = [
    ("admin", "admin-password"),     # Full permissions
    ("analyst", "analyst-password"), # Limited permissions  
    ("viewer", "viewer-password")    # Minimal permissions
]

for username, password in users_to_test:
    config = Config(
        superset_url="https://test-superset.com",
        username=username,
        password=password
    )
    
    try:
        with SupersetClient(config=config) as client:
            print(f"✅ {username} login successful, user_id: {client.user_id}")
            
            # Test basic operations
            chart_id = client.create_table_chart("Test Chart", table="test_data")
            print(f"✅ {username} can create charts")
            
    except Exception as e:
        print(f"❌ {username} failed: {e}")
```
