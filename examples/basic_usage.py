#!/usr/bin/env python3
"""
Basic Usage Example - Professional Client Methods

This example shows the simplest way to use Superset Toolkit with professional patterns:
1. Client-centric operations (no session/base_url repetition)
2. Username-aware functions (no manual user ID resolution)
3. Context managers for clean resource management

Update the configuration below and run: python3 basic_usage.py
"""

import os
import sys

# For local development only - remove when package is installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    """Run the basic usage example with professional patterns."""
    
    print("🚀 Basic Usage Example - Professional Client")
    print("=" * 60)
    
    # Configure connection (update with your details)
    config = Config(
        superset_url="https://your-superset-instance.com",  # Update with your Superset URL
        username="your-username",                           # Update with your username
        password="your-secure-password",                    # Update with your password
        schema="your-schema",                               # Update with your schema
        database_name="your-database"                       # Update with your database name
    )
    
    try:
        # Professional pattern: Use context manager
        with SupersetClient(config=config) as client:
            
            # Test connection
            status = client.validate_connection()
            print(f"✅ Connection: {status['status']}")
            print(f"   URL: {status['url']}")
            print(f"   User ID: {status['user_id']}")
            print(f"   Schema: {status['schema']}")
            print(f"   Database: {status['database']}")
            
            # ========================================================
            # BASIC CHART CREATION (Professional Way)
            # ========================================================
            print("\n📊 Creating a basic chart...")
            
            chart_id = client.create_table_chart(
                name="Basic Example Chart",
                table="your_table_name",  # Update with your actual table name
                columns=["column1", "column2", "column3"],  # Update with your columns
                row_limit=50
            )
            
            print(f"✅ Created chart ID: {chart_id}")
            
            # ========================================================
            # BASIC DASHBOARD CREATION
            # ========================================================
            print("\n🖥️ Creating a basic dashboard...")
            
            dashboard_id = client.create_dashboard(
                title="Basic Example Dashboard",
                slug="basic-example-dashboard",
                charts=["Basic Example Chart"]  # Auto-links the chart we created
            )
            
            print(f"✅ Created dashboard ID: {dashboard_id}")
            print(f"🌐 View at: {client.base_url}/superset/dashboard/basic-example-dashboard/")
            
            # ========================================================
            # QUERY OPERATIONS  
            # ========================================================
            print("\n🔍 Querying resources...")
            
            # Get your charts
            my_charts = client.get_charts(owner="your-username")  # Update with your username
            print(f"You have {len(my_charts)} charts")
            
            # Get your dashboards
            my_dashboards = client.get_dashboards(owner="your-username")  # Update with your username  
            print(f"You have {len(my_dashboards)} dashboards")
            
            # ========================================================
            # OPTIONAL: CLEANUP
            # ========================================================
            print("\n🧹 Cleanup (optional)...")
            print("To clean up test resources, uncomment the line below:")
            print("# client.cleanup_user('admin', dry_run=False)")
            
            # Uncomment to actually clean up:
            # cleanup_result = client.cleanup_user("admin", dry_run=False)
            # print(f"Deleted {len(cleanup_result['chart_ids'])} charts, {len(cleanup_result['dashboard_ids'])} dashboards")
            
        # Context manager automatically cleans up session
        print("\n✅ Basic example completed successfully!")
        print("\n💡 Next Steps:")
        print("   1. Check other examples in examples/ directory")
        print("   2. Read docs/ for comprehensive guides")
        print("   3. Explore advanced features like batch operations")
        
    except SupersetToolkitError as e:
        print(f"❌ Superset Toolkit Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your configuration (URL, credentials)")
        print("   2. Verify table name exists in your database")
        print("   3. Ensure user has proper permissions")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
