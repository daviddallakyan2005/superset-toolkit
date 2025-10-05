"""Main Superset client for API operations."""

import logging
from typing import Optional, Dict, Any, List

import requests

from .config import Config, get_default_config
from .auth import create_session, login, attach_csrf_token, get_current_user_id, get_user_id_by_username
from .exceptions import AuthenticationError, SupersetToolkitError

# Configure logging
logger = logging.getLogger(__name__)


class SupersetClient:
    """
    Main client for Superset API operations.
    
    This class provides a high-level interface for all Superset operations,
    managing authentication, session state, and providing access to all
    toolkit functionality.
    
    Example:
        >>> client = SupersetClient()
        >>> # Client is now authenticated and ready to use
        >>> from superset_toolkit.flows import run_timelapse_illustration
        >>> run_timelapse_illustration(client)
        
        >>> # Or specify a username to work with
        >>> client = SupersetClient(username_for_ownership="john_doe")
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        session: Optional[requests.Session] = None,
        username_for_ownership: Optional[str] = None
    ):
        """
        Initialize the Superset client.
        
        Args:
            config: Configuration object. If None, uses default config from environment
            session: Requests session. If None, creates a new session
            username_for_ownership: Optional username to use for chart/dashboard ownership.
                                   If None, uses current authenticated user from /api/v1/me/
        """
        self.config = config or get_default_config()
        self.session = session or create_session()
        self._user_id: Optional[int] = None
        self._username_for_ownership = username_for_ownership
        
        # Authenticate immediately
        self._authenticate()
        
        logger.info(f"SupersetClient initialized for {self.config.superset_url}")
    
    def _authenticate(self) -> None:
        """Authenticate with Superset and set up session."""
        try:
            # Login and get access token
            login(
                self.session,
                self.config.superset_url,
                self.config.username,
                self.config.password
            )
            
            # Attach CSRF token
            attach_csrf_token(self.session, self.config.superset_url)
            
            print("✅ Authentication completed")
            
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with Superset: {e}")
    
    @property
    def base_url(self) -> str:
        """Get the Superset base URL."""
        return self.config.superset_url
    
    @property
    def user_id(self) -> int:
        """
        Get the user ID for chart/dashboard ownership.
        
        If username_for_ownership was provided, looks up that user's ID.
        Otherwise, gets the current authenticated user's ID from /api/v1/me/.
        
        Returns:
            User ID
        """
        if self._user_id is None:
            if self._username_for_ownership:
                # Look up the specified username
                self._user_id = get_user_id_by_username(
                    self.session, 
                    self.config.superset_url, 
                    self._username_for_ownership
                )
            else:
                # Get current user using reliable username lookup method
                self._user_id = get_current_user_id(
                    self.session, 
                    self.config.superset_url,
                    self.config.username  # Use login username
                )
        return self._user_id
    
    def refresh_auth(self) -> None:
        """Refresh authentication if needed."""
        self._authenticate()
        self._user_id = None  # Clear cached user ID
    
    def resolve_current_user_id(self) -> int:
        """
        Explicitly get the current authenticated user's ID.
        
        Returns:
            User ID of the currently logged-in user
        """
        return get_current_user_id(
            self.session, 
            self.config.superset_url,
            self.config.username
        )
    
    def resolve_user_id(self, username: str) -> int:
        """
        Explicitly get a user's ID by their username.
        
        Args:
            username: Username to look up
            
        Returns:
            User ID
            
        Raises:
            AuthenticationError: If user is not found
        """
        return get_user_id_by_username(self.session, self.config.superset_url, username)
    
    # ========================================================================
    # PROFESSIONAL CLIENT METHODS - Username-Aware Chart Operations  
    # ========================================================================
    
    def create_table_chart(
        self,
        name: str,
        table: str,
        schema: str = None,
        owner: Optional[str] = None,
        database: str = None,
        columns: Optional[List[str]] = None,
        **kwargs
    ) -> int:
        """
        Create a table chart with automatic setup.
        
        Args:
            name: Chart name
            table: Source table name
            schema: Database schema (defaults to config schema)
            owner: Username for ownership (defaults to authenticated user)
            database: Database name (defaults to config database) 
            columns: Columns to display
            **kwargs: Additional chart parameters
            
        Returns:
            Chart ID
        """
        from .charts import create_table_chart
        from .ensure import get_database_id_by_name
        from .datasets import ensure_dataset, refresh_dataset_metadata
        
        # Use config defaults
        schema = schema or self.config.schema
        database = database or self.config.database_name
        
        # Resolve database and dataset
        database_id = get_database_id_by_name(self.session, self.base_url, database)
        dataset_id = ensure_dataset(self.session, self.base_url, database_id, schema, table)
        refresh_dataset_metadata(self.session, self.base_url, dataset_id)
        
        # Create chart with username support
        return create_table_chart(
            session=self.session,
            base_url=self.base_url,
            slice_name=name,
            dataset_id=dataset_id,
            username=owner,  # Let function handle user resolution
            columns=columns,
            **kwargs
        )
    
    def create_dashboard(
        self,
        title: str,
        slug: str,
        owner: Optional[str] = None,
        charts: Optional[List[str]] = None
    ) -> int:
        """
        Create a dashboard with optional chart linking.
        
        Args:
            title: Dashboard title
            slug: Dashboard slug
            owner: Username for ownership (defaults to authenticated user)
            charts: Optional list of chart names to add
            
        Returns:
            Dashboard ID
        """
        from .dashboard import ensure_dashboard, link_chart_to_dashboard, add_charts_to_dashboard
        from .ensure import get_chart_id
        from .auth import get_user_id_by_username, get_current_user_id
        
        # Resolve user
        if owner:
            user_id = get_user_id_by_username(self.session, self.base_url, owner)
        else:
            user_id = get_current_user_id(
                self.session, 
                self.base_url,
                self.config.username
            )
        
        # Create dashboard
        dashboard_id = ensure_dashboard(self.session, self.base_url, title, slug, user_id)
        
        # Link charts if specified
        if charts:
            chart_ids = []
            for chart_name in charts:
                chart_id = get_chart_id(self.session, self.base_url, chart_name)
                if chart_id:
                    chart_ids.append(chart_id)
                    link_chart_to_dashboard(self.session, self.base_url, chart_id, dashboard_id)
            
            if chart_ids:
                add_charts_to_dashboard(self.session, self.base_url, dashboard_id, chart_ids)
                print(f"✅ Added {len(chart_ids)} charts to dashboard")
        
        return dashboard_id
    
    def get_charts(
        self,
        owner: Optional[str] = None,
        table: Optional[str] = None,
        schema: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get charts with flexible filtering.
        
        Args:
            owner: Username to filter by (if None, gets all charts)
            table: Table name to filter by
            schema: Schema to filter by
            
        Returns:
            List of chart objects
        """
        if owner:
            from .queries import get_charts_by_username
            return get_charts_by_username(self.session, self.base_url, owner)
        elif table and schema:
            from .queries import get_charts_by_dataset
            from .ensure import get_database_id_by_name, get_dataset_id
            database_id = get_database_id_by_name(self.session, self.base_url, self.config.database_name)
            dataset_id = get_dataset_id(self.session, self.base_url, table, schema)
            if dataset_id:
                return get_charts_by_dataset(self.session, self.base_url, dataset_id)
            return []
        else:
            from .queries import get_all_charts
            return get_all_charts(self.session, self.base_url)
    
    def get_dashboards(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get dashboards with optional owner filtering.
        
        Args:
            owner: Username to filter by (if None, gets all dashboards)
            
        Returns:
            List of dashboard objects
        """
        if owner:
            from .queries import get_dashboards_by_username
            return get_dashboards_by_username(self.session, self.base_url, owner)
        else:
            from .queries import get_all_dashboards
            return get_all_dashboards(self.session, self.base_url)
    
    def cleanup_user(self, username: str, dry_run: bool = True) -> Dict[str, List[int]]:
        """
        Clean up all resources for a user.
        
        Args:
            username: Username whose resources to delete
            dry_run: If True, only shows what would be deleted
            
        Returns:
            Dictionary with deleted chart_ids and dashboard_ids
        """
        from .charts import delete_charts_by_username
        from .dashboard import delete_dashboards_by_username
        
        print(f"🧹 Cleaning up resources for user '{username}' (dry_run={dry_run})")
        
        chart_ids = delete_charts_by_username(self.session, self.base_url, username, dry_run)
        dashboard_ids = delete_dashboards_by_username(self.session, self.base_url, username, dry_run)
        
        return {
            "chart_ids": chart_ids,
            "dashboard_ids": dashboard_ids
        }
    
    # ========================================================================
    # PRIORITY 3: COMPOSITE OPERATIONS - Complete Workflows
    # ========================================================================
    
    def create_chart_from_table(
        self,
        chart_name: str,
        table: str,
        schema: str = None,
        owner: Optional[str] = None,
        database: str = None,
        chart_type: str = "table",
        **kwargs
    ) -> int:
        """
        Create any chart type from a table with full automatic setup.
        
        Args:
            chart_name: Name for the chart
            table: Source table name
            schema: Database schema (defaults to config)
            owner: Username for ownership (defaults to authenticated user)
            database: Database name (defaults to config)
            chart_type: Type of chart ("table", "pie", "histogram", "area")
            **kwargs: Chart-specific parameters
            
        Returns:
            Chart ID
        """
        from .ensure import get_database_id_by_name
        from .datasets import ensure_dataset, refresh_dataset_metadata
        from .charts import create_table_chart, create_pie_chart, create_histogram_chart, create_area_chart
        
        # Use config defaults
        schema = schema or self.config.schema
        database = database or self.config.database_name
        
        # Setup dataset
        database_id = get_database_id_by_name(self.session, self.base_url, database)
        dataset_id = ensure_dataset(self.session, self.base_url, database_id, schema, table)
        refresh_dataset_metadata(self.session, self.base_url, dataset_id)
        
        # Create appropriate chart type
        chart_functions = {
            "table": create_table_chart,
            "pie": create_pie_chart, 
            "histogram": create_histogram_chart,
            "area": create_area_chart
        }
        
        if chart_type not in chart_functions:
            raise ValueError(f"Unsupported chart type: {chart_type}. Supported: {list(chart_functions.keys())}")
        
        chart_function = chart_functions[chart_type]
        
        # Set sensible defaults based on chart type
        if chart_type == "table":
            kwargs.setdefault("columns", ["id"])
            kwargs.setdefault("row_limit", 1000)
            kwargs.setdefault("include_search", True)
        
        return chart_function(
            session=self.session,
            base_url=self.base_url,
            slice_name=chart_name,
            dataset_id=dataset_id,
            username=owner,
            **kwargs
        )
    
    def create_dashboard_with_charts(
        self,
        dashboard_title: str,
        slug: str,
        chart_configs: List[Dict[str, str]],
        owner: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Create dashboard and multiple charts in one operation.
        
        Args:
            dashboard_title: Dashboard title
            slug: Dashboard slug
            chart_configs: List of chart configurations, each with keys:
                           - name: Chart name
                           - table: Table name  
                           - type: Chart type (optional, defaults to "table")
                           - columns: Columns (optional)
            owner: Username for ownership (defaults to authenticated user)
            
        Returns:
            Dictionary with dashboard_id and list of chart_ids
        """
        print(f"🚀 Creating dashboard with {len(chart_configs)} charts...")
        
        # Create all charts first
        chart_ids = []
        chart_names = []
        
        for config in chart_configs:
            chart_name = config["name"]
            table = config["table"]
            chart_type = config.get("type", "table")
            columns = config.get("columns")
            
            chart_id = self.create_chart_from_table(
                chart_name=chart_name,
                table=table,
                owner=owner,
                chart_type=chart_type,
                columns=columns
            )
            
            chart_ids.append(chart_id)
            chart_names.append(chart_name)
            print(f"  ✅ Created chart '{chart_name}' (ID: {chart_id})")
        
        # Create dashboard with all charts
        dashboard_id = self.create_dashboard(
            title=dashboard_title,
            slug=slug,
            owner=owner,
            charts=chart_names
        )
        
        print(f"✅ Created complete dashboard with {len(chart_ids)} charts")
        
        return {
            "dashboard_id": dashboard_id,
            "chart_ids": chart_ids
        }
    
    def migrate_user_resources(
        self,
        from_user: str,
        to_user: str,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate all resources from one user to another.
        
        Args:
            from_user: Source username
            to_user: Target username  
            dry_run: If True, only shows what would be migrated
            
        Returns:
            Migration summary
        """
        print(f"🔄 Migrating resources from '{from_user}' to '{to_user}' (dry_run={dry_run})")
        
        # Get current resources
        charts = self.get_charts(owner=from_user)
        dashboards = self.get_dashboards(owner=from_user)
        
        if not charts and not dashboards:
            print(f"ℹ️  No resources found for user '{from_user}'")
            return {"migrated": 0, "charts": [], "dashboards": []}
        
        migrated_charts = []
        migrated_dashboards = []
        
        if not dry_run:
            # Resolve target user
            from .auth import get_user_id_by_username
            to_user_id = get_user_id_by_username(self.session, self.base_url, to_user)
            
            # Update chart ownership
            for chart in charts:
                chart_id = chart["id"]
                response = self.session.put(
                    f"{self.base_url}/api/v1/chart/{chart_id}",
                    json={"owners": [to_user_id]},
                    headers={"Referer": self.base_url}
                )
                if response.status_code in [200, 201]:
                    migrated_charts.append(chart_id)
                    print(f"  ✅ Migrated chart {chart_id}")
            
            # Update dashboard ownership
            for dashboard in dashboards:
                dashboard_id = dashboard["id"]
                response = self.session.put(
                    f"{self.base_url}/api/v1/dashboard/{dashboard_id}",
                    json={"owners": [to_user_id]}, 
                    headers={"Referer": self.base_url}
                )
                if response.status_code in [200, 201]:
                    migrated_dashboards.append(dashboard_id)
                    print(f"  ✅ Migrated dashboard {dashboard_id}")
        else:
            print(f"[DRY RUN] Would migrate {len(charts)} charts and {len(dashboards)} dashboards")
        
        return {
            "migrated": len(migrated_charts) + len(migrated_dashboards),
            "charts": migrated_charts,
            "dashboards": migrated_dashboards
        }
    
    def get_user_summary(self, username: str) -> Dict[str, Any]:
        """
        Get complete summary of user's resources.
        
        Args:
            username: Username to analyze
            
        Returns:
            Dictionary with charts, dashboards, and summary statistics
        """
        try:
            from .auth import get_user_id_by_username
            user_id = get_user_id_by_username(self.session, self.base_url, username)
            
            charts = self.get_charts(owner=username)
            dashboards = self.get_dashboards(owner=username)
            
            return {
                "username": username,
                "user_id": user_id,
                "charts": {
                    "count": len(charts),
                    "items": charts
                },
                "dashboards": {
                    "count": len(dashboards),
                    "items": dashboards
                },
                "summary": f"{len(charts)} charts, {len(dashboards)} dashboards"
            }
            
        except Exception as e:
            logger.error(f"Failed to get user summary for '{username}': {e}")
            return {
                "username": username,
                "error": str(e),
                "charts": {"count": 0, "items": []},
                "dashboards": {"count": 0, "items": []}
            }
    
    # ========================================================================
    # BATCH OPERATIONS
    # ========================================================================
    
    def create_charts_batch(
        self,
        chart_definitions: List[Dict[str, Any]],
        owner: Optional[str] = None
    ) -> List[int]:
        """
        Create multiple charts in batch.
        
        Args:
            chart_definitions: List of chart definitions, each with:
                              - name: Chart name
                              - table: Table name
                              - type: Chart type (optional, defaults to "table")
                              - schema: Schema (optional, uses config default)
                              - columns: Columns (optional)
                              - **kwargs: Chart-specific parameters
            owner: Username for ownership (defaults to authenticated user)
            
        Returns:
            List of created chart IDs
        """
        print(f"🚀 Creating {len(chart_definitions)} charts in batch...")
        
        chart_ids = []
        for i, chart_def in enumerate(chart_definitions, 1):
            try:
                chart_name = chart_def["name"]
                table = chart_def["table"]
                chart_type = chart_def.get("type", "table")
                schema = chart_def.get("schema")
                columns = chart_def.get("columns")
                
                print(f"📊 ({i}/{len(chart_definitions)}) Creating '{chart_name}'...")
                
                chart_id = self.create_chart_from_table(
                    chart_name=chart_name,
                    table=table,
                    schema=schema,
                    owner=owner,
                    chart_type=chart_type,
                    columns=columns,
                    **{k: v for k, v in chart_def.items() if k not in ["name", "table", "type", "schema", "columns"]}
                )
                
                chart_ids.append(chart_id)
                print(f"  ✅ Created chart ID: {chart_id}")
                
            except Exception as e:
                logger.error(f"Failed to create chart '{chart_def.get('name', 'unknown')}': {e}")
                print(f"  ❌ Failed to create chart: {e}")
        
        print(f"✅ Batch operation complete: {len(chart_ids)}/{len(chart_definitions)} charts created")
        return chart_ids
    
    def delete_charts_batch(self, chart_ids: List[int], dry_run: bool = True) -> List[int]:
        """
        Delete multiple charts in batch.
        
        Args:
            chart_ids: List of chart IDs to delete
            dry_run: If True, only shows what would be deleted
            
        Returns:
            List of successfully deleted chart IDs
        """
        from .charts import delete_chart
        
        print(f"🗑️ {'[DRY RUN] ' if dry_run else ''}Deleting {len(chart_ids)} charts in batch...")
        
        deleted_ids = []
        for i, chart_id in enumerate(chart_ids, 1):
            try:
                print(f"  ({i}/{len(chart_ids)}) Chart ID: {chart_id}")
                
                if not dry_run:
                    delete_chart(self.session, self.base_url, chart_id)
                    deleted_ids.append(chart_id)
                    
            except Exception as e:
                logger.error(f"Failed to delete chart {chart_id}: {e}")
                print(f"    ❌ Failed: {e}")
        
        if dry_run:
            print(f"ℹ️  DRY RUN: No charts were actually deleted. Set dry_run=False to delete.")
        else:
            print(f"✅ Batch delete complete: {len(deleted_ids)}/{len(chart_ids)} charts deleted")
        
        return deleted_ids
    
    # ========================================================================
    # PRIORITY 5: CONTEXT MANAGER SUPPORT
    # ========================================================================
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if exc_type is not None:
            logger.error(f"Exception in SupersetClient context: {exc_type.__name__}: {exc_val}")
        
        # Close session gracefully
        if hasattr(self.session, 'close'):
            self.session.close()
        
        logger.info("SupersetClient session closed")
        return False  # Don't suppress exceptions
    
    def validate_connection(self) -> Dict[str, Any]:
        """
        Validate connection and return system info.
        
        Returns:
            Dictionary with connection status and system information
        """
        try:
            # Test basic API access
            response = self.session.get(f"{self.base_url}/api/v1/chart/?q=%7B%22page_size%22%3A1%7D")
            
            if response.status_code == 200:
                chart_count = len(response.json().get("result", []))
                
                return {
                    "status": "connected",
                    "url": self.base_url,
                    "user_id": self.user_id,
                    "schema": self.config.schema,
                    "database": self.config.database_name,
                    "chart_count": chart_count,
                    "message": "Connection successful"
                }
            else:
                return {
                    "status": "error",
                    "message": f"API test failed: {response.status_code}",
                    "url": self.base_url
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection failed: {e}",
                "url": self.base_url
            }
    
    def __repr__(self) -> str:
        return f"SupersetClient(url='{self.config.superset_url}', user_id={self.user_id})"
