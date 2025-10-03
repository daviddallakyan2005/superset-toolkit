"""Test metric builder utilities."""

from superset_toolkit.utils.metrics import build_simple_metric, build_sql_metric


def test_build_simple_metric():
    """Test building a simple aggregation metric."""
    metric = build_simple_metric("sales", "DECIMAL", "SUM", "Total Sales")
    
    expected = {
        "aggregate": "SUM",
        "column": {
            "column_name": "sales",
            "type": "DECIMAL",
        },
        "expressionType": "SIMPLE",
        "label": "Total Sales",
        "optionName": "metric_sum_sales"
    }
    
    assert metric == expected


def test_build_simple_metric_defaults():
    """Test building a simple metric with default values."""
    metric = build_simple_metric("count_field")
    
    expected = {
        "aggregate": "SUM",
        "column": {
            "column_name": "count_field",
            "type": "BIGINT",
        },
        "expressionType": "SIMPLE",
        "label": "SUM(count_field)",
        "optionName": "metric_sum_count_field"
    }
    
    assert metric == expected


def test_build_sql_metric():
    """Test building a SQL expression metric."""
    metric = build_sql_metric("Approval Rate", "approved / total * 100")
    
    expected = {
        "expressionType": "SQL",
        "label": "Approval Rate",
        "sqlExpression": "approved / total * 100",
        "optionName": "metric_sql_approval_rate"
    }
    
    assert metric == expected


def test_build_sql_metric_complex_label():
    """Test building a SQL metric with complex label."""
    metric = build_sql_metric("Average Order Value (USD)", "SUM(amount) / COUNT(DISTINCT order_id)")
    
    expected = {
        "expressionType": "SQL",
        "label": "Average Order Value (USD)",
        "sqlExpression": "SUM(amount) / COUNT(DISTINCT order_id)",
        "optionName": "metric_sql_average_order_value_(usd)"
    }
    
    assert metric == expected
