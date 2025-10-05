#!/usr/bin/env python3
"""
Custom Configuration & Multi-Environment Example

This example shows how to:
1. Create custom configurations for different environments
2. Use different credentials and settings  
3. Professional configuration patterns for production use
4. Environment-specific resource management

Run: python3 custom_config.py
"""

import os
import sys

# For local development only - remove when package is installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from superset_toolkit import SupersetClient
from superset_toolkit.config import Config
from superset_toolkit.exceptions import SupersetToolkitError


def test_environment(env_name: str, config: Config):
    """Test an environment configuration."""
    print(f"\n🌐 Testing {env_name} Environment")
    print("-" * 40)
    
    try:
        with SupersetClient(config=config) as client:
            # Validate connection
            status = client.validate_connection()
            
            if status['status'] == 'connected':
                print(f"✅ {env_name} connection successful")
                print(f"   URL: {status['url']}")
                print(f"   User ID: {status['user_id']}")
                print(f"   Schema: {status['schema']}")
                print(f"   Charts in system: {status['chart_count']}")
                
                # Test basic operation
                summary = client.get_user_summary(config.username)
                print(f"   User resources: {summary['summary']}")
                
                return True
            else:
                print(f"❌ {env_name} connection failed: {status['message']}")
                return False
                
    except Exception as e:
        print(f"❌ {env_name} error: {e}")
        return False


def main():
    """Run the custom configuration examples."""
    print("🔧 Custom Configuration & Multi-Environment Example")
    print("=" * 60)
    
    # ================================================================
    # CONFIGURATION PATTERNS
    # ================================================================
    
    # Pattern 1: Development Environment
    dev_config = Config(
        superset_url="http://localhost:8088",  # Local dev instance
        username="admin",
        password="admin", 
        schema="dev_analytics",
        database_name="DevTrino"
    )
    
    # Pattern 2: Staging Environment  
    staging_config = Config(
        superset_url="https://staging-superset.yourcompany.com",
        username="staging-admin",
        password=os.getenv("STAGING_SUPERSET_PASSWORD"),  # From env var
        schema="staging_analytics",
        database_name="StagingTrino"
    )
    
    # Pattern 3: Production Environment 
    prod_config = Config(
        superset_url="https://prod-superset.yourcompany.com",  # Production instance
        username="prod-admin",
        password=os.getenv("PROD_SUPERSET_PASSWORD", "production-password"),
        schema="production_analytics",
        database_name="ProductionDatabase"
    )
    
    # Pattern 4: Mixed Configuration (Some from env, some explicit)
    mixed_config = Config(
        superset_url="https://custom-superset.com",    # Explicit
        schema="custom_schema",                        # Explicit
        # username/password from SUPERSET_USERNAME/PASSWORD env vars
        database_name="CustomTrino"                   # Explicit
    )
    
    # ================================================================
    # ENVIRONMENT TESTING
    # ================================================================
    print("\n🧪 Testing Different Environment Configurations")
    
    environments = [
        ("Development", dev_config),
        ("Staging", staging_config), 
        ("Production", prod_config),
        # ("Mixed", mixed_config)  # Uncomment if you set env vars
    ]
    
    working_envs = []
    for env_name, config in environments:
        if test_environment(env_name, config):
            working_envs.append(env_name)
    
    # ================================================================
    # DEMONSTRATE MULTI-ENVIRONMENT DEPLOYMENT
    # ================================================================
    if working_envs:
        print(f"\n🚀 Demonstrating Multi-Environment Operations")
        print("-" * 50)
        
        # Use a working config for demonstration (first working environment)
        demo_config = next((config for name, config in environments if name in working_envs), prod_config)
        
        with SupersetClient(config=demo_config) as client:
            print("Creating example resources...")
            
            # Environment-specific chart (using generic table name)
            chart_id = client.create_table_chart(
                name="Multi-Environment Example Chart",
                table="your_table_name",  # Update with your table
                columns=["id", "name"],   # Update with your columns
                row_limit=30
            )
            
            print(f"✅ Created chart for environment: {chart_id}")
            
            # Environment-specific dashboard
            dashboard_id = client.create_dashboard(
                title="Multi-Environment Dashboard", 
                slug="multi-env-dashboard",
                charts=["Multi-Environment Example Chart"]
            )
            
            print(f"✅ Created dashboard: {dashboard_id}")
            print(f"🌐 Dashboard URL: {client.base_url}/superset/dashboard/multi-env-dashboard/")
    
    # ================================================================
    # CONFIGURATION BEST PRACTICES
    # ================================================================
    print("\n" + "=" * 60)
    print("💡 CONFIGURATION BEST PRACTICES")
    print("=" * 60)
    
    print("1. Environment Variables (Simple):")
    print("   export SUPERSET_URL='https://superset.com'")
    print("   export SUPERSET_USERNAME='admin'")
    print("   export SUPERSET_PASSWORD='password'")
    print("   client = SupersetClient()  # Auto-uses env vars")
    
    print("\n2. Config Class (Production):")
    print("   config = Config(url='...', username='...', password='...')")
    print("   client = SupersetClient(config=config)")
    
    print("\n3. Context Managers (Recommended):")
    print("   with SupersetClient(config=config) as client:")
    print("       # Operations here")
    print("   # Automatic cleanup")
    
    print("\n4. Multi-Environment (Advanced):")
    print("   environments = {'dev': dev_config, 'prod': prod_config}")
    print("   for env, config in environments.items():")
    print("       with SupersetClient(config=config) as client:")
    print("           # Deploy to each environment")
    
    print(f"\n✅ Working environments: {working_envs}")
    print("🎯 Update configurations above for your specific environments")


if __name__ == "__main__":
    main()
