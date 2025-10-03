#!/usr/bin/env python3
"""
Basic usage example for Superset Toolkit.

This example shows how to:
1. Create a SupersetClient
2. Perform basic Superset operations
3. Handle errors gracefully

Before running, set these environment variables:
- SUPERSET_URL
- SUPERSET_USERNAME
- SUPERSET_PASSWORD
- SUPERSET_SCHEMA (optional, defaults to 'reports')
- SUPERSET_DATABASE_NAME (optional, defaults to 'Trino')
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
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    """Run the basic usage example."""
    try:
        print("🚀 Creating Superset client...")
        
        # Create client (will authenticate automatically)
        client = SupersetClient()
        
        print(f"✅ Connected to Superset: {client.base_url}")
        print(f"👤 Authenticated as user ID: {client.user_id}")
        print(f"📊 Using schema: {client.config.schema}")
        print(f"🗄️ Using database: {client.config.database_name}")
        
        # Example: Create a simple table chart and dashboard
        print("\n📊 Running basic Superset operations...")
        
        session = client.session
        base_url = client.base_url
        user_id = client.user_id
        
        # 1. Get database ID
        database_id = get_database_id_by_name(session, base_url, client.config.database_name)
        print(f"Database ID: {database_id}")
        
        # 2. Ensure a dataset exists (replace 'your_table' with actual table name)
        print("Note: Replace 'your_table' with an actual table name in your database")
        # dataset_id = ensure_dataset(session, base_url, database_id, client.config.schema, "your_table")
        # print(f"Dataset ID: {dataset_id}")
        
        print("\n🎉 Basic operations example completed!")
        print("💡 Uncomment the dataset operations above and provide real table names to test fully")
        
    except SupersetToolkitError as e:
        print(f"❌ Superset Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
