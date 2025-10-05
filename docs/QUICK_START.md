# Quick Start Guide

Get up and running with Superset Toolkit in 5 minutes.

## 1. Installation

```bash
pip install -e .
```

## 2. Basic Setup

### Option A: Environment Variables (Simplest)

```bash
export SUPERSET_URL="https://your-superset-instance.com"
export SUPERSET_USERNAME="your-username"
export SUPERSET_PASSWORD="your-secure-password"
```

### Option B: Config Class (Recommended)

```python
from superset_toolkit.config import Config

config = Config(
    superset_url="https://your-superset-instance.com",
    username="your-username", 
    password="your-secure-password",
    schema="analytics",
    database_name="your-database"
)
```

## 3. First Chart & Dashboard

```python
from superset_toolkit import SupersetClient

# Method 1: Simple client usage
with SupersetClient() as client:
    # Create a chart (replace with your actual table name)
    chart_id = client.create_table_chart(
        name="My First Chart",
        table="your_table_name",  # ← Replace with real table
        columns=["column1", "column2"]
    )
    
    # Create a dashboard and link the chart
    dashboard_id = client.create_dashboard(
        title="My First Dashboard",
        slug="my-first-dashboard", 
        charts=["My First Chart"]  # Auto-links by name
    )
    
    print(f"✅ Created chart {chart_id} and dashboard {dashboard_id}")
    print(f"🌐 View at: {client.base_url}/superset/dashboard/my-first-dashboard/")
```

## 4. Create Charts for Different Users

```python
with SupersetClient() as client:
    # Chart for specific user (no manual user ID resolution needed!)
    sales_chart = client.create_table_chart(
        name="Sales Report", 
        table="sales_data",
        owner="sales_team",  # Just specify username
        columns=["region", "amount", "date"]
    )
    
    # Chart for another user
    marketing_chart = client.create_table_chart(
        name="Campaign Performance",
        table="campaign_data",
        owner="marketing_team",
        columns=["campaign", "impressions", "conversions"]
    )
    
    print("✅ Created charts for different users")
```

## 5. Query & Manage Resources

```python
with SupersetClient() as client:
    # Get all charts owned by a user
    user_charts = client.get_charts(owner="sales_analyst")
    print(f"Sales analyst has {len(user_charts)} charts")
    
    # Get user summary
    summary = client.get_user_summary("sales_team") 
    print(f"Complete summary: {summary['summary']}")
    
    # Clean up if needed
    # client.cleanup_user("temp_user", dry_run=False)
```

## 6. Error Handling

```python
from superset_toolkit.exceptions import SupersetToolkitError, AuthenticationError

try:
    with SupersetClient() as client:
        chart_id = client.create_table_chart("Test", table="nonexistent_table")
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except SupersetToolkitError as e:
    print(f"Operation failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Common Patterns

### Pattern 1: Single Chart + Dashboard

```python
with SupersetClient() as client:
    chart_id = client.create_table_chart("Report", table="data")
    dashboard_id = client.create_dashboard("Dashboard", "dash", charts=["Report"])
```

### Pattern 2: Multiple Charts + Dashboard

```python
with SupersetClient() as client:
    result = client.create_dashboard_with_charts(
        dashboard_title="Analytics Dashboard",
        slug="analytics",
        chart_configs=[
            {"name": "Sales", "table": "sales"},
            {"name": "Revenue", "table": "revenue"}
        ]
    )
    print(f"Created dashboard {result['dashboard_id']} with charts {result['chart_ids']}")
```

### Pattern 3: Batch Operations

```python
with SupersetClient() as client:
    # Create multiple charts
    chart_ids = client.create_charts_batch([
        {"name": "Q1 Report", "table": "q1_data"},
        {"name": "Q2 Report", "table": "q2_data"},
        {"name": "Q3 Report", "table": "q3_data"}
    ])
    
    print(f"Created {len(chart_ids)} charts in batch")
```

## Next Steps

1. **Explore Examples**: Check `examples/` directory for more patterns
2. **Read Full Documentation**: Review `docs/` for comprehensive guides  
3. **Advanced Features**: Learn about composite operations and resource management
4. **Permissions**: Understand user permissions and JWT authentication

## Troubleshooting

### Connection Issues

```python
# Test connection
status = client.validate_connection()
if status['status'] != 'connected':
    print(f"Issue: {status['message']}")
```

### Authentication Issues  

```python
# Check if authentication is working
try:
    client = SupersetClient()
    print(f"✅ Authenticated as user ID: {client.user_id}")
except AuthenticationError as e:
    print(f"❌ Auth failed: {e}")
```

### Permission Issues

The SDK handles permission restrictions automatically:
- **JWT extraction** works for all users
- **API fallbacks** for admin operations  
- **Graceful degradation** for limited permissions

## Sample Tables for Testing

If you need test data, create these tables in your database:

```sql
-- Simple test table
CREATE TABLE test_data (
    id INTEGER,
    name VARCHAR(100),
    value DECIMAL(10,2),
    category VARCHAR(50),
    created_date DATE
);

-- Insert sample data
INSERT INTO test_data VALUES 
(1, 'Item 1', 100.50, 'Category A', '2024-01-01'),
(2, 'Item 2', 250.75, 'Category B', '2024-01-02'),
(3, 'Item 3', 175.25, 'Category A', '2024-01-03');
```

Then use with the toolkit:
```python
chart_id = client.create_table_chart("Test Chart", table="test_data")
```
