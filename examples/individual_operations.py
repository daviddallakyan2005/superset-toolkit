#!/usr/bin/env python3
"""
Individual operations example for Superset Toolkit.

This example shows how to use individual components:
1. Dataset management
2. Chart creation
3. Dashboard operations
"""

import os
import sys

# For local development only - remove when package is installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.ensure import get_database_id_by_name
from superset_toolkit.datasets import ensure_dataset, refresh_dataset_metadata
from superset_toolkit.charts import create_table_chart
from superset_toolkit.dashboard import ensure_dashboard, add_charts_to_dashboard
from superset_toolkit.utils.metrics import build_simple_metric
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    """Run individual operations example."""
    try:
        print("🚀 Creating Superset client...")
        client = SupersetClient()
        
        session = client.session
        base_url = client.base_url
        user_id = client.user_id
        
        print(f"✅ Connected to Superset: {base_url}")
        
        # 1. Get database ID
        print("\n📊 Getting database ID...")
        database_id = get_database_id_by_name(session, base_url, client.config.database_name)
        print(f"Database ID: {database_id}")
        
        # 2. Ensure a dataset exists
        print("\n📊 Ensuring dataset exists...")
        print("Note: Update 'your_table_name' with an actual table in your database")
        dataset_id = ensure_dataset(
            session, 
            base_url, 
            database_id, 
            client.config.schema, 
            "your_table_name"  # Update with your actual table name
        )
        print(f"Dataset ID: {dataset_id}")
        
        # 3. Refresh dataset metadata
        print("\n🔄 Refreshing dataset metadata...")
        refresh_dataset_metadata(session, base_url, dataset_id)
        
        # 4. Create a simple table chart
        print("\n📊 Creating a table chart...")
        try:
            from superset_toolkit.datasets import get_dataset_column_names
            columns = get_dataset_column_names(session, base_url, dataset_id)
            
            chart_id = create_table_chart(
                session,
                base_url,
                "Example Table Chart",
                dataset_id,
                user_id,
                columns=columns[:5],  # Just first 5 columns
                row_limit=100,
                include_search=True,
                table_filter=True
            )
        except Exception as e:
            print(f"⚠️  Chart creation skipped (dataset issue): {e}")
            print("💡 Ensure your table name exists and is accessible")
            chart_id = None
        if chart_id:
            print(f"Chart ID: {chart_id}")
            
            # 5. Create a dashboard
            print("\n📊 Creating dashboard...")
            dashboard_id = ensure_dashboard(
                session,
                base_url,
                "Example Dashboard",
                "example-dashboard"
            )
            print(f"Dashboard ID: {dashboard_id}")
            
            # 6. Add chart to dashboard
            print("\n📐 Adding chart to dashboard...")
            add_charts_to_dashboard(session, base_url, dashboard_id, [chart_id])
            
            print(f"\n🎉 Individual operations completed successfully!")
            print(f"📊 Dashboard URL: {base_url}/superset/dashboard/{dashboard_id}/")
        else:
            print("\n💡 Individual operations example completed with notes")
            print("   Update the table name to create actual charts and dashboards")
        
    except SupersetToolkitError as e:
        print(f"❌ Superset Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
