#!/usr/bin/env python3
"""
Professional Client Usage Example

Demonstrates the enhanced SupersetClient with professional patterns:
- Client-centric operations (no session/base_url repetition)
- Username-aware functions (no manual user ID resolution)
- Composite workflows (complete operations in single calls)
- Context managers with automatic cleanup

Before running:
1. Update the configuration below with your Superset credentials
2. Ensure you have a table named 'media_assets' or update table name
3. Run: python3 professional_client_usage.py
"""

import sys
import os

# For local development - adjust path as needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    print("🚀 Professional SupersetClient Usage Example")
    print("=" * 60)
    
    # Configure connection (update with your details)
    config = Config(
        superset_url="https://your-superset-instance.com",  # Your Superset URL
        username="your-username",                           # Your username
        password="your-secure-password",                    # Your password
        schema="your-schema",                               # Your default schema
        database_name="your-database"                       # Your database name
    )
    
    try:
        # Professional pattern: Context manager with automatic cleanup
        with SupersetClient(config=config) as client:
            
            # Validate connection first
            status = client.validate_connection()
            print(f"✅ Connected: {status['status']}")
            print(f"   User ID: {status['user_id']}")
            print(f"   System charts: {status['chart_count']}")
            
            # ================================================================
            # EXAMPLE 1: Simple Chart Creation (Username-Aware)
            # ================================================================
            print("\n📊 Example 1: Create chart with username")
            
            chart_id = client.create_table_chart(
                name="Professional Example Chart",
                table="your_table_name",  # Update with your table name
                owner="data_analyst",     # Specify owner by username
                columns=["id", "name", "value"],  # Update with your columns
                row_limit=100
            )
            
            print(f"✅ Created chart ID: {chart_id}")
            
            # ================================================================
            # EXAMPLE 2: Dashboard with Automatic Chart Linking
            # ================================================================
            print("\n🖥️ Example 2: Create dashboard with chart linking")
            
            dashboard_id = client.create_dashboard(
                title="Professional Example Dashboard",
                slug="professional-example-dashboard",
                owner="data_analyst",
                charts=["Professional Example Chart"]  # Auto-links by name
            )
            
            print(f"✅ Created dashboard ID: {dashboard_id}")
            print(f"🌐 View at: {client.base_url}/superset/dashboard/professional-example-dashboard/")
            
            # ================================================================
            # EXAMPLE 3: Composite Operations (Multiple Charts + Dashboard)
            # ================================================================
            print("\n🚀 Example 3: Composite operation (dashboard + multiple charts)")
            
            result = client.create_dashboard_with_charts(
                dashboard_title="Composite Example Dashboard",
                slug="composite-example-dashboard",
                chart_configs=[
                    {
                        "name": "Example Table Chart",
                        "table": "your_table_name",
                        "type": "table",
                        "columns": ["id", "title"]
                    },
                    {
                        "name": "Example ID Chart", 
                        "table": "your_table_name",
                        "type": "table",
                        "columns": ["id"]
                    }
                ],
                owner="admin"
            )
            
            print(f"✅ Created dashboard {result['dashboard_id']} with charts {result['chart_ids']}")
            
            # ================================================================
            # EXAMPLE 4: Resource Queries
            # ================================================================
            print("\n🔍 Example 4: Query user resources")
            
            # Get all charts for current user
            user_charts = client.get_charts(owner="data_analyst")
            print(f"User has {len(user_charts)} charts")
            
            # Get comprehensive summary
            summary = client.get_user_summary("data_analyst")
            print(f"User summary: {summary['summary']}")
            
            # ================================================================
            # EXAMPLE 5: Cleanup (Optional)
            # ================================================================
            print("\n🧹 Example 5: Resource cleanup")
            
            # Preview what would be deleted
            cleanup_preview = client.cleanup_user("data_analyst", dry_run=True)
            print(f"Would delete: {len(cleanup_preview['chart_ids'])} charts, {len(cleanup_preview['dashboard_ids'])} dashboards")
            
            # Uncomment to actually clean up:
            # client.cleanup_user("admin", dry_run=False)
            
            print("\n✅ Professional client example completed!")
            print("💡 Check the Superset UI to see the created charts and dashboards")
            
    except SupersetToolkitError as e:
        print(f"❌ Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
