"""Main Superset client for API operations."""

from typing import Optional

import requests

from .config import Config, get_default_config
from .auth import create_session, login, attach_csrf_token, get_current_user_id
from .exceptions import AuthenticationError


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
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        session: Optional[requests.Session] = None
    ):
        """
        Initialize the Superset client.
        
        Args:
            config: Configuration object. If None, uses default config from environment
            session: Requests session. If None, creates a new session
        """
        self.config = config or get_default_config()
        self.session = session or create_session()
        self._user_id: Optional[int] = None
        
        # Authenticate immediately
        self._authenticate()
    
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
        """Get the current user ID, fetching it if not cached."""
        if self._user_id is None:
            self._user_id = get_current_user_id(self.session, self.config.superset_url)
        return self._user_id
    
    def refresh_auth(self) -> None:
        """Refresh authentication if needed."""
        self._authenticate()
        self._user_id = None  # Clear cached user ID
    
    def __repr__(self) -> str:
        return f"SupersetClient(url='{self.config.superset_url}', user_id={self.user_id})"
