#!/usr/bin/env python3
"""
Multi-User Workflows Example

Demonstrates advanced multi-user scenarios:
- Creating resources for different users  
- Resource management across teams
- Permission-aware operations
- User migration and cleanup

Before running:
1. Update configuration below
2. Ensure TEST user exists in your Superset (or change username)
3. Run: python3 multi_user_workflows.py
"""

import sys
import os

# For local development - adjust path as needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.exceptions import SupersetToolkitError, AuthenticationError


def main():
    print("👥 Multi-User Workflows Example")
    print("=" * 50)
    
    # Use admin account for multi-user operations
    admin_config = Config(
        superset_url="https://your-superset-instance.com",
        username="admin",
        password="your-admin-password", 
        schema="your-schema",
        database_name="your-database"
    )
    
    try:
        with SupersetClient(config=admin_config) as admin_client:
            print(f"✅ Admin authenticated (User ID: {admin_client.user_id})")
            
            # ========================================================
            # MULTI-USER CHART CREATION
            # ========================================================
            print("\n🎨 Creating Charts for Different Users")
            print("-" * 40)
            
            # Create charts for different team members
            team_charts = []
            
            print("📊 Creating chart for Sales team:")
            sales_chart = admin_client.create_table_chart(
                name="Sales Team Dashboard Data",
                table="sales_data",
                owner="sales_team",  # Sales team ownership
                columns=["region", "amount"],
                row_limit=30
            )
            team_charts.append(("Sales", sales_chart))
            
            print("📊 Creating chart for Analytics user:")
            analyst_chart = admin_client.create_table_chart(
                name="Analytics User Personal Chart", 
                table="analytics_data",
                owner="data_analyst",  # Different user
                columns=["metric", "value"],
                row_limit=20
            )
            team_charts.append(("Analytics", analyst_chart))
            
            print("📊 Creating chart for Admin (self):")
            admin_chart = admin_client.create_table_chart(
                name="Admin Overview Chart",
                table="admin_data",
                # No owner specified = uses authenticated user (admin)
                columns=["id", "status"],
                row_limit=15
            )
            team_charts.append(("Admin", admin_chart))
            
            print(f"✅ Created {len(team_charts)} charts for different users")
            
            # ========================================================
            # TEAM DASHBOARD CREATION
            # ========================================================
            print("\n🚀 Team Dashboard Creation")
            print("-" * 30)
            
            team_dashboard = admin_client.create_dashboard_with_charts(
                dashboard_title="Multi-User Team Dashboard",
                slug="multi-user-team-dashboard",
                chart_configs=[
                    {
                        "name": "Team Overview",
                        "table": "team_overview_data",
                        "columns": ["team", "metrics"]
                    },
                    {
                        "name": "Team Details", 
                        "table": "team_details_data", 
                        "columns": ["details", "status"]
                    }
                ],
                owner="admin"  # Dashboard owned by admin, but accessible to team
            )
            
            print(f"✅ Created team dashboard: {team_dashboard['dashboard_id']}")
            print(f"🌐 URL: {admin_client.base_url}/superset/dashboard/multi-user-team-dashboard/")
            
            # ========================================================
            # USER RESOURCE ANALYSIS
            # ========================================================
            print("\n📊 User Resource Analysis")
            print("-" * 30)
            
            # Analyze different user resources
            users_to_analyze = ["admin", "data_analyst"]
            
            for username in users_to_analyze:
                try:
                    summary = admin_client.get_user_summary(username)
                    print(f"👤 {username}: {summary['summary']}")
                    
                    # Show recent charts
                    if summary['charts']['count'] > 0:
                        recent_charts = [c['slice_name'] for c in summary['charts']['items'][:2]]
                        print(f"   Recent charts: {recent_charts}")
                        
                except Exception as e:
                    print(f"⚠️  Could not analyze {username}: {e}")
            
            # ========================================================
            # RESOURCE MIGRATION DEMO
            # ========================================================
            print("\n🔄 Resource Migration Demo")
            print("-" * 30)
            
            print("Testing migration from admin to data_analyst (dry run):")
            migration_preview = admin_client.migrate_user_resources(
                from_user="admin",
                to_user="data_analyst",
                dry_run=True
            )
            print(f"Would migrate {migration_preview['migrated']} resources")
            
            # ========================================================
            # PERMISSION TESTING
            # ========================================================
            print("\n🛡️ Permission Testing")
            print("-" * 25)
            
            # Test what happens with regular user login
            print("Testing with regular user login (limited permissions):")
            print("Note: Update with your actual regular user credentials to test")
            
            # Commented out as it requires valid regular user credentials
            # try:
            #     regular_config = Config(
            #         superset_url="https://your-superset-instance.com",
            #         username="regular_user",
            #         password="regular_password",
            #         schema="your-schema", 
            #         database_name="your-database"
            #     )
            #     
            #     with SupersetClient(config=regular_config) as regular_client:
            #         print(f"✅ Regular user authenticated (User ID: {regular_client.user_id})")
            #         
            #         # Test chart creation (should work)
            #         user_chart = regular_client.create_table_chart(
            #             name="Regular User Chart",
            #             table="user_data",
            #             # No owner = uses regular user automatically 
            #             columns=["id"]
            #         )
            #         print(f"✅ Regular user can create charts: {user_chart}")
            #         
            # except Exception as e:
            #     print(f"ℹ️  Regular user issue: {e}")
            
            print("💡 Uncomment and update credentials above to test regular user permissions")
            
            # ========================================================
            # CLEANUP OPERATIONS
            # ========================================================
            print("\n🧹 Cleanup Operations")
            print("-" * 25)
            
            # Clean up test resources by pattern
            from superset_toolkit.charts import delete_charts_by_name_pattern
            from superset_toolkit.dashboard import delete_dashboards_by_name_pattern
            
            print("Cleaning up Multi-User test resources...")
            deleted_charts = delete_charts_by_name_pattern(
                admin_client.session, admin_client.base_url, "Multi-User", dry_run=False
            )
            deleted_dashboards = delete_dashboards_by_name_pattern(
                admin_client.session, admin_client.base_url, "Multi-User", dry_run=False  
            )
            
            print(f"✅ Cleaned up {len(deleted_charts)} charts, {len(deleted_dashboards)} dashboards")
            
            # ========================================================
            # FINAL SUMMARY
            # ========================================================
            print("\n" + "=" * 60)
            print("✅ MULTI-USER WORKFLOWS EXAMPLE COMPLETE")
            print("=" * 60)
            
            print("Capabilities demonstrated:")
            print("  👥 Multi-user chart creation") 
            print("  🎨 Team dashboard creation")
            print("  📊 User resource analysis")
            print("  🔄 Resource migration capabilities")
            print("  🛡️ Permission-aware operations")
            print("  🧹 Bulk cleanup operations")
            
            print("\n💡 Key Insights:")
            print("  ✨ Admin users: Full multi-user capabilities")
            print("  ✨ Regular users: Can create, limited query access") 
            print("  ✨ JWT extraction: Works for all user types")
            print("  ✨ SDK gracefully handles permission restrictions")
            
            # Show final resource state
            final_admin_summary = admin_client.get_user_summary("admin")
            print(f"\nFinal admin resources: {final_admin_summary['summary']}")
            
    except SupersetToolkitError as e:
        print(f"❌ Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
