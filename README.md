# 🚀 Superset Toolkit

**Production-grade SDK for Apache Superset API automation with professional patterns.**

## ✨ Key Features

- 🎯 **Client-Centric Design**: No more repetitive `(session, base_url)` parameters
- 👤 **Username-Aware Operations**: Work with usernames directly, no manual ID resolution
- 🔧 **JWT-Based Authentication**: Robust user ID extraction from tokens (works for any user)
- 🚀 **Composite Workflows**: Complete operations in single function calls  
- 📦 **Batch Operations**: Efficient bulk chart/dashboard management
- 🧹 **Resource Lifecycle**: Context managers with automatic cleanup
- 🛡️ **Professional Error Handling**: Graceful fallbacks and detailed logging
- 📊 **Full Chart Support**: Table, pie, histogram, area charts with username support

## Installation

### Basic Installation

```bash
pip install -e .
```

### With CLI Support

```bash
pip install -e ".[cli]"
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Professional Client-Centric Usage (Recommended)

```python
from superset_toolkit import SupersetClient
from superset_toolkit.config import Config

# Configure connection
config = Config(
    superset_url="https://your-superset-instance.com",
    username="your-username",
    password="your-secure-password",
    schema="your-schema",
    database_name="your-database"
)

# Context manager with automatic cleanup
with SupersetClient(config=config) as client:
    
    # Create chart (all complexity hidden)
    chart_id = client.create_table_chart(
        name="Sales Report",
        table="sales_data",
        owner="analyst"  # Just username - no ID resolution needed!
    )
    
    # Create dashboard with automatic chart linking
    dashboard_id = client.create_dashboard(
        title="Sales Dashboard", 
        slug="sales-dashboard",
        owner="analyst",
        charts=["Sales Report"]  # Auto-links existing charts
    )
    
    # Query resources by owner
    user_charts = client.get_charts(owner="analyst")
    user_dashboards = client.get_dashboards(owner="analyst")
    
    # Get comprehensive user summary
    summary = client.get_user_summary("analyst")
    print(f"User has: {summary['summary']}")
    
    # Clean up everything for a user
    client.cleanup_user("temp_user", dry_run=False)
```

### Batch & Composite Operations

```python
# Create dashboard with multiple charts in one operation
result = client.create_dashboard_with_charts(
    dashboard_title="Analytics Dashboard",
    slug="analytics-dash",
    chart_configs=[
        {"name": "Sales Chart", "table": "sales", "columns": ["region", "amount"]},
        {"name": "Revenue Chart", "table": "revenue", "columns": ["month", "total"]}
    ],
    owner="analytics_team"
)

# Create multiple charts efficiently  
chart_ids = client.create_charts_batch([
    {"name": "Chart 1", "table": "data1"},
    {"name": "Chart 2", "table": "data2"},
    {"name": "Chart 3", "table": "data3"}
], owner="data_team")
```

### Enhanced Standalone Functions (For Advanced Use Cases)

```python
from superset_toolkit.charts import create_table_chart
from superset_toolkit.queries import get_charts_by_username

client = SupersetClient()

# Enhanced standalone functions now support username parameter
chart_id = create_table_chart(
    client.session, client.base_url, 
    "Advanced Chart", dataset_id,
    username="data_analyst"  # No manual user ID resolution!
)

# Direct function calls for specific operations
charts = get_charts_by_username(client.session, client.base_url, "data_analyst")
```

### Environment Variables (Optional)

```bash
export SUPERSET_URL="https://your-superset-instance.com"
export SUPERSET_USERNAME="your-username" 
export SUPERSET_PASSWORD="your-password"
export SUPERSET_SCHEMA="your_schema"  # Optional, defaults to 'reports'
export SUPERSET_DATABASE_NAME="YourDatabase"  # Optional, defaults to 'Trino'
```


**Module Organization:**
- **`client.py`**: Enhanced SupersetClient with professional methods
- **`auth.py`**: JWT-based authentication with permission-aware fallbacks
- **`charts.py`**: Username-aware chart creation (table, pie, histogram, area)
- **`dashboard.py`**: Dashboard creation with automatic chart linking
- **`queries.py`**: Resource filtering and querying by owner/dataset
- **`datasets.py`**: Dataset management with permission handling

## 📊 Advanced Usage Examples

### Multiple Chart Types with Username Support

```python
with SupersetClient() as client:
    # Table chart
    table_chart = client.create_chart_from_table(
        chart_name="Sales Data",
        table="sales",
        owner="analyst",
        chart_type="table",
        columns=["region", "amount", "date"]
    )
    
    # Pie chart  
    pie_chart = client.create_chart_from_table(
        chart_name="Sales by Region", 
        table="sales",
        owner="analyst",
        chart_type="pie",
        metric={"aggregate": "SUM", "column": {"column_name": "amount"}},
        groupby=["region"]
    )
    
    # Histogram
    hist_chart = client.create_chart_from_table(
        chart_name="Amount Distribution",
        table="sales", 
        owner="analyst",
        chart_type="histogram",
        all_columns_x=["amount"],
        bins=10
    )
```

### Resource Management & Migration

```python
with SupersetClient() as client:
    # Get comprehensive user summary
    summary = client.get_user_summary("data_analyst")
    print(f"User has: {summary['summary']}")
    
    # Migrate resources between users
    result = client.migrate_user_resources(
        from_user="old_analyst", 
        to_user="new_analyst",
        dry_run=False
    )
    
    # Clean up user resources
    cleanup = client.cleanup_user("temp_user", dry_run=False)
    print(f"Deleted: {len(cleanup['chart_ids'])} charts, {len(cleanup['dashboard_ids'])} dashboards")
```

### Dataset Ownership Management

```python
from superset_toolkit import SupersetClient
from superset_toolkit.datasets import add_dataset_owner, refresh_dataset_metadata
from superset_toolkit.ensure import get_dataset_id

# Login as admin (with privileges to modify ownership)
client = SupersetClient()

# Get dataset ID
dataset_id = get_dataset_id(client.session, client.base_url, "sales_data", "public")

# Refresh dataset metadata (update columns from database)
refresh_dataset_metadata(client.session, client.base_url, dataset_id)

# Add an owner to the dataset without removing existing owners
# Admin logs in, but adds other users as owners for collaboration
add_dataset_owner(
    client.session, 
    client.base_url, 
    dataset_id, 
    username="data_analyst"  # Add this user as owner
)

# Add multiple owners
for username in ["analyst1", "analyst2", "analyst3"]:
    add_dataset_owner(client.session, client.base_url, dataset_id, username)
```

**Key Features:**
- ✅ **Preserves existing owners** - doesn't remove anyone
- ✅ **Admin authentication** - login as admin, add others as owners
- ✅ **Idempotent** - won't duplicate if user is already an owner
- ✅ **Collaboration-friendly** - enable team access to datasets

## 🔧 Installation & Setup

```bash
# Install the toolkit
pip install -e .

# Optional: Install with CLI support  
pip install -e ".[cli]"
```

## 🎯 Why Choose This SDK?

**Before (Traditional Approach):**
```python
# Manual user ID resolution, parameter repetition, fragmented operations
user_id = get_user_id_by_username(session, base_url, "john")
dataset_id = ensure_dataset(session, base_url, db_id, schema, table)  
chart_id = create_table_chart(session, base_url, name, dataset_id, user_id)
dashboard_id = ensure_dashboard(session, base_url, title, slug)
link_chart_to_dashboard(session, base_url, chart_id, dashboard_id)
```

**After (Professional SDK):**
```python
# Clean, username-first, composite operations
with SupersetClient() as client:
    chart_id = client.create_table_chart("Report", table="sales", owner="analyst")
    dashboard_id = client.create_dashboard("Dashboard", "dashboard", charts=["Report"])
```

## 📚 Documentation

- 📖 **[Full Documentation](docs/)** - Comprehensive guides and API reference
- 🎯 **[Examples](examples/)** - Ready-to-run examples for common patterns
- 🔧 **[Configuration Guide](docs/CONFIGURATION.md)** - Setup and customization
- 👤 **[User Management](docs/USER_MANAGEMENT.md)** - Username-aware operations

## 🎯 Supported Chart Types

| Chart Type | Client Method | Standalone Function | Username Support |
|------------|---------------|--------------------|-----------------| 
| **Table** | `client.create_table_chart()` | `create_table_chart()` | ✅ |
| **Pie** | `client.create_chart_from_table(type="pie")` | `create_pie_chart()` | ✅ |
| **Histogram** | `client.create_chart_from_table(type="histogram")` | `create_histogram_chart()` | ✅ |
| **Area** | `client.create_chart_from_table(type="area")` | `create_area_chart()` | ✅ |
| **Pivot** | Available via standalone function | `create_pivot_table_chart()` | ✅ |

## 🛡️ Error Handling & Permissions

The SDK gracefully handles permission restrictions:
- **JWT Token Extraction**: Gets user ID without requiring admin permissions
- **403 Fallback Logic**: Smart fallbacks for non-admin users
- **Professional Exceptions**: Clear error messages with context

```python
# Robust error handling
try:
    chart_id = client.create_table_chart("Report", table="sales", owner="user") 
except AuthenticationError as e:
    print(f"Auth issue: {e}")
except SupersetToolkitError as e:
    print(f"Operation failed: {e}")
```

## 📁 Project Structure

```
superset_toolkit/
├── 📖 docs/              # Comprehensive documentation
├── 🎯 examples/          # Ready-to-run examples  
├── 🔧 src/superset_toolkit/
│   ├── client.py         # Professional SupersetClient class
│   ├── auth.py          # JWT + permission-aware authentication
│   ├── charts.py        # Username-aware chart creation
│   ├── dashboard.py     # Dashboard management 
│   ├── queries.py       # Resource filtering and queries
│   └── utils/           # Utilities (metrics, etc.)
└── 🧪 src/superset-api-test/  # Test scripts
```

## 🚀 Getting Started

1. **Install**: `pip install -e .`
2. **Configure**: Set up credentials (Config class or env vars)  
3. **Explore**: Check `examples/` for common patterns
4. **Read Docs**: Review `docs/` for comprehensive guides

## 📝 License & Contributing

MIT License - Open source project for the Superset community.