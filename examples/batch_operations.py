#!/usr/bin/env python3
"""
Batch Operations Example

Demonstrates efficient batch operations for creating and managing multiple resources:
- Batch chart creation
- Batch dashboard creation  
- Bulk deletion operations
- Resource migration between users

Before running:
1. Update configuration below
2. Ensure required tables exist
3. Run: python3 batch_operations.py
"""

import sys
import os

# For local development - adjust path as needed  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    print("📦 Batch Operations Example")
    print("=" * 50)
    
    config = Config(
        superset_url="https://your-superset-instance.com", 
        username="your-username",
        password="your-secure-password",
        schema="your-schema",
        database_name="your-database"
    )
    
    try:
        with SupersetClient(config=config) as client:
            
            # ============================================================
            # BATCH CHART CREATION
            # ============================================================
            print("\n📊 Batch Chart Creation")
            print("-" * 30)
            
            chart_definitions = [
                {
                    "name": "Batch Chart 1 - All Columns",
                    "table": "your_table_name",
                    "columns": ["id", "title", "media_url"],
                    "row_limit": 50
                },
                {
                    "name": "Batch Chart 2 - IDs Only", 
                    "table": "your_table_name",
                    "columns": ["id"],
                    "row_limit": 100
                },
                {
                    "name": "Batch Chart 3 - Titles Only",
                    "table": "your_table_name", 
                    "columns": ["title"],
                    "row_limit": 25
                }
            ]
            
            print(f"Creating {len(chart_definitions)} charts in batch...")
            batch_chart_ids = client.create_charts_batch(
                chart_definitions=chart_definitions,
                owner="data_team"  # All owned by data team
            )
            
            print(f"✅ Created {len(batch_chart_ids)} charts: {batch_chart_ids}")
            
            # ============================================================
            # COMPOSITE DASHBOARD CREATION
            # ============================================================
            print("\n🚀 Composite Dashboard Creation")
            print("-" * 35)
            
            print("Creating dashboard with multiple charts in one operation...")
            dashboard_result = client.create_dashboard_with_charts(
                dashboard_title="Batch Operations Dashboard",
                slug="batch-operations-dashboard",
                chart_configs=[
                    {
                        "name": "Overview Chart",
                        "table": "your_table_name",
                        "type": "table", 
                        "columns": ["id", "title", "media_url"],
                        "row_limit": 20
                    },
                    {
                        "name": "Quick Stats",
                        "table": "your_table_name",
                        "type": "table",
                        "columns": ["id"],
                        "row_limit": 5
                    }
                ],
                owner="admin"
            )
            
            print(f"✅ Created dashboard {dashboard_result['dashboard_id']}")
            print(f"✅ With charts: {dashboard_result['chart_ids']}")
            
            # ============================================================
            # QUERY OPERATIONS
            # ============================================================
            print("\n🔍 Query Operations")
            print("-" * 20)
            
            # Get user summary
            summary = client.get_user_summary("data_team")
            print(f"User summary: {summary['summary']}")
            
            # Get charts by table
            table_charts = client.get_charts(table="your_table_name", schema=config.schema)
            print(f"Table used by {len(table_charts)} charts")
            
            # ============================================================ 
            # BATCH DELETION OPERATIONS
            # ============================================================
            print("\n🗑️ Batch Deletion Operations")  
            print("-" * 30)
            
            print(f"Deleting {len(batch_chart_ids)} batch-created charts...")
            deleted_charts = client.delete_charts_batch(batch_chart_ids, dry_run=False)
            print(f"✅ Deleted {len(deleted_charts)} charts")
            
            # Clean up dashboards by pattern
            from superset_toolkit.dashboard import delete_dashboards_by_name_pattern
            deleted_dashboards = delete_dashboards_by_name_pattern(
                client.session, client.base_url, "Batch", dry_run=False
            )
            print(f"✅ Deleted {len(deleted_dashboards)} dashboards matching 'Batch'")
            
            # ============================================================
            # RESOURCE MIGRATION EXAMPLE
            # ============================================================
            print("\n🔄 Resource Migration Example")
            print("-" * 35)
            
            # Note: This is a dry run since we don't have a real second user
            print("Testing resource migration (dry run)...")
            migration_preview = client.migrate_user_resources(
                from_user="data_team",
                to_user="backup_team",  # Example migration
                dry_run=True
            )
            print(f"Migration preview: {migration_preview['migrated']} resources would be migrated")
            
            # ============================================================
            # FINAL SUMMARY
            # ============================================================
            print("\n" + "=" * 60)
            print("✅ BATCH OPERATIONS EXAMPLE COMPLETE")
            print("=" * 60)
            
            print("Operations demonstrated:")
            print("  📦 Batch chart creation (efficient)")
            print("  🚀 Composite dashboard creation")
            print("  🔍 Resource queries and summaries") 
            print("  🗑️ Batch deletion operations")
            print("  🔄 Resource migration capabilities")
            
            # Final verification
            final_summary = client.get_user_summary("data_team")
            print(f"\nFinal team resources: {final_summary['summary']}")
            
            print("\n🎯 Key Benefits:")
            print("  ✨ No manual user ID resolution")
            print("  ✨ Efficient batch operations")
            print("  ✨ Professional error handling")
            print("  ✨ Graceful permission handling")
            
    except SupersetToolkitError as e:
        print(f"❌ Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
