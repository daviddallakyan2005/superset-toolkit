#!/usr/bin/env python3
"""
Dataset Ownership Management Example

This example demonstrates how to manage dataset ownership in Superset.
You can add owners to datasets without removing existing ones, which is
useful for team collaboration and automated workflows.
"""

import os
import sys

# For local development only - remove when package is installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.datasets import add_dataset_owner, refresh_dataset_metadata
from superset_toolkit.ensure import get_dataset_id, get_database_id_by_name
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    """Demonstrate dataset ownership management."""
    print("🔐 Dataset Ownership Management Example")
    print("=" * 60)
    
    try:
        # Create Superset client (login as admin with privileges)
        print("\n1️⃣ Connecting to Superset as admin...")
        client = SupersetClient()
        
        print(f"✅ Connected to: {client.base_url}")
        print(f"👤 Authenticated as user ID: {client.user_id}")
        
        # Example configuration
        table_name = "your_table_name"  # Update with actual table
        schema = client.config.schema
        
        print(f"\n2️⃣ Looking up dataset: {schema}.{table_name}")
        
        # Get dataset ID
        dataset_id = get_dataset_id(
            client.session, 
            client.base_url, 
            table_name, 
            schema
        )
        
        if not dataset_id:
            print(f"⚠️  Dataset '{schema}.{table_name}' not found")
            print("💡 Update the table_name variable with an actual table in your database")
            return
        
        print(f"✅ Found dataset ID: {dataset_id}")
        
        # Refresh dataset metadata
        print(f"\n3️⃣ Refreshing dataset metadata...")
        refresh_dataset_metadata(client.session, client.base_url, dataset_id)
        print("✅ Dataset metadata refreshed")
        
        # Add owners to the dataset
        print(f"\n4️⃣ Adding owners to dataset...")
        
        # Example: Add multiple team members as owners
        team_members = ["data_analyst", "data_engineer", "business_analyst"]
        
        print(f"👥 Adding {len(team_members)} team members as owners:")
        for username in team_members:
            try:
                add_dataset_owner(
                    client.session,
                    client.base_url,
                    dataset_id,
                    username
                )
                print(f"   ✅ Added: {username}")
            except Exception as e:
                print(f"   ⚠️  Could not add {username}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ DATASET OWNERSHIP MANAGEMENT COMPLETE")
        print("=" * 60)
        
        print("\n📝 Summary:")
        print("  • Logged in as admin with elevated privileges")
        print("  • Refreshed dataset metadata from database")
        print("  • Added multiple users as dataset owners")
        print("  • Existing owners were preserved (not removed)")
        print("  • All operations are idempotent (safe to re-run)")
        
        print("\n💡 Use Cases:")
        print("  • Enable team collaboration on datasets")
        print("  • Automated dataset provisioning for new users")
        print("  • Bulk ownership management for compliance")
        print("  • Service account to user delegation")
        
    except SupersetToolkitError as e:
        print(f"❌ Superset Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("DATASET OWNERSHIP MANAGEMENT EXAMPLE")
    print("=" * 60)
    print("Demonstrates adding owners to datasets without removing existing ones")
    print()
    print("Required environment variables:")
    print("- SUPERSET_URL")
    print("- SUPERSET_USERNAME (admin account)")
    print("- SUPERSET_PASSWORD")
    print()
    
    main()

