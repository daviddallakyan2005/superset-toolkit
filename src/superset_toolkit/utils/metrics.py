"""Metric builders for Superset charts."""

from typing import Dict, Any, Optional


def build_simple_metric(
    column_name: str,
    column_type: str = "BIGINT",
    aggregate: str = "SUM",
    label: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a simple aggregation metric for Superset charts.
    
    Args:
        column_name: Name of the column to aggregate
        column_type: SQL column type
        aggregate: Aggregation function (SUM, COUNT, AVG, etc.)
        label: Display label for the metric
        
    Returns:
        Metric configuration dictionary
    """
    metric_label = label or f"{aggregate}({column_name})"
    return {
        "aggregate": aggregate,
        "column": {
            "column_name": column_name,
            "type": column_type,
        },
        "expressionType": "SIMPLE",
        "label": metric_label,
        "optionName": f"metric_{aggregate.lower()}_{column_name}"
    }


def build_sql_metric(label: str, sql_expression: str) -> Dict[str, Any]:
    """
    Build a SQL expression metric for Superset charts.
    
    Args:
        label: Display label for the metric
        sql_expression: SQL expression to calculate the metric
        
    Returns:
        Metric configuration dictionary
    """
    return {
        "expressionType": "SQL",
        "label": label,
        "sqlExpression": sql_expression,
        "optionName": f"metric_sql_{label.lower().replace(' ', '_')}"
    }
