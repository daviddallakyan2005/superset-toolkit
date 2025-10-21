"""
Superset Toolkit - Professional API automation for Apache Superset.

Production-grade SDK with both low-level building blocks and high-level convenience functions.

## Professional Client-Centric Usage (Recommended):

    >>> from superset_toolkit import SupersetClient
    >>> 
    >>> client = SupersetClient()
    >>> 
    >>> # Create chart (all complexity hidden)
    >>> chart_id = client.create_table_chart(
    ...     name="Sales Report",
    ...     table="sales_data",
    ...     owner="john_doe"  # Just username - no ID resolution needed!
    ... )
    >>> 
    >>> # Create dashboard with automatic chart linking
    >>> dashboard_id = client.create_dashboard(
    ...     title="Sales Dashboard", 
    ...     slug="sales-dash",
    ...     owner="john_doe",
    ...     charts=["Sales Report"]  # Auto-links existing charts
    ... )
    >>> 
    >>> # Query resources
    >>> charts = client.get_charts(owner="john_doe")
    >>> dashboards = client.get_dashboards(owner="john_doe")
    >>>
    >>> # Clean up everything for a user
    >>> client.cleanup_user("john_doe", dry_run=False)

## Enhanced Standalone Functions (For Advanced Use Cases):

    >>> from superset_toolkit.charts import create_table_chart
    >>> from superset_toolkit.queries import get_charts_by_username
    >>> 
    >>> # Enhanced standalone functions now support username parameter
    >>> chart_id = create_table_chart(
    ...     client.session, client.base_url, 
    ...     "Advanced Chart", dataset_id,
    ...     username="john_doe"  # No manual user ID resolution!
    ... )
    >>> 
    >>> # Direct function calls for specific operations
    >>> charts = get_charts_by_username(client.session, client.base_url, "john_doe")
"""

from .client import SupersetClient
from .exceptions import SupersetToolkitError, AuthenticationError, SupersetApiError

__version__ = "0.2.2"

__all__ = [
    "SupersetClient",
    "SupersetToolkitError",
    "AuthenticationError", 
    "SupersetApiError",
]
