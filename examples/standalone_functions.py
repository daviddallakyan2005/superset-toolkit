#!/usr/bin/env python3
"""
Enhanced Standalone Functions Example

Demonstrates the enhanced standalone functions with username support:
- All chart functions now accept `username` parameter
- No manual user ID resolution required
- Backward compatible with existing code

Before running:
1. Update the configuration below
2. Ensure you have the required tables
3. Run: python3 standalone_functions.py
"""

import sys
import os

# For local development - adjust path as needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.charts import create_table_chart, create_pie_chart, create_histogram_chart
from superset_toolkit.dashboard import ensure_dashboard, add_charts_to_dashboard
from superset_toolkit.queries import get_charts_by_username, get_dashboards_by_username
from superset_toolkit.ensure import get_database_id_by_name, get_dataset_id
from superset_toolkit.utils.metrics import build_simple_metric
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    print("⚙️ Enhanced Standalone Functions Example")
    print("=" * 60)
    
    # Configuration (update with your details)
    config = Config(
        superset_url="https://your-superset-instance.com",
        username="your-username", 
        password="your-secure-password",
        schema="your-schema",
        database_name="your-database"
    )
    
    try:
        # Create client for session/authentication
        client = SupersetClient(config=config)
        print(f"✅ Authenticated as user ID: {client.user_id}")
        
        # Get common IDs for standalone functions
        db_id = get_database_id_by_name(client.session, client.base_url, config.database_name)
        dataset_id = get_dataset_id(client.session, client.base_url, "your_table_name", config.schema)
        print(f"✅ Using dataset ID: {dataset_id}")
        
        # ================================================================
        # ENHANCED STANDALONE FUNCTIONS (New Username Support)
        # ================================================================
        print("\n👤 Enhanced Standalone Functions (Username Support)")
        print("-" * 50)
        
        print("📊 1. Table chart with username (no user ID resolution needed):")
        table_chart_id = create_table_chart(
            session=client.session,
            base_url=client.base_url,
            slice_name="Standalone Table Chart",
            dataset_id=dataset_id,
            username="data_analyst",  # ✨ Enhanced: Just pass username!
            columns=["id", "name"],
            row_limit=50
        )
        print(f"   ✅ Created table chart ID: {table_chart_id}")
        
        print("\n🥧 2. Pie chart with username:")
        pie_chart_id = create_pie_chart(
            session=client.session,
            base_url=client.base_url,
            slice_name="Standalone Pie Chart",
            dataset_id=dataset_id,
            username="data_analyst",  # ✨ Enhanced: Username support
            metric=build_simple_metric("id", "BIGINT", "COUNT", "Record Count"),
            groupby=["name"],
            row_limit=10
        )
        print(f"   ✅ Created pie chart ID: {pie_chart_id}")
        
        print("\n📊 3. Histogram chart with username:")
        hist_chart_id = create_histogram_chart(
            session=client.session,
            base_url=client.base_url, 
            slice_name="Standalone Histogram Chart",
            dataset_id=dataset_id,
            username="data_analyst",  # ✨ Enhanced: Username support
            all_columns_x=["id"],
            bins=5
        )
        print(f"   ✅ Created histogram chart ID: {hist_chart_id}")
        
        # ================================================================
        # BACKWARD COMPATIBILITY (Existing Code Still Works)
        # ================================================================
        print("\n🔄 Backward Compatibility (Existing Code)")
        print("-" * 50)
        
        print("📊 4. Traditional approach (user_id parameter still works):")
        traditional_chart_id = create_table_chart(
            session=client.session,
            base_url=client.base_url,
            slice_name="Traditional Approach Chart",
            dataset_id=dataset_id,
            user_id=1,  # Traditional: explicit user_id
            columns=["media_url"],
            row_limit=25
        )
        print(f"   ✅ Created chart with user_id: {traditional_chart_id}")
        
        # ================================================================
        # DASHBOARD CREATION (Enhanced Functions)
        # ================================================================
        print("\n🖥️ Enhanced Dashboard Operations")
        print("-" * 50)
        
        print("📋 5. Create dashboard and link charts:")
        dashboard_id = ensure_dashboard(
            session=client.session,
            base_url=client.base_url,
            title="Standalone Functions Dashboard",
            slug="standalone-functions-dashboard",
            user_id=1  # Dashboard ownership
        )
        
        # Add all created charts to dashboard
        chart_ids = [table_chart_id, pie_chart_id, hist_chart_id, traditional_chart_id]
        add_charts_to_dashboard(client.session, client.base_url, dashboard_id, chart_ids)
        
        print(f"   ✅ Created dashboard {dashboard_id} with {len(chart_ids)} charts")
        
        # ================================================================
        # QUERY OPERATIONS (Enhanced Functions)
        # ================================================================
        print("\n🔍 Enhanced Query Operations")
        print("-" * 50)
        
        print("📊 6. Query charts by username:")
        user_charts = get_charts_by_username(client.session, client.base_url, "data_analyst")
        print(f"   User has {len(user_charts)} charts")
        print(f"   Recent charts: {[c['slice_name'][:30] + '...' for c in user_charts[:3]]}")
        
        print("\n🖥️ 7. Query dashboards by username:")
        user_dashboards = get_dashboards_by_username(client.session, client.base_url, "data_analyst")
        print(f"   User has {len(user_dashboards)} dashboards")
        
        # ================================================================
        # SUMMARY
        # ================================================================
        print("\n" + "=" * 60)
        print("✅ ENHANCED STANDALONE FUNCTIONS EXAMPLE COMPLETE")
        print("=" * 60)
        
        print("Key improvements demonstrated:")
        print("  ✨ Username parameters in all chart functions")
        print("  ✨ No manual user ID resolution needed")
        print("  ✨ Backward compatibility maintained")
        print("  ✨ Professional error handling")
        
        print(f"\nCreated resources:")
        print(f"  📊 Charts: {chart_ids}")
        print(f"  🖥️ Dashboard: {dashboard_id}")
        print(f"  🌐 URL: {client.base_url}/superset/dashboard/standalone-functions-dashboard/")
        
        print("\n💡 To clean up test resources:")
        print("   from superset_toolkit.charts import delete_charts_by_name_pattern")
        print("   delete_charts_by_name_pattern(session, base_url, 'Standalone', dry_run=False)")
        
    except SupersetToolkitError as e:
        print(f"❌ Toolkit Error: {e}")
        sys.exit(1) 
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
