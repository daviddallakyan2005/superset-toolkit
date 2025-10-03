#!/usr/bin/env python3
"""
Custom configuration example for Superset Toolkit.

This example shows how to:
1. Create a custom configuration
2. Use different credentials or URLs
3. Override default settings
"""

import os
import sys

# For local development only - remove when package is installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.ensure import get_database_id_by_name
from superset_toolkit.exceptions import SupersetToolkitError


def main():
    """Run the custom configuration example."""
    try:
        print("🚀 Creating custom configuration...")
        
        # Create custom config (you can override any settings)
        custom_config = Config(
            superset_url="https://your-custom-superset.com",  # Override URL
            # username and password will still come from env vars
            schema="custom_schema",  # Override schema
            database_name="CustomDB"  # Override database name
        )
        
        print(f"📊 Using custom config:")
        print(f"  - URL: {custom_config.superset_url}")
        print(f"  - Schema: {custom_config.schema}")
        print(f"  - Database: {custom_config.database_name}")
        
        # Create client with custom config
        client = SupersetClient(config=custom_config)
        
        print(f"✅ Connected to Superset: {client.base_url}")
        print(f"👤 Authenticated as user ID: {client.user_id}")
        
        # Test database connection
        print("\n📊 Testing database connection...")
        session = client.session
        base_url = client.base_url
        
        try:
            database_id = get_database_id_by_name(session, base_url, custom_config.database_name)
            print(f"✅ Found database '{custom_config.database_name}' with ID: {database_id}")
        except Exception as e:
            print(f"⚠️ Database '{custom_config.database_name}' not found: {e}")
            print("💡 Make sure the database name matches one in your Superset instance")
        
        print("\n🎉 Custom configuration example completed successfully!")
        
    except SupersetToolkitError as e:
        print(f"❌ Superset Toolkit Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
