"""Dashboard creation, management, and deletion for Superset."""

import json
from typing import List, Dict, Any, Optional

import requests

from .exceptions import DashboardError, SupersetApiError
from .ensure import get_dashboard_id_by_slug


def create_dashboard(
    session: requests.Session,
    base_url: str,
    title: str,
    slug: str,
    user_id: Optional[int] = None
) -> int:
    """
    Create a new dashboard.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        title: Dashboard title
        slug: Dashboard slug
        user_id: Optional user ID for ownership. If None, uses authenticated user.
        
    Returns:
        Dashboard ID
        
    Raises:
        DashboardError: If dashboard creation fails
    """
    # Create an empty dashboard without placing charts at creation time
    position_json = {
        "GRID_ID": {"children": [], "id": "GRID_ID", "type": "GRID"},
        "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"}
    }
    
    payload = {
        "dashboard_title": title,
        "slug": slug,
        "position_json": json.dumps(position_json),
        "published": True
    }
    
    # Set ownership if user_id is provided
    if user_id is not None:
        payload["owners"] = [user_id]
    
    response = session.post(
        f"{base_url}/api/v1/dashboard/",
        json=payload,
        headers={"Referer": base_url}
    )
    
    if response.status_code != 201:
        raise DashboardError(
            f"Dashboard creation failed: {response.status_code} - {response.text}"
        )
    
    result = response.json()
    return result['id']


def ensure_dashboard(
    session: requests.Session,
    base_url: str,
    title: str,
    slug: str,
    user_id: Optional[int] = None
) -> int:
    """
    Ensure a dashboard exists, creating it if necessary.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        title: Dashboard title
        slug: Dashboard slug
        user_id: Optional user ID for ownership. If None, uses authenticated user.
        
    Returns:
        Dashboard ID
    """
    existing = get_dashboard_id_by_slug(session, base_url, slug)
    if existing:
        return existing
    
    return create_dashboard(session, base_url, title, slug, user_id)


def create_markdown_component(
    session: requests.Session,
    base_url: str,
    title: str,
    content: str
) -> int:
    """
    Create a markdown component that can render HTML.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        title: Component title
        content: HTML/Markdown content
        
    Returns:
        Component ID
        
    Raises:
        DashboardError: If component creation fails
    """
    payload = {
        "slice_name": title,
        "viz_type": "markup",
        "params": json.dumps({
            "markup_type": "html",  # Enable HTML rendering
            "code": content,  # HTML/Markdown content
            "viz_type": "markup"
        })
    }
    
    print(f"📝 Creating markdown component: {title}")
    response = session.post(f"{base_url}/api/v1/chart/", json=payload)
    print(f"📝 Markdown creation response status: {response.status_code}")
    
    if response.status_code != 201:
        raise DashboardError(
            f"Markdown component creation failed: {response.status_code} - {response.text}"
        )
    
    result = response.json()
    return result['id']


def update_dashboard_css(
    session: requests.Session,
    base_url: str,
    dashboard_id: int,
    custom_css: str
) -> None:
    """
    Update dashboard with custom CSS.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dashboard_id: Dashboard ID
        custom_css: Custom CSS to apply
    """
    print("🎨 Updating dashboard CSS...")
    response = session.put(
        f"{base_url}/api/v1/dashboard/{dashboard_id}",
        json={"css": custom_css},
        headers={"Referer": base_url}
    )
    print(f"🎨 CSS update response status: {response.status_code}")
    
    if response.status_code not in [200, 204]:
        print(f"⚠️ Failed to update CSS: {response.text}")
    else:
        print("✅ Dashboard CSS updated successfully")


def _get_dashboard_position_json(
    session: requests.Session,
    base_url: str,
    dashboard_id: int
) -> Dict[str, Any]:
    """
    Get the current dashboard position JSON.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dashboard_id: Dashboard ID
        
    Returns:
        Position JSON dictionary
    """
    response = session.get(f"{base_url}/api/v1/dashboard/{dashboard_id}")
    result = response.json()
    pos = result['result'].get('position_json') or {}
    
    if isinstance(pos, str):
        try:
            pos = json.loads(pos)
        except Exception:
            pos = {}
    
    print(f"📊 Current dashboard position_json: {json.dumps(pos, indent=2)}")
    return pos


def _update_dashboard_position_json(
    session: requests.Session,
    base_url: str,
    dashboard_id: int,
    position_json: Dict[str, Any]
) -> None:
    """
    Update the dashboard position JSON.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dashboard_id: Dashboard ID
        position_json: New position JSON
    """
    session.put(
        f"{base_url}/api/v1/dashboard/{dashboard_id}",
        json={"position_json": json.dumps(position_json)},
        headers={"Referer": base_url}
    )


def link_chart_to_dashboard(
    session: requests.Session,
    base_url: str,
    chart_id: int,
    dashboard_id: int
) -> None:
    """
    Establish chart ↔ dashboard relationship.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        chart_id: Chart ID
        dashboard_id: Dashboard ID
    """
    try:
        print(f"🔗 Linking chart {chart_id} to dashboard {dashboard_id}...")
        response = session.put(
            f"{base_url}/api/v1/chart/{chart_id}",
            json={"dashboards": [dashboard_id]},
            headers={"Referer": base_url}
        )
        
        if response.status_code not in [200, 201]:
            # Fallback structure some versions expect
            response2 = session.put(
                f"{base_url}/api/v1/chart/{chart_id}",
                json={"dashboards": [{"id": dashboard_id}]},
                headers={"Referer": base_url}
            )
            if response2.status_code not in [200, 201]:
                print(f"⚠️ Failed to link chart {chart_id} to dashboard {dashboard_id}: "
                      f"{response.status_code} {response.text} / "
                      f"{response2.status_code} {response2.text}")
            else:
                print("✅ Chart linked via fallback payload")
        else:
            print("✅ Chart linked")
    except Exception as e:
        print(f"⚠️ Error linking chart {chart_id} to dashboard {dashboard_id}: {e}")


def add_charts_to_dashboard(
    session: requests.Session,
    base_url: str,
    dashboard_id: int,
    chart_ids: List[int]
) -> None:
    """
    Add charts to dashboard layout (2 charts per row).
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dashboard_id: Dashboard ID
        chart_ids: List of chart IDs to add
    """
    # Rebuild a clean position_json with 2 charts per row
    print("📐 Rebuilding dashboard layout (2 charts per row)...")
    pos = {
        "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"},
        "GRID_ID": {"children": [], "id": "GRID_ID", "type": "GRID"},
    }

    # Chunk charts into rows of 2
    row_index = 0
    for i in range(0, len(chart_ids), 2):
        row_index += 1
        row_id = f"ROW-{row_index}"
        pos[row_id] = {
            "children": [],
            "id": row_id,
            "type": "ROW",
            "meta": {"background": "BACKGROUND_TRANSPARENT"}
        }
        pos["GRID_ID"]["children"].append(row_id)

        row_chart_ids = chart_ids[i:i+2]
        for cid in row_chart_ids:
            chart_key = f"CHART-{cid}"
            pos[chart_key] = {
                "children": [],
                "id": chart_key,
                "meta": {"chartId": cid, "width": 6, "height": 50},
                "type": "CHART",
            }
            pos[row_id]["children"].append(chart_key)

    print(f"📊 Updated dashboard position_json: {json.dumps(pos, indent=2)}")
    _update_dashboard_position_json(session, base_url, dashboard_id, pos)

    # Also ensure chart ↔ dashboard relation for API responses to include chart definitions
    for cid in chart_ids:
        link_chart_to_dashboard(session, base_url, cid, dashboard_id)




# ============================================================================
# DASHBOARD DELETION FUNCTIONS
# ============================================================================

def delete_dashboard(
    session: requests.Session,
    base_url: str,
    dashboard_id: int
) -> bool:
    """
    Delete a dashboard by ID.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        dashboard_id: Dashboard ID to delete
        
    Returns:
        True if successful
        
    Raises:
        SupersetApiError: If deletion fails
    """
    response = session.delete(
        f"{base_url}/api/v1/dashboard/{dashboard_id}",
        headers={"Referer": base_url},
        timeout=10
    )
    
    if response.status_code not in [200, 204]:
        raise SupersetApiError(
            f"Failed to delete dashboard {dashboard_id}: HTTP {response.status_code} - {response.text}"
        )
    
    print(f"✅ Deleted dashboard ID {dashboard_id}")
    return True


def delete_dashboards_by_username(
    session: requests.Session,
    base_url: str,
    username: str,
    dry_run: bool = True
) -> List[int]:
    """
    Delete all dashboards owned by a specific username.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Username whose dashboards to delete
        dry_run: If True, only prints what would be deleted without deleting
        
    Returns:
        List of deleted dashboard IDs
    """
    from .queries import get_dashboards_by_username
    
    dashboards = get_dashboards_by_username(session, base_url, username)
    deleted_ids = []
    
    if not dashboards:
        print(f"ℹ️  No dashboards found for user '{username}'")
        return deleted_ids
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(dashboards)} dashboards to delete:")
    for dashboard in dashboards:
        dashboard_id = dashboard.get("id")
        dashboard_title = dashboard.get("dashboard_title", "Unknown")
        print(f"  - Dashboard ID {dashboard_id}: {dashboard_title}")
        
        if not dry_run:
            try:
                delete_dashboard(session, base_url, dashboard_id)
                deleted_ids.append(dashboard_id)
            except Exception as e:
                print(f"⚠️  Failed to delete dashboard {dashboard_id}: {e}")
    
    if dry_run:
        print(f"\nℹ️  DRY RUN: No dashboards were actually deleted. Set dry_run=False to delete.")
    else:
        print(f"\n✅ Deleted {len(deleted_ids)} dashboards")
    
    return deleted_ids


def delete_dashboards_by_name_pattern(
    session: requests.Session,
    base_url: str,
    name_pattern: str,
    dry_run: bool = True
) -> List[int]:
    """
    Delete all dashboards matching a name pattern.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        name_pattern: Pattern to match in dashboard titles (substring match)
        dry_run: If True, only prints what would be deleted without deleting
        
    Returns:
        List of deleted dashboard IDs
    """
    from .queries import get_all_dashboards
    
    all_dashboards = get_all_dashboards(session, base_url)
    matching_dashboards = [
        dashboard for dashboard in all_dashboards 
        if name_pattern in dashboard.get("dashboard_title", "")
    ]
    
    deleted_ids = []
    
    if not matching_dashboards:
        print(f"ℹ️  No dashboards found matching pattern '{name_pattern}'")
        return deleted_ids
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(matching_dashboards)} dashboards matching '{name_pattern}':")
    for dashboard in matching_dashboards:
        dashboard_id = dashboard.get("id")
        dashboard_title = dashboard.get("dashboard_title", "Unknown")
        print(f"  - Dashboard ID {dashboard_id}: {dashboard_title}")
        
        if not dry_run:
            try:
                delete_dashboard(session, base_url, dashboard_id)
                deleted_ids.append(dashboard_id)
            except Exception as e:
                print(f"⚠️  Failed to delete dashboard {dashboard_id}: {e}")
    
    if dry_run:
        print(f"\nℹ️  DRY RUN: No dashboards were actually deleted. Set dry_run=False to delete.")
    else:
        print(f"\n✅ Deleted {len(deleted_ids)} dashboards")
    
    return deleted_ids
