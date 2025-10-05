# API Reference

Complete reference for all Superset Toolkit classes and functions.

## SupersetClient Class

The main client class for professional Superset operations.

### Constructor

```python
SupersetClient(
    config: Optional[Config] = None,
    session: Optional[requests.Session] = None,
    username_for_ownership: Optional[str] = None
)
```

**Parameters:**
- `config`: Configuration object (uses env vars if None)
- `session`: HTTP session to reuse (creates new if None)
- `username_for_ownership`: Default username for chart/dashboard ownership

### Context Manager Support

```python
with SupersetClient() as client:
    # Operations here
    pass
# Automatic session cleanup
```

### Core Client Methods

#### Chart Operations

**`create_table_chart(name, table, schema=None, owner=None, **kwargs) -> int`**

Creates a table chart with automatic setup.

```python
chart_id = client.create_table_chart(
    name="Sales Report",
    table="sales_data",
    schema="analytics",      # Optional, uses config default
    owner="john_doe",        # Optional, uses authenticated user
    columns=["region", "amount"],
    row_limit=1000
)
```

**`create_chart_from_table(chart_name, table, chart_type="table", owner=None, **kwargs) -> int`**

Creates any chart type from table name.

```python
# Table chart
chart_id = client.create_chart_from_table(
    chart_name="Data Table",
    table="my_data", 
    chart_type="table",
    columns=["col1", "col2"]
)

# Pie chart
pie_id = client.create_chart_from_table(
    chart_name="Distribution",
    table="sales",
    chart_type="pie",
    metric={"aggregate": "COUNT", "column": {"column_name": "id"}},
    groupby=["category"]
)
```

#### Dashboard Operations

**`create_dashboard(title, slug, owner=None, charts=None) -> int`**

Creates a dashboard with optional chart linking.

```python
dashboard_id = client.create_dashboard(
    title="Analytics Dashboard",
    slug="analytics-dash",
    owner="analytics_team",
    charts=["Sales Report", "Revenue Chart"]  # Auto-links by name
)
```

**`create_dashboard_with_charts(dashboard_title, slug, chart_configs, owner=None) -> dict`**

Creates dashboard and multiple charts in one operation.

```python
result = client.create_dashboard_with_charts(
    dashboard_title="Complete Dashboard",
    slug="complete-dash", 
    chart_configs=[
        {"name": "Chart 1", "table": "data1", "type": "table"},
        {"name": "Chart 2", "table": "data2", "type": "pie"}
    ],
    owner="dashboard_team"
)
# Returns: {"dashboard_id": 123, "chart_ids": [456, 789]}
```

#### Query Operations

**`get_charts(owner=None, table=None, schema=None) -> List[dict]`**

Get charts with flexible filtering.

```python
# All charts for a user
charts = client.get_charts(owner="analyst")

# All charts using a specific table
charts = client.get_charts(table="sales_data", schema="analytics")

# All charts in system
all_charts = client.get_charts()
```

**`get_dashboards(owner=None) -> List[dict]`**

Get dashboards with optional owner filtering.

```python
user_dashboards = client.get_dashboards(owner="manager")
```

**`get_user_summary(username) -> dict`**

Get comprehensive user resource summary.

```python
summary = client.get_user_summary("data_analyst")
# Returns:
# {
#   "username": "data_analyst",
#   "user_id": 42,
#   "charts": {"count": 5, "items": [...]},
#   "dashboards": {"count": 2, "items": [...]},
#   "summary": "5 charts, 2 dashboards"
# }
```

#### Resource Management

**`cleanup_user(username, dry_run=True) -> dict`**

Delete all resources for a user.

```python
result = client.cleanup_user("temp_contractor", dry_run=False)
# Returns: {"chart_ids": [1,2,3], "dashboard_ids": [4,5]}
```

**`migrate_user_resources(from_user, to_user, dry_run=True) -> dict`**

Transfer ownership between users.

```python
result = client.migrate_user_resources("old_analyst", "new_analyst", dry_run=False)
# Returns: {"migrated": 10, "charts": [1,2,3], "dashboards": [4,5]}
```

#### Batch Operations

**`create_charts_batch(chart_definitions, owner=None) -> List[int]`**

Create multiple charts efficiently.

```python
chart_ids = client.create_charts_batch([
    {"name": "Chart 1", "table": "data1", "columns": ["col1"]},
    {"name": "Chart 2", "table": "data2", "columns": ["col2"]}
], owner="batch_user")
```

**`delete_charts_batch(chart_ids, dry_run=True) -> List[int]`**

Delete multiple charts efficiently.

```python
deleted = client.delete_charts_batch([123, 456, 789], dry_run=False)
```

#### Utilities

**`validate_connection() -> dict`**

Validate connection and get system info.

```python
status = client.validate_connection()
# Returns:
# {
#   "status": "connected",
#   "url": "https://superset.com",
#   "user_id": 1,
#   "chart_count": 150
# }
```

**`resolve_current_user_id() -> int`**

Explicitly get current user ID.

**`resolve_user_id(username) -> int`**

Explicitly resolve username to user ID.

## Enhanced Standalone Functions

All standalone chart functions now support `username` parameter:

### Chart Functions

```python
from superset_toolkit.charts import (
    create_table_chart,
    create_pie_chart, 
    create_histogram_chart,
    create_area_chart,
    create_pivot_table_chart
)

# All functions support username parameter
chart_id = create_table_chart(
    session, base_url, "Chart Name", dataset_id,
    username="chart_owner",  # Enhanced with username support
    columns=["col1", "col2"]
)
```

### Query Functions  

```python
from superset_toolkit.queries import (
    get_charts_by_username,
    get_dashboards_by_username,
    get_charts_by_dataset
)

# Query resources
charts = get_charts_by_username(session, base_url, "analyst")
dashboards = get_dashboards_by_username(session, base_url, "manager")
dataset_charts = get_charts_by_dataset(session, base_url, dataset_id)
```

### Deletion Functions

```python
from superset_toolkit.charts import delete_charts_by_username
from superset_toolkit.dashboard import delete_dashboards_by_username

# Delete by user
deleted_charts = delete_charts_by_username(session, base_url, "user", dry_run=False)
deleted_dashboards = delete_dashboards_by_username(session, base_url, "user", dry_run=False)
```

## Authentication Internals

### JWT Token Structure

Superset JWT tokens contain:
```json
{
  "sub": 2,           // User ID (this is what we extract)
  "iat": 1234567890,  // Issued at
  "exp": 1234567890,  // Expires at  
  "csrf": "token123", // CSRF token
  "type": "access"    // Token type
}
```

### Permission Matrix

| Operation | Admin User | Regular User | Notes |
|-----------|------------|--------------|-------|
| Login | ✅ | ✅ | Both can authenticate |
| JWT extraction | ✅ | ✅ | Both get user_id from token |
| Query own resources | ✅ | ✅ | Both can see their own charts |
| Query other users | ✅ | ❌ (403) | Only admin can query others |
| Create charts | ✅ | ✅ | Both can create |
| Create for others | ✅ | ✅ | Both can specify owner |
| Delete own resources | ✅ | ✅ | Both can delete their own |
| Delete others' resources | ✅ | ❌ | Only admin typically |

## Error Scenarios & Handling

### Scenario 1: Regular User Querying Others

```python
# Regular user trying to get another user's resources
try:
    charts = client.get_charts(owner="other_user")
except AuthenticationError as e:
    print("Expected: Regular user can't query others")
    # SDK handles this gracefully with fallbacks
```

### Scenario 2: Invalid Username

```python
try:
    chart_id = client.create_table_chart("Chart", table="data", owner="nonexistent") 
except AuthenticationError as e:
    print(f"User not found: {e}")
```

### Scenario 3: Network/API Issues

```python
try:
    client = SupersetClient()
except AuthenticationError as e:
    print(f"Connection/auth failed: {e}")
```

## Advanced Patterns

### Service Account Pattern

```python
# Use dedicated service account for automation
service_config = Config(
    superset_url="https://your-superset-instance.com",
    username="automation_service",
    password="secure-service-password"
)

with SupersetClient(config=service_config) as service:
    # Create resources for multiple teams
    for team in ["sales", "marketing", "finance"]:
        chart_id = service.create_table_chart(f"{team} Report", table=f"{team}_data", owner=f"{team}_team")
```

### Multi-Environment Pattern

```python
environments = {
    "dev": Config(superset_url="https://dev-superset.yourcompany.com", username="dev-admin", ...),
    "staging": Config(superset_url="https://staging-superset.yourcompany.com", username="staging-admin", ...),
    "prod": Config(superset_url="https://prod-superset.yourcompany.com", username="prod-admin", ...)
}

for env_name, config in environments.items():
    with SupersetClient(config=config) as client:
        print(f"Deploying to {env_name}...")
        chart_id = client.create_table_chart("Report", table="environment_data", owner="deployment_team")
```

## Performance Considerations

- **JWT extraction** is instant (no API calls)
- **Batch operations** are more efficient than individual calls
- **Context managers** properly clean up resources
- **Session reuse** improves performance for multiple operations
