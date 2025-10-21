"""Dataset management and deletion for Superset."""

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
    response = session.post(
        f"{base_url}/api/v1/dataset/",
        json=payload,
        headers={"Referer": base_url}
    )
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
    response = session.put(
        f"{base_url}/api/v1/dataset/{dataset_id}/refresh",
        headers={"Referer": base_url}
    )
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
        json={"main_dttm_col": time_column},
        headers={"Referer": base_url}
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


# ============================================================================
# DATASET DELETION FUNCTIONS
# ============================================================================

def delete_dataset(
    session: requests.Session,
    base_url: str,
    dataset_id: int
) -> bool:
    """
    Delete a dataset by ID.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dataset_id: Dataset ID to delete
        
    Returns:
        True if successful
        
    Raises:
        SupersetApiError: If deletion fails
    """
    response = session.delete(
        f"{base_url}/api/v1/dataset/{dataset_id}",
        headers={"Referer": base_url},
        timeout=10
    )
    
    if response.status_code not in [200, 204]:
        raise SupersetApiError(
            f"Failed to delete dataset {dataset_id}: HTTP {response.status_code} - {response.text}"
        )
    
    print(f"✅ Deleted dataset ID {dataset_id}")
    return True


def delete_datasets_by_name_pattern(
    session: requests.Session,
    base_url: str,
    name_pattern: str,
    dry_run: bool = True
) -> List[int]:
    """
    Delete all datasets matching a name pattern.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        name_pattern: Pattern to match in dataset names (substring match)
        dry_run: If True, only prints what would be deleted without deleting
        
    Returns:
        List of deleted dataset IDs
    """
    from .queries import get_all_datasets
    
    all_datasets = get_all_datasets(session, base_url)
    matching_datasets = [
        dataset for dataset in all_datasets 
        if name_pattern in dataset.get("table_name", "")
    ]
    
    deleted_ids = []
    
    if not matching_datasets:
        print(f"ℹ️  No datasets found matching pattern '{name_pattern}'")
        return deleted_ids
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(matching_datasets)} datasets matching '{name_pattern}':")
    for dataset in matching_datasets:
        dataset_id = dataset.get("id")
        table_name = dataset.get("table_name", "Unknown")
        schema = dataset.get("schema", "")
        print(f"  - Dataset ID {dataset_id}: {schema}.{table_name}")
        
        if not dry_run:
            try:
                delete_dataset(session, base_url, dataset_id)
                deleted_ids.append(dataset_id)
            except Exception as e:
                print(f"⚠️  Failed to delete dataset {dataset_id}: {e}")
    
    if dry_run:
        print(f"\nℹ️  DRY RUN: No datasets were actually deleted. Set dry_run=False to delete.")
    else:
        print(f"\n✅ Deleted {len(deleted_ids)} datasets")
    
    return deleted_ids


def add_dataset_owner(
    session: requests.Session,
    base_url: str,
    dataset_id: int,
    username: str
) -> None:
    """
    Add an owner to a dataset without removing existing owners.
    
    This function fetches the current dataset owners, adds the specified user
    to the owner list (if not already present), and updates the dataset.
    
    Args:
        session: Authenticated requests session (requires admin privileges)
        base_url: Superset base URL
        dataset_id: Dataset ID to update
        username: Username to add as owner
        
    Raises:
        SupersetApiError: If operation fails
        
    Example:
        >>> from superset_toolkit import SupersetClient
        >>> from superset_toolkit.datasets import add_dataset_owner
        >>> 
        >>> client = SupersetClient()  # Login as admin
        >>> add_dataset_owner(
        ...     client.session, 
        ...     client.base_url, 
        ...     dataset_id=123, 
        ...     username="data_analyst"
        ... )
    """
    from .auth import get_user_id_by_username
    
    # Get user ID from username
    user_id = get_user_id_by_username(session, base_url, username)
    
    # Get current dataset info to retrieve existing owners
    print(f"📊 Fetching current dataset info for dataset {dataset_id}...")
    get_response = session.get(
        f"{base_url}/api/v1/dataset/{dataset_id}",
        headers={"Referer": base_url}
    )
    
    if get_response.status_code != 200:
        raise SupersetApiError(
            f"Failed to fetch dataset {dataset_id}: {get_response.status_code}",
            get_response.status_code,
            get_response.text
        )
    
    dataset_data = get_response.json()
    result = dataset_data.get("result", {})
    current_owners = result.get("owners", [])
    
    # Extract current owner IDs
    current_owner_ids = [owner["id"] for owner in current_owners if isinstance(owner, dict) and "id" in owner]
    
    # Check if user is already an owner
    if user_id in current_owner_ids:
        print(f"ℹ️  User '{username}' (ID: {user_id}) is already an owner of dataset {dataset_id}")
        return
    
    # Add new owner to the list
    updated_owner_ids = current_owner_ids + [user_id]
    
    print(f"👥 Adding owner '{username}' (ID: {user_id}) to dataset {dataset_id}")
    print(f"   Current owners: {current_owner_ids}")
    print(f"   Updated owners: {updated_owner_ids}")
    
    # Update dataset with complete owner list
    payload = {
        "owners": updated_owner_ids
    }
    
    patch_response = session.put(
        f"{base_url}/api/v1/dataset/{dataset_id}",
        json=payload,
        headers={"Referer": base_url}
    )
    
    if patch_response.status_code not in [200, 201]:
        raise SupersetApiError(
            f"Failed to add owner to dataset {dataset_id}: {patch_response.status_code}",
            patch_response.status_code,
            patch_response.text
        )
    
    print(f"✅ Successfully added '{username}' as owner to dataset {dataset_id}")
