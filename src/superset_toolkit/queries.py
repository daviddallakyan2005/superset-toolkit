"""Query functions for retrieving charts, dashboards, and filtering by owners/datasets."""

import json
from typing import List, Dict, Any, Optional

import requests

from .exceptions import SupersetApiError


def get_all_charts(
    session: requests.Session,
    base_url: str,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all charts from Superset with full owner information.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        page_size: Number of charts per page
        
    Returns:
        List of chart objects with full metadata including owners
    """
    query = json.dumps({"page_size": page_size})
    
    response = session.get(
        f"{base_url}/api/v1/chart/",
        params={"q": query},
        headers={"Referer": base_url},
        timeout=30
    )
    
    if response.status_code != 200:
        raise SupersetApiError(
            f"Failed to retrieve charts: HTTP {response.status_code} - {response.text}"
        )
    
    data = response.json()
    charts = data.get("result", [])
    
    print(f"✅ Retrieved {len(charts)} charts")
    return charts


def get_charts_by_username(
    session: requests.Session,
    base_url: str,
    username: str,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all charts owned by a specific username.
    
    This function first resolves the username to user_id, then filters by user_id.
    This is more reliable than trying to match username fields in the owners array.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Username to filter by
        page_size: Number of charts per page
        
    Returns:
        List of charts owned by the specified user
    """
    from .auth import get_user_id_by_username
    
    try:
        # First resolve username to user_id
        user_id = get_user_id_by_username(session, base_url, username)
        
        # Then use the reliable user_id-based filtering
        return get_charts_by_user_id(session, base_url, user_id, page_size)
        
    except Exception as e:
        # Fallback to manual filtering if user lookup fails
        print(f"⚠️  User lookup failed ({e}), trying manual filtering...")
        
        all_charts = get_all_charts(session, base_url, page_size)
        
        filtered_charts = []
        for chart in all_charts:
            owners = chart.get("owners", [])
            created_by = chart.get("created_by", {})
            
            # Check if username is in owners or created_by
            # Note: owners array may have 'username' field OR use first_name/last_name
            is_owner = any(
                (owner.get("username") == username or 
                 owner.get("first_name") == username or
                 owner.get("last_name") == username)
                for owner in owners
                if isinstance(owner, dict)
            )
            is_creator = created_by.get("username") == username
            
            if is_owner or is_creator:
                filtered_charts.append(chart)
        
        print(f"✅ Found {len(filtered_charts)} charts owned by '{username}' (via fallback)")
        return filtered_charts


def get_charts_by_user_id(
    session: requests.Session,
    base_url: str,
    user_id: int,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all charts owned by a specific user ID.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        user_id: User ID to filter by
        page_size: Number of charts per page
        
    Returns:
        List of charts owned by the specified user
    """
    all_charts = get_all_charts(session, base_url, page_size)
    
    # Filter charts by user_id in owners list
    filtered_charts = []
    for chart in all_charts:
        owners = chart.get("owners", [])
        created_by = chart.get("created_by", {})
        
        # Check if user_id is in owners or created_by
        is_owner = any(
            owner.get("id") == user_id
            for owner in owners
            if isinstance(owner, dict)
        )
        is_creator = created_by.get("id") == user_id
        
        if is_owner or is_creator:
            filtered_charts.append(chart)
    
    print(f"✅ Found {len(filtered_charts)} charts owned by user ID {user_id}")
    return filtered_charts


def get_charts_by_dataset(
    session: requests.Session,
    base_url: str,
    dataset_id: int,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all charts using a specific dataset.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dataset_id: Dataset ID to filter by
        page_size: Number of charts per page
        
    Returns:
        List of charts using the specified dataset
    """
    # Server-side filter for better performance
    query = json.dumps({
        "filters": [{"col": "datasource_id", "opr": "eq", "value": dataset_id}],
        "page_size": page_size
    })
    
    response = session.get(
        f"{base_url}/api/v1/chart/",
        params={"q": query},
        headers={"Referer": base_url},
        timeout=30
    )
    
    if response.status_code != 200:
        raise SupersetApiError(
            f"Failed to retrieve charts: HTTP {response.status_code} - {response.text}"
        )
    
    data = response.json()
    charts = data.get("result", [])
    
    print(f"✅ Found {len(charts)} charts using dataset ID {dataset_id}")
    return charts




def get_user_info_from_charts(
    session: requests.Session,
    base_url: str,
    username: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Extract user information from chart metadata.
    This is a fallback method when /api/v1/user or /api/v1/security/users is not available.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Optional username to filter by. If None, returns all unique users.
        
    Returns:
        List of user objects with id, username, first_name, last_name
    """
    all_charts = get_all_charts(session, base_url)
    
    users_map = {}
    
    for chart in all_charts:
        # Extract from owners
        for owner in chart.get("owners", []):
            if isinstance(owner, dict) and owner.get("id"):
                uid = owner["id"]
                if uid not in users_map:
                    users_map[uid] = {
                        "id": uid,
                        "username": owner.get("username", ""),
                        "first_name": owner.get("first_name", ""),
                        "last_name": owner.get("last_name", "")
                    }
        
        # Extract from created_by
        created_by = chart.get("created_by", {})
        if isinstance(created_by, dict) and created_by.get("id"):
            uid = created_by["id"]
            if uid not in users_map:
                users_map[uid] = {
                    "id": uid,
                    "username": created_by.get("username", ""),
                    "first_name": created_by.get("first_name", ""),
                    "last_name": created_by.get("last_name", "")
                }
    
    users = list(users_map.values())
    
    # Filter by username if specified
    if username:
        users = [u for u in users if u["username"] == username]
        if users:
            print(f"✅ Found user '{username}' from chart metadata: ID {users[0]['id']}")
        else:
            print(f"⚠️  User '{username}' not found in any chart metadata")
    else:
        print(f"✅ Extracted {len(users)} unique users from chart metadata")
    
    return users


# ============================================================================
# DASHBOARD QUERIES
# ============================================================================

def get_all_dashboards(
    session: requests.Session,
    base_url: str,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all dashboards from Superset with full owner information.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        page_size: Number of dashboards per page
        
    Returns:
        List of dashboard objects with full metadata including owners
    """
    query = json.dumps({"page_size": page_size})
    
    response = session.get(
        f"{base_url}/api/v1/dashboard/",
        params={"q": query},
        headers={"Referer": base_url},
        timeout=30
    )
    
    if response.status_code != 200:
        raise SupersetApiError(
            f"Failed to retrieve dashboards: HTTP {response.status_code} - {response.text}"
        )
    
    data = response.json()
    dashboards = data.get("result", [])
    
    print(f"✅ Retrieved {len(dashboards)} dashboards")
    return dashboards


def get_dashboards_by_username(
    session: requests.Session,
    base_url: str,
    username: str,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all dashboards owned by a specific username.
    
    This function first resolves the username to user_id, then filters by user_id.
    This is more reliable than trying to match username fields in the owners array.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Username to filter by
        page_size: Number of dashboards per page
        
    Returns:
        List of dashboards owned by the specified user
    """
    from .auth import get_user_id_by_username
    
    try:
        # First resolve username to user_id
        user_id = get_user_id_by_username(session, base_url, username)
        
        # Then filter by user_id
        all_dashboards = get_all_dashboards(session, base_url, page_size)
        
        filtered_dashboards = []
        for dashboard in all_dashboards:
            owners = dashboard.get("owners", [])
            created_by = dashboard.get("created_by", {})
            
            # Check if user_id is in owners or created_by
            is_owner = any(
                owner.get("id") == user_id
                for owner in owners
                if isinstance(owner, dict)
            )
            is_creator = created_by.get("id") == user_id
            
            if is_owner or is_creator:
                filtered_dashboards.append(dashboard)
        
        print(f"✅ Found {len(filtered_dashboards)} dashboards owned by '{username}' (user ID: {user_id})")
        return filtered_dashboards
        
    except Exception as e:
        # Fallback to manual filtering if user lookup fails
        print(f"⚠️  User lookup failed ({e}), trying manual filtering...")
        
        all_dashboards = get_all_dashboards(session, base_url, page_size)
        
        filtered_dashboards = []
        for dashboard in all_dashboards:
            owners = dashboard.get("owners", [])
            created_by = dashboard.get("created_by", {})
            
            # Check if username is in owners or created_by
            is_owner = any(
                (owner.get("username") == username or 
                 owner.get("first_name") == username or
                 owner.get("last_name") == username)
                for owner in owners
                if isinstance(owner, dict)
            )
            is_creator = created_by.get("username") == username
            
            if is_owner or is_creator:
                filtered_dashboards.append(dashboard)
        
        print(f"✅ Found {len(filtered_dashboards)} dashboards owned by '{username}' (via fallback)")
        return filtered_dashboards


# ============================================================================
# DATASET QUERIES
# ============================================================================

def get_all_datasets(
    session: requests.Session,
    base_url: str,
    page_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Get all datasets from Superset.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        page_size: Number of datasets per page
        
    Returns:
        List of dataset objects
    """
    query = json.dumps({"page_size": page_size})
    
    response = session.get(
        f"{base_url}/api/v1/dataset/",
        params={"q": query},
        headers={"Referer": base_url},
        timeout=30
    )
    
    if response.status_code != 200:
        raise SupersetApiError(
            f"Failed to retrieve datasets: HTTP {response.status_code} - {response.text}"
        )
    
    data = response.json()
    datasets = data.get("result", [])
    
    print(f"✅ Retrieved {len(datasets)} datasets")
    return datasets



