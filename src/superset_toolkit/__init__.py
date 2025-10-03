"""
Superset Toolkit - Professional API automation for Apache Superset.

This package provides a clean, modular interface for automating Superset operations:
- Authentication and session management
- Dataset creation and management
- Chart creation (pivot tables, pie charts, histograms, area charts, etc.)
- Dashboard creation and layout management
- General-purpose building blocks for any Superset automation

Example:
    >>> from superset_toolkit import SupersetClient
    >>> from superset_toolkit.charts import create_table_chart
    >>> from superset_toolkit.dashboard import ensure_dashboard, add_charts_to_dashboard
    >>> 
    >>> client = SupersetClient()
    >>> # Create charts and dashboards as needed for your specific use case
"""

from .client import SupersetClient
from .exceptions import SupersetToolkitError, AuthenticationError, SupersetApiError

__version__ = "0.1.0"

__all__ = [
    "SupersetClient",
    "SupersetToolkitError",
    "AuthenticationError", 
    "SupersetApiError",
]
