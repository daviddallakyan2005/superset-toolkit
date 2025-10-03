"""Dashboard creation and management for Superset."""

import json
from typing import List, Dict, Any, Optional

import requests

from .exceptions import DashboardError
from .ensure import get_dashboard_id_by_slug


def create_dashboard(
    session: requests.Session,
    base_url: str,
    title: str,
    slug: str
) -> int:
    """
    Create a new dashboard.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        title: Dashboard title
        slug: Dashboard slug
        
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
    
    response = session.post(f"{base_url}/api/v1/dashboard/", json=payload)
    
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
    slug: str
) -> int:
    """
    Ensure a dashboard exists, creating it if necessary.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        title: Dashboard title
        slug: Dashboard slug
        
    Returns:
        Dashboard ID
    """
    existing = get_dashboard_id_by_slug(session, base_url, slug)
    if existing:
        return existing
    
    return create_dashboard(session, base_url, title, slug)


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
        json={"css": custom_css}
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
        json={"position_json": json.dumps(position_json)}
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
        )
        
        if response.status_code not in [200, 201]:
            # Fallback structure some versions expect
            response2 = session.put(
                f"{base_url}/api/v1/chart/{chart_id}",
                json={"dashboards": [{"id": dashboard_id}]},
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
