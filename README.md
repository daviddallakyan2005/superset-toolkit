# Superset Toolkit

Professional toolkit for Apache Superset API automation - datasets, charts, and dashboards.

## Features

- **Authentication & Session Management**: Automatic login, CSRF token handling, and session management
- **Dataset Operations**: Create, ensure, refresh, and manage Superset datasets
- **Chart Creation**: Support for pivot tables, regular tables, pie charts, histograms, area charts, and more
- **Dashboard Management**: Create dashboards, manage layouts, apply custom CSS
- **Orchestrated Flows**: Pre-built flows for common dashboard patterns
- **CLI Interface**: Command-line interface for easy automation
- **Type Safety**: Full type hints for better development experience

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

## Quick Start

### Environment Variables

Set these environment variables before using the toolkit:

```bash
export SUPERSET_URL="https://your-superset-instance.com"
export SUPERSET_USERNAME="your-username"
export SUPERSET_PASSWORD="your-password"
export SUPERSET_SCHEMA="your_schema"  # Optional, defaults to 'reports'
export SUPERSET_DATABASE_NAME="YourDatabase"  # Optional, defaults to 'Trino'
```

### Basic Usage

```python
from superset_toolkit import SupersetClient
from superset_toolkit.charts import create_table_chart
from superset_toolkit.dashboard import ensure_dashboard, add_charts_to_dashboard

# Create client (authenticates automatically)
client = SupersetClient()

# Use individual components to build what you need
session = client.session
base_url = client.base_url
user_id = client.user_id

# Example: Create a table chart and add it to a dashboard
# (Replace with your actual dataset ID and chart configuration)
# chart_id = create_table_chart(session, base_url, "My Chart", dataset_id, user_id, columns=["col1", "col2"])
# dashboard_id = ensure_dashboard(session, base_url, "My Dashboard", "my-dashboard")
# add_charts_to_dashboard(session, base_url, dashboard_id, [chart_id])
```

### CLI Usage

```bash
# Test connection to Superset
superset-toolkit test-connection

# With custom parameters
superset-toolkit test-connection --url https://custom-superset.com --schema custom_schema --database MyDB

# Show version
superset-toolkit version
```

## Architecture

The toolkit is organized into several modules:

- **`client.py`**: Main SupersetClient class that manages authentication and provides high-level access
- **`auth.py`**: Authentication, CSRF token management, and user identification
- **`datasets.py`**: Dataset creation, management, and metadata operations
- **`charts.py`**: Chart creation functions for various visualization types
- **`dashboard.py`**: Dashboard creation, layout management, and styling
- **`ensure.py`**: Idempotent resource management (create-or-get patterns)
- **`utils/`**: Utility functions like metric builders

## Individual Operations

### Dataset Management

```python
from superset_toolkit import SupersetClient
from superset_toolkit.datasets import ensure_dataset, refresh_dataset_metadata

client = SupersetClient()
session, base_url = client.session, client.base_url

# Get database ID
from superset_toolkit.ensure import get_database_id_by_name
database_id = get_database_id_by_name(session, base_url, "Trino")

# Ensure dataset exists
dataset_id = ensure_dataset(session, base_url, database_id, "reports", "my_table")

# Refresh metadata
refresh_dataset_metadata(session, base_url, dataset_id)
```

### Chart Creation

```python
from superset_toolkit.charts import create_table_chart, create_pie_chart
from superset_toolkit.utils.metrics import build_simple_metric

# Create a table chart
chart_id = create_table_chart(
    session, base_url, "My Table", dataset_id, client.user_id,
    columns=["col1", "col2", "col3"],
    row_limit=1000,
    include_search=True
)

# Create a pie chart
metric = build_simple_metric("amount", aggregate="SUM")
pie_chart_id = create_pie_chart(
    session, base_url, "Sales by Category", dataset_id, client.user_id,
    metric=metric,
    groupby=["category"]
)
```

### Dashboard Operations

```python
from superset_toolkit.dashboard import ensure_dashboard, add_charts_to_dashboard

# Create dashboard
dashboard_id = ensure_dashboard(session, base_url, "My Dashboard", "my-dashboard")

# Add charts to dashboard
add_charts_to_dashboard(session, base_url, dashboard_id, [chart_id, pie_chart_id])
```

## Custom Configuration

```python
from superset_toolkit import SupersetClient
from superset_toolkit.config import Config

# Create custom config
config = Config(
    superset_url="https://custom-superset.com",
    schema="custom_schema",
    database_name="CustomDB"
)

# Use with client
client = SupersetClient(config=config)
```

## Available Chart Types

- **Pivot Tables**: `create_pivot_table_chart()`
- **Regular Tables**: `create_table_chart()`
- **Pie Charts**: `create_pie_chart()`
- **Histograms**: `create_histogram_chart()`
- **Area Charts**: `create_area_chart()`

## Building Custom Solutions

The toolkit provides all the building blocks you need to create custom Superset automation:

### Common Patterns

1. **Dataset Management**: Ensure datasets exist and refresh metadata
2. **Chart Creation**: Create various chart types with full customization
3. **Dashboard Assembly**: Create dashboards and arrange charts in layouts
4. **Batch Operations**: Process multiple charts, datasets, or dashboards

### Example Workflow

```python
# 1. Ensure your data sources are available
dataset_id = ensure_dataset(session, base_url, database_id, schema, table_name)
refresh_dataset_metadata(session, base_url, dataset_id)

# 2. Create charts with your data
chart_id = create_pie_chart(session, base_url, "Sales by Region", dataset_id, user_id,
                           metric=build_simple_metric("sales", aggregate="SUM"),
                           groupby=["region"])

# 3. Organize in dashboards
dashboard_id = ensure_dashboard(session, base_url, "Sales Dashboard", "sales-dashboard")
add_charts_to_dashboard(session, base_url, dashboard_id, [chart_id])
```

## Examples

Check the `examples/` directory for:

- `basic_usage.py`: Simple usage example
- `custom_config.py`: Custom configuration example
- `individual_operations.py`: Using individual components

## Error Handling

The toolkit provides custom exceptions:

- `SupersetToolkitError`: Base exception
- `AuthenticationError`: Authentication failures
- `SupersetApiError`: API-related errors
- `DatasetNotFoundError`: Dataset not found
- `ChartCreationError`: Chart creation failures
- `DashboardError`: Dashboard operation errors

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

### Type Checking

```bash
mypy src/
```

## License

MIT License

## Author

Open source project  
[GitHub Repository](https://github.com/daviddallakyan2005/superset-toolkit)