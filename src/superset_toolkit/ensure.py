"""Ensure patterns for idempotent Superset resource management."""

import json
from typing import Optional, List, Dict, Any, Callable

import requests

from .exceptions import SupersetApiError


def _api_get_first_id(
    session: requests.Session, 
    base_url: str, 
    endpoint: str, 
    filters: List[Dict[str, Any]]
) -> Optional[int]:
    """
    Generic helper to get the first ID from a filtered API endpoint.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        endpoint: API endpoint (e.g., "/api/v1/dataset/")
        filters: List of filter dictionaries
        
    Returns:
        First matching ID or None
    """
    query = json.dumps({"filters": filters})
    response = session.get(f"{base_url}{endpoint}", params={"q": query})
    
    if response.status_code != 200:
        return None
        
    result = response.json()
    return result['result'][0]['id'] if result.get('result') else None


def get_database_id_by_name(session: requests.Session, base_url: str, name: str) -> int:
    """
    Get database ID by name.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        name: Database name
        
    Returns:
        Database ID
        
    Raises:
        SupersetApiError: If database not found
    """
    response = session.get(f"{base_url}/api/v1/database/")
    
    if response.status_code != 200:
        raise SupersetApiError(
            f"Failed to get databases: {response.status_code}",
            response.status_code,
            response.text
        )
    
    result = response.json()
    for db in result['result']:
        if db['database_name'] == name:
            return db['id']
    
    raise SupersetApiError(f"Database '{name}' not found")


def get_dataset_id(
    session: requests.Session, 
    base_url: str, 
    table_name: str, 
    schema: str
) -> Optional[int]:
    """
    Get dataset ID by table name and schema.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        table_name: Table name
        schema: Schema name
        
    Returns:
        Dataset ID or None if not found
    """
    return _api_get_first_id(
        session,
        base_url,
        "/api/v1/dataset/",
        [
            {"col": "table_name", "opr": "eq", "value": table_name},
            {"col": "schema", "opr": "eq", "value": schema},
        ],
    )


def get_chart_id(session: requests.Session, base_url: str, slice_name: str) -> Optional[int]:
    """
    Get chart ID by name.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        
    Returns:
        Chart ID or None if not found
    """
    return _api_get_first_id(
        session,
        base_url,
        "/api/v1/chart/",
        [{"col": "slice_name", "opr": "eq", "value": slice_name}],
    )


def get_dashboard_id_by_slug(
    session: requests.Session, 
    base_url: str, 
    slug: str
) -> Optional[int]:
    """
    Get dashboard ID by slug.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slug: Dashboard slug
        
    Returns:
        Dashboard ID or None if not found
    """
    return _api_get_first_id(
        session,
        base_url,
        "/api/v1/dashboard/",
        [{"col": "slug", "opr": "eq", "value": slug}],
    )


def find_chart_id_by_name_dataset_owner(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    dataset_id: int,
    user_id: int
) -> Optional[int]:
    """
    Find chart ID by name, dataset, and owner.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        dataset_id: Dataset ID
        user_id: User ID
        
    Returns:
        Chart ID or None if not found
    """
    # Narrow by name via server-side filter, then match dataset and owner client-side
    query = json.dumps({
        "filters": [{"col": "slice_name", "opr": "eq", "value": slice_name}], 
        "page_size": 1000
    })
    response = session.get(f"{base_url}/api/v1/chart/", params={"q": query})
    
    if response.status_code != 200:
        return None
    
    result = response.json()
    for item in (result.get('result') or []):
        ds_id = item.get('datasource_id')
        created_by = item.get('created_by') or {}
        owners = item.get('owners') or []
        owner_ids = [o.get('id') for o in owners if isinstance(o, dict) and o.get('id') is not None]
        
        if ds_id == dataset_id and (created_by.get('id') == user_id or user_id in owner_ids):
            return item.get('id')
    
    return None


def ensure_chart(
    session: requests.Session,
    base_url: str,
    slice_name: str,
    creator_fn: Callable,
    dataset_id: int,
    user_id: int,
    create_kwargs: Optional[Dict[str, Any]] = None
) -> int:
    """
    Ensure a chart exists, creating it if necessary.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        slice_name: Chart name
        creator_fn: Function to create the chart
        dataset_id: Dataset ID
        user_id: User ID
        create_kwargs: Additional kwargs for creator function
        
    Returns:
        Chart ID
    """
    existing = find_chart_id_by_name_dataset_owner(session, base_url, slice_name, dataset_id, user_id)
    
    if existing:
        print(f"📊 Found existing chart '{slice_name}' with ID: {existing}")
        # Delete the existing chart since it likely has invalid configuration
        print("📊 Deleting existing chart to recreate with proper metrics...")
        delete_response = session.delete(f"{base_url}/api/v1/chart/{existing}")
        print(f"📊 Delete response status: {delete_response.status_code}")
        if delete_response.status_code not in [200, 204, 404]:
            print(f"⚠️ Failed to delete chart {existing}: {delete_response.text}")
    
    # Create new chart with proper configuration
    create_kwargs = create_kwargs or {}
    return creator_fn(session, base_url, slice_name, dataset_id, user_id, **create_kwargs)
