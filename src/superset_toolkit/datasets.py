"""Dataset management for Superset."""

from typing import List

import requests

from .exceptions import SupersetApiError, DatasetNotFoundError
from .ensure import get_dataset_id


def create_dataset(
    session: requests.Session,
    base_url: str,
    database_id: int,
    schema: str,
    table_name: str
) -> int:
    """
    Create a new dataset in Superset.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        database_id: Database ID
        schema: Schema name
        table_name: Table name
        
    Returns:
        Dataset ID
        
    Raises:
        SupersetApiError: If dataset creation fails
    """
    payload = {
        "database": database_id,
        "schema": schema,
        "table_name": table_name
    }
    
    print(f"📊 Creating dataset: {schema}.{table_name}")
    response = session.post(f"{base_url}/api/v1/dataset/", json=payload)
    print(f"📊 Dataset creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise SupersetApiError(
            f"Dataset creation failed: {response.status_code}",
            response.status_code,
            response.text
        )
    
    result = response.json()
    # DO NOT log full API responses as they may contain sensitive data
    
    if 'id' not in result:
        raise SupersetApiError(f"Dataset creation response missing 'id': {result}")
    
    return result['id']


def ensure_dataset(
    session: requests.Session,
    base_url: str,
    database_id: int,
    schema: str,
    table_name: str
) -> int:
    """
    Ensure a dataset exists, creating it if necessary.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        database_id: Database ID
        schema: Schema name
        table_name: Table name
        
    Returns:
        Dataset ID
    """
    existing = get_dataset_id(session, base_url, table_name, schema)
    if existing:
        return existing
    
    return create_dataset(session, base_url, database_id, schema, table_name)


def refresh_dataset_metadata(
    session: requests.Session,
    base_url: str,
    dataset_id: int,
    force: bool = True
) -> None:
    """
    Refresh dataset metadata from the underlying table.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dataset_id: Dataset ID
        force: Whether to force refresh
        
    Raises:
        SupersetApiError: If refresh fails
    """
    print(f"🔄 Refreshing dataset metadata for dataset_id={dataset_id}...")
    response = session.put(f"{base_url}/api/v1/dataset/{dataset_id}/refresh")
    print(f"🔄 Dataset refresh status: {response.status_code}")
    
    if response.status_code not in [200, 202, 204]:
        raise SupersetApiError(
            f"Failed to refresh dataset metadata: {response.status_code}",
            response.status_code,
            response.text
        )


def ensure_dataset_main_dttm(
    session: requests.Session,
    base_url: str,
    dataset_id: int,
    time_column: str
) -> None:
    """
    Set the dataset's main datetime column for time-series charts.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dataset_id: Dataset ID
        time_column: Name of the datetime column
    """
    print(f"🕒 Ensuring main datetime column '{time_column}' for dataset {dataset_id}...")
    response = session.put(
        f"{base_url}/api/v1/dataset/{dataset_id}",
        json={"main_dttm_col": time_column}
    )
    print(f"🕒 Set main_dttm_col response: {response.status_code}")
    
    if response.status_code not in [200, 201]:
        print(f"⚠️ Could not set main_dttm_col: {response.text}")


def get_dataset_column_names(
    session: requests.Session,
    base_url: str,
    dataset_id: int
) -> List[str]:
    """
    Get column names for a dataset.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dataset_id: Dataset ID
        
    Returns:
        List of column names
        
    Raises:
        DatasetNotFoundError: If dataset not found or has no columns
    """
    response = session.get(f"{base_url}/api/v1/dataset/{dataset_id}")
    
    if response.status_code != 200:
        raise DatasetNotFoundError(
            f"Failed to fetch dataset columns for {dataset_id}: {response.status_code} {response.text}"
        )
    
    body = response.json() or {}
    result = body.get("result") or body
    cols = result.get("columns") or []
    names = [c.get("column_name") for c in cols if isinstance(c, dict) and c.get("column_name")]
    
    if not names:
        raise DatasetNotFoundError(f"No columns returned for dataset {dataset_id}")
    
    return names
