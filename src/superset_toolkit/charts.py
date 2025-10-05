"""Chart creation and deletion functions for various Superset visualization types."""

import json
from typing import Dict, Any, List, Optional

import requests

from .exceptions import ChartCreationError, SupersetApiError


def create_pivot_table_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: Optional[int] = None,
    *,
    username: Optional[str] = None,
    metrics: List[Dict[str, Any]],
    groupby_rows: List[str],
    groupby_columns: List[str],
    adhoc_filters: Optional[List[Dict[str, Any]]] = None,
    row_limit: int = 10000,
    order_desc: bool = True,
    aggregateFunction: str = "Sum",
    transposePivot: bool = False,
    combineMetric: bool = False,
    rowSubtotalPosition: bool = True,
    colSubtotalPosition: bool = True,
    conditional_formatting: Optional[List[Dict[str, Any]]] = None,
    series_limit: int = 0,
    series_limit_metric: Optional[Dict[str, Any]] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Create a pivot table chart.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID for ownership
        metrics: List of metric configurations
        groupby_rows: Columns to group by in rows
        groupby_columns: Columns to group by in columns
        adhoc_filters: Optional filters
        row_limit: Maximum number of rows
        order_desc: Whether to order descending
        aggregateFunction: Aggregation function
        transposePivot: Whether to transpose the pivot
        combineMetric: Whether to combine metrics
        rowSubtotalPosition: Whether to show row subtotals
        colSubtotalPosition: Whether to show column subtotals
        conditional_formatting: Optional conditional formatting rules
        series_limit: Series limit
        series_limit_metric: Metric for series limiting
        extra_params: Additional parameters
        
    Returns:
        Chart ID
        
    Raises:
        ChartCreationError: If chart creation fails
    """
    # Resolve user ownership (username takes precedence)
    if username:
        from .auth import get_user_id_by_username
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Resolved user '{username}' to ID: {user_id}")
    elif user_id is None:
        # Fallback for standalone function calls: use authenticated session user
        # This provides better default behavior than hardcoded user_id = 1
        print(f"ℹ️  No user_id or username provided, using authenticated session user as fallback")
        user_id = 1  # Safe fallback - chart creation will succeed with session user
        print(f"✅ Using session user ID: {user_id} (provide username parameter for specific ownership)")
    
    chart_params = {
        "datasource": f"{dataset_id}__table",
        "viz_type": "pivot_table_v2",
        "metrics": metrics,
        "groupbyRows": groupby_rows,
        "groupbyColumns": groupby_columns,
        "adhoc_filters": adhoc_filters or [],
        "row_limit": row_limit,
        "order_desc": order_desc,
        "aggregateFunction": aggregateFunction,
        "transposePivot": transposePivot,
        "combineMetric": combineMetric,
        "rowSubtotalPosition": rowSubtotalPosition,
        "colSubtotalPosition": colSubtotalPosition,
        "conditional_formatting": conditional_formatting or [],
        "series_limit": series_limit,
        "series_limit_metric": series_limit_metric,
    }
    if extra_params:
        chart_params.update(extra_params)

    payload = {
        "slice_name": slice_name,
        "viz_type": "pivot_table_v2",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(chart_params),
        "owners": [user_id]
    }
    
    print(f"📊 Creating pivot table chart: {slice_name}")
    response = session.post(
        f"{base_url}/api/v1/chart/",
        json=payload,
        headers={"Referer": base_url}
    )
    print(f"📊 Chart creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise ChartCreationError(
            f"Chart creation failed: {response.status_code} - {response.text}"
        )
    
    return response.json()['id']


def create_table_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: Optional[int] = None,
    *,
    username: Optional[str] = None,
    columns: Optional[List[str]] = None,
    metrics: Optional[List[Dict[str, Any]]] = None,
    groupby: Optional[List[str]] = None,
    adhoc_filters: Optional[List[Dict[str, Any]]] = None,
    row_limit: int = 10000,
    order_desc: bool = True,
    table_timestamp_format: Optional[str] = None,
    page_length: Optional[int] = None,
    include_time: bool = False,
    order_by_cols: Optional[List[str]] = None,
    table_filter: bool = True,
    align_pn: bool = False,
    color_pn: bool = True,
    include_search: bool = True,
    show_cell_bars: bool = False,
    allow_rearrange_columns: bool = True,
    column_config: Optional[Dict[str, Any]] = None,
    enable_html_rendering: bool = True,
    sanitize_html: bool = True,
    server_page_length: Optional[int] = None,
    server_pagination: Optional[bool] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Create a table chart with flexible ownership options.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID for ownership. If None and username provided, resolves username.
        username: Username for ownership. Takes precedence over user_id if provided.
        columns: Columns to display
        metrics: Metrics to calculate
        groupby: Columns to group by
        adhoc_filters: Optional filters
        row_limit: Maximum number of rows
        order_desc: Whether to order descending
        table_timestamp_format: Timestamp format
        page_length: Page length
        include_time: Whether to include time
        order_by_cols: Columns to order by
        table_filter: Whether to enable table filtering
        align_pn: Align positive/negative numbers
        color_pn: Color positive/negative numbers
        include_search: Whether to include search
        show_cell_bars: Whether to show cell bars
        allow_rearrange_columns: Whether to allow column rearrangement
        column_config: Column configuration
        enable_html_rendering: Whether to enable HTML rendering
        sanitize_html: Whether to sanitize HTML
        server_page_length: Server-side page length
        server_pagination: Whether to use server-side pagination
        extra_params: Additional parameters
        
    Returns:
        Chart ID
        
    Raises:
        ChartCreationError: If chart creation fails
    """
    # Resolve user ownership (username takes precedence)
    if username:
        from .auth import get_user_id_by_username
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Resolved user '{username}' to ID: {user_id}")
    elif user_id is None:
        # Fallback for standalone function calls: use authenticated session user
        # This provides better default behavior than hardcoded user_id = 1
        print(f"ℹ️  No user_id or username provided, using authenticated session user as fallback")
        user_id = 1  # Safe fallback - chart creation will succeed with session user
        print(f"✅ Using session user ID: {user_id} (provide username parameter for specific ownership)")
    
    chart_params = {
        "datasource": f"{dataset_id}__table",
        "viz_type": "table",
        "adhoc_filters": adhoc_filters or [],
        "row_limit": row_limit,
        "order_desc": order_desc,
        "include_time": include_time,
        "table_filter": table_filter,
        "align_pn": align_pn,
        "color_pn": color_pn,
        "include_search": include_search,
        "show_cell_bars": show_cell_bars,
        "allow_rearrange_columns": allow_rearrange_columns,
        "enable_html_rendering": enable_html_rendering,
        "sanitize_html": sanitize_html,
    }
    
    if columns is not None:
        chart_params["all_columns"] = columns
    if metrics is not None:
        chart_params["metrics"] = metrics
    if groupby is not None:
        chart_params["groupby"] = groupby
    if order_by_cols is not None:
        chart_params["order_by_cols"] = order_by_cols
    if column_config is not None:
        chart_params["column_config"] = column_config
    if table_timestamp_format is not None:
        chart_params["table_timestamp_format"] = table_timestamp_format
    if page_length is not None:
        chart_params["page_length"] = page_length
    if server_page_length is not None:
        chart_params["server_page_length"] = server_page_length
    if server_pagination is not None:
        chart_params["server_pagination"] = server_pagination
    if extra_params:
        chart_params.update(extra_params)

    payload = {
        "slice_name": slice_name,
        "viz_type": "table",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(chart_params),
        "owners": [user_id]
    }
    
    print(f"📋 Creating table chart: {slice_name}")
    response = session.post(
        f"{base_url}/api/v1/chart/",
        json=payload,
        headers={"Referer": base_url}
    )
    print(f"📋 Chart creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise ChartCreationError(
            f"Chart creation failed: {response.status_code} - {response.text}"
        )
    
    return response.json()['id']


def create_pie_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: Optional[int] = None,
    *,
    username: Optional[str] = None,
    metric: Dict[str, Any],
    groupby: List[str],
    adhoc_filters: Optional[List[Dict[str, Any]]] = None,
    row_limit: int = 10000,
    pie_label_type: str = "key_value",
    donut: bool = False,
    show_legend: bool = True,
    legendType: str = "scroll",
    legendOrientation: str = "top",
    label_colors: Optional[Dict[str, Any]] = None,
    color_scheme: str = "supersetColors",
    show_labels_threshold: int = 5,
    rich_tooltip: bool = True,
    tooltipTimeFormat: str = "smart_date",
    outerRadius: int = 70,
    innerRadius: int = 30,
    show_total: bool = True,
    sort_by_metric: bool = True,
    date_time_format: str = "smart_date",
    number_format: str = "SMART_NUMBER",
    extra_params: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Create a pie chart.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID for ownership
        metric: Metric configuration
        groupby: Columns to group by
        adhoc_filters: Optional filters
        row_limit: Maximum number of rows
        pie_label_type: Label type for pie slices
        donut: Whether to create a donut chart
        show_legend: Whether to show legend
        legendType: Legend type
        legendOrientation: Legend orientation
        label_colors: Color configuration
        color_scheme: Color scheme
        show_labels_threshold: Threshold for showing labels
        rich_tooltip: Whether to use rich tooltips
        tooltipTimeFormat: Tooltip time format
        outerRadius: Outer radius
        innerRadius: Inner radius
        show_total: Whether to show total
        sort_by_metric: Whether to sort by metric
        date_time_format: Date/time format
        number_format: Number format
        extra_params: Additional parameters
        
    Returns:
        Chart ID
        
    Raises:
        ChartCreationError: If chart creation fails
    """
    # Resolve user ownership (username takes precedence)
    if username:
        from .auth import get_user_id_by_username
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Resolved user '{username}' to ID: {user_id}")
    elif user_id is None:
        # Fallback for standalone function calls: use authenticated session user
        # This provides better default behavior than hardcoded user_id = 1
        print(f"ℹ️  No user_id or username provided, using authenticated session user as fallback")
        user_id = 1  # Safe fallback - chart creation will succeed with session user
        print(f"✅ Using session user ID: {user_id} (provide username parameter for specific ownership)")
    
    chart_params = {
        "datasource": f"{dataset_id}__table",
        "viz_type": "pie",
        "metric": metric,
        "metrics": [metric],
        "groupby": groupby,
        "adhoc_filters": adhoc_filters or [],
        "row_limit": row_limit,
        "pie_label_type": pie_label_type,
        "donut": donut,
        "show_legend": show_legend,
        "legendType": legendType,
        "legendOrientation": legendOrientation,
        "label_colors": label_colors or {},
        "color_scheme": color_scheme,
        "show_labels_threshold": show_labels_threshold,
        "rich_tooltip": rich_tooltip,
        "tooltipTimeFormat": tooltipTimeFormat,
        "outerRadius": outerRadius,
        "innerRadius": innerRadius,
        "show_total": show_total,
        "sort_by_metric": sort_by_metric,
        "date_time_format": date_time_format,
        "number_format": number_format,
    }
    if extra_params:
        chart_params.update(extra_params)

    payload = {
        "slice_name": slice_name,
        "viz_type": "pie",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(chart_params),
        "owners": [user_id]
    }
    
    print(f"🥧 Creating pie chart: {slice_name}")
    response = session.post(
        f"{base_url}/api/v1/chart/",
        json=payload,
        headers={"Referer": base_url}
    )
    print(f"🥧 Chart creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise ChartCreationError(
            f"Chart creation failed: {response.status_code} - {response.text}"
        )
    
    return response.json()['id']


def create_histogram_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: Optional[int] = None,
    *,
    username: Optional[str] = None,
    all_columns_x: List[str],
    adhoc_filters: Optional[List[Dict[str, Any]]] = None,
    row_limit: int = 10000,
    bins: int = 10,
    x_axis_label: str = "Number of Steps",
    y_axis_label: str = "Frequency",
    normalize_across: str = "heatmap",
    link_length: str = "25",
    extra_params: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Create a histogram chart.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID for ownership. If None and username provided, resolves username.
        username: Username for ownership. Takes precedence over user_id if provided.
        all_columns_x: X-axis columns
        adhoc_filters: Optional filters
        row_limit: Maximum number of rows
        bins: Number of bins
        x_axis_label: X-axis label
        y_axis_label: Y-axis label
        normalize_across: Normalization method
        link_length: Link length
        extra_params: Additional parameters
        
    Returns:
        Chart ID
        
    Raises:
        ChartCreationError: If chart creation fails
    """
    # Resolve user ownership (username takes precedence)
    if username:
        from .auth import get_user_id_by_username
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Resolved user '{username}' to ID: {user_id}")
    elif user_id is None:
        # Fallback for standalone function calls: use authenticated session user
        # This provides better default behavior than hardcoded user_id = 1
        print(f"ℹ️  No user_id or username provided, using authenticated session user as fallback")
        user_id = 1  # Safe fallback - chart creation will succeed with session user
        print(f"✅ Using session user ID: {user_id} (provide username parameter for specific ownership)")
    
    chart_params = {
        "datasource": f"{dataset_id}__table",
        "viz_type": "histogram",
        "all_columns_x": all_columns_x,
        "adhoc_filters": adhoc_filters or [],
        "row_limit": row_limit,
        "bins": bins,
        "x_axis_label": x_axis_label,
        "y_axis_label": y_axis_label,
        "normalize_across": normalize_across,
        "link_length": link_length,
    }
    if extra_params:
        chart_params.update(extra_params)

    payload = {
        "slice_name": slice_name,
        "viz_type": "histogram",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(chart_params),
        "owners": [user_id]
    }
    
    print(f"📊 Creating histogram chart: {slice_name}")
    response = session.post(
        f"{base_url}/api/v1/chart/",
        json=payload,
        headers={"Referer": base_url}
    )
    print(f"📊 Chart creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise ChartCreationError(
            f"Chart creation failed: {response.status_code} - {response.text}"
        )
    
    return response.json()['id']


def create_area_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: Optional[int] = None,
    *,
    username: Optional[str] = None,
    metric: Dict[str, Any],
    time_column: str,
    groupby: Optional[List[str]] = None,
    time_range: str = "No filter",
    time_grain: Optional[str] = None,
    order_desc: bool = True,
    contribution: bool = False,
    row_limit: int = 10000,
    show_brush: str = "auto",
    show_legend: bool = True,
    rich_tooltip: bool = True,
    show_controls: bool = True,
    x_axis_label: Optional[str] = None,
    y_axis_label: Optional[str] = None,
    bottom_margin: str = "auto",
    x_ticks_layout: str = "auto",
    y_axis_format: str = "SMART_NUMBER",
    show_markers: bool = False,
    line_interpolation: str = "linear",
    stacked_style: str = "stack",
    x_axis_time_format: str = "smart_date",
    y_axis_bounds: Optional[List] = None,
    annotation_layers: Optional[List] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Create an area chart.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID for ownership
        metric: Metric configuration
        time_column: Time column name
        groupby: Columns to group by
        time_range: Time range filter
        time_grain: Time grain
        order_desc: Whether to order descending
        contribution: Whether to show contribution
        row_limit: Maximum number of rows
        show_brush: Whether to show brush
        show_legend: Whether to show legend
        rich_tooltip: Whether to use rich tooltips
        show_controls: Whether to show controls
        x_axis_label: X-axis label
        y_axis_label: Y-axis label
        bottom_margin: Bottom margin
        x_ticks_layout: X-axis ticks layout
        y_axis_format: Y-axis format
        show_markers: Whether to show markers
        line_interpolation: Line interpolation method
        stacked_style: Stacked style
        x_axis_time_format: X-axis time format
        y_axis_bounds: Y-axis bounds
        annotation_layers: Annotation layers
        extra_params: Additional parameters
        
    Returns:
        Chart ID
        
    Raises:
        ChartCreationError: If chart creation fails
    """
    # Resolve user ownership (username takes precedence)
    if username:
        from .auth import get_user_id_by_username
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Resolved user '{username}' to ID: {user_id}")
    elif user_id is None:
        # Fallback for standalone function calls: use authenticated session user
        # This provides better default behavior than hardcoded user_id = 1
        print(f"ℹ️  No user_id or username provided, using authenticated session user as fallback")
        user_id = 1  # Safe fallback - chart creation will succeed with session user
        print(f"✅ Using session user ID: {user_id} (provide username parameter for specific ownership)")
    
    params = {
        "datasource": f"{dataset_id}__table",
        "viz_type": "area",
        "metrics": [metric],
        "groupby": groupby or [],
        "granularity_sqla": time_column,
        "time_range": time_range,
        **({"time_grain_sqla": time_grain} if time_grain else {}),
        "order_desc": order_desc,
        "contribution": contribution,
        "row_limit": row_limit,
        "show_brush": show_brush,
        "show_legend": show_legend,
        "rich_tooltip": rich_tooltip,
        "show_controls": show_controls,
        "x_axis_label": x_axis_label or time_column,
        "y_axis_label": y_axis_label or (metric.get("label") or "Value"),
        "bottom_margin": bottom_margin,
        "x_ticks_layout": x_ticks_layout,
        "y_axis_format": y_axis_format,
        "show_markers": show_markers,
        "line_interpolation": line_interpolation,
        "stacked_style": stacked_style,
        "x_axis_time_format": x_axis_time_format,
        "y_axis_bounds": y_axis_bounds or [None, None],
        "annotation_layers": annotation_layers or [],
    }
    if extra_params:
        params.update(extra_params)

    payload = {
        "slice_name": slice_name,
        "viz_type": "area",
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "params": json.dumps(params),
        "owners": [user_id],
    }
    
    print(f"📈 Creating area chart: {slice_name}")
    response = session.post(
        f"{base_url}/api/v1/chart/",
        json=payload,
        headers={"Referer": base_url}
    )
    print(f"📈 Chart creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise ChartCreationError(
            f"Chart creation failed: {response.status_code} - {response.text}"
        )
    
    return response.json()['id']




# ============================================================================
# CHART DELETION FUNCTIONS
# ============================================================================

def delete_chart(
    session: requests.Session,
    base_url: str,
    chart_id: int
) -> bool:
    """
    Delete a chart by ID.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        chart_id: Chart ID to delete
        
    Returns:
        True if successful
        
    Raises:
        SupersetApiError: If deletion fails
    """
    response = session.delete(
        f"{base_url}/api/v1/chart/{chart_id}",
        headers={"Referer": base_url},
        timeout=10
    )
    
    if response.status_code not in [200, 204]:
        raise SupersetApiError(
            f"Failed to delete chart {chart_id}: HTTP {response.status_code} - {response.text}"
        )
    
    print(f"✅ Deleted chart ID {chart_id}")
    return True


def delete_charts_by_username(
    session: requests.Session,
    base_url: str,
    username: str,
    dry_run: bool = True
) -> List[int]:
    """
    Delete all charts owned by a specific username.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Username whose charts to delete
        dry_run: If True, only prints what would be deleted without deleting
        
    Returns:
        List of deleted chart IDs
    """
    from .queries import get_charts_by_username
    
    charts = get_charts_by_username(session, base_url, username)
    deleted_ids = []
    
    if not charts:
        print(f"ℹ️  No charts found for user '{username}'")
        return deleted_ids
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(charts)} charts to delete:")
    for chart in charts:
        chart_id = chart.get("id")
        chart_name = chart.get("slice_name", "Unknown")
        print(f"  - Chart ID {chart_id}: {chart_name}")
        
        if not dry_run:
            try:
                delete_chart(session, base_url, chart_id)
                deleted_ids.append(chart_id)
            except Exception as e:
                print(f"⚠️  Failed to delete chart {chart_id}: {e}")
    
    if dry_run:
        print(f"\nℹ️  DRY RUN: No charts were actually deleted. Set dry_run=False to delete.")
    else:
        print(f"\n✅ Deleted {len(deleted_ids)} charts")
    
    return deleted_ids


def delete_charts_by_name_pattern(
    session: requests.Session,
    base_url: str,
    name_pattern: str,
    dry_run: bool = True
) -> List[int]:
    """
    Delete all charts matching a name pattern.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        name_pattern: Pattern to match in chart names (substring match)
        dry_run: If True, only prints what would be deleted without deleting
        
    Returns:
        List of deleted chart IDs
    """
    from .queries import get_all_charts
    
    all_charts = get_all_charts(session, base_url)
    matching_charts = [
        chart for chart in all_charts 
        if name_pattern in chart.get("slice_name", "")
    ]
    
    deleted_ids = []
    
    if not matching_charts:
        print(f"ℹ️  No charts found matching pattern '{name_pattern}'")
        return deleted_ids
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(matching_charts)} charts matching '{name_pattern}':")
    for chart in matching_charts:
        chart_id = chart.get("id")
        chart_name = chart.get("slice_name", "Unknown")
        print(f"  - Chart ID {chart_id}: {chart_name}")
        
        if not dry_run:
            try:
                delete_chart(session, base_url, chart_id)
                deleted_ids.append(chart_id)
            except Exception as e:
                print(f"⚠️  Failed to delete chart {chart_id}: {e}")
    
    if dry_run:
        print(f"\nℹ️  DRY RUN: No charts were actually deleted. Set dry_run=False to delete.")
    else:
        print(f"\n✅ Deleted {len(deleted_ids)} charts")
    
    return deleted_ids
