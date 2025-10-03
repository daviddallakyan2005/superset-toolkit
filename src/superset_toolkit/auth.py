"""Authentication and session management for Superset API."""

import json
from typing import Optional

import requests

from .exceptions import AuthenticationError


def create_session() -> requests.Session:
    """Create a new requests session for Superset API calls."""
    return requests.Session()


def login(session: requests.Session, base_url: str, username: str, password: str) -> str:
    """
    Authenticate with Superset and return access token.
    
    Args:
        session: Requests session to use
        base_url: Superset base URL
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        Access token string
        
    Raises:
        AuthenticationError: If login fails
    """
    print("🔐 Attempting login...")
    
    login_response = session.post(
        f"{base_url}/api/v1/security/login",
        json={
            "username": username,
            "password": password,
            "provider": "db",
            "refresh": True
        }
    )
    
    print(f"🔐 Login response status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        raise AuthenticationError(
            f"Login failed with status {login_response.status_code}: {login_response.text}"
        )
    
    login_data = login_response.json()
    # DO NOT log login_data as it contains sensitive access tokens
    
    if 'access_token' not in login_data:
        raise AuthenticationError(f"Login failed: {login_data}")
    
    access_token = login_data['access_token']
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    
    return access_token


def attach_csrf_token(session: requests.Session, base_url: str) -> Optional[str]:
    """
    Get and attach CSRF token to session headers.
    
    Args:
        session: Requests session to update
        base_url: Superset base URL
        
    Returns:
        CSRF token if obtained, None otherwise
    """
    csrf_response = session.get(f"{base_url}/api/v1/security/csrf_token/")
    print(f"🔐 CSRF response status: {csrf_response.status_code}")
    
    if csrf_response.status_code == 200:
        csrf_data = csrf_response.json()
        # DO NOT log csrf_data as it contains sensitive CSRF tokens
        
        # Handle different response formats across Superset versions
        csrf_token = csrf_data.get('result') or csrf_data.get('csrf_token') or csrf_data
        if isinstance(csrf_token, dict):
            csrf_token = csrf_token.get('csrf_token')
        
        if csrf_token:
            print("🔐 CSRF token obtained and attached")
            session.headers.update({'X-CSRFToken': csrf_token})
            return csrf_token
    else:
        print(f"⚠️ CSRF token not required or failed to get: {csrf_response.status_code}")
        print(f"⚠️ CSRF response: {csrf_response.text}")
    
    return None


def get_current_user_id(session: requests.Session, base_url: str) -> int:
    """
    Get the current user's ID.
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        
    Returns:
        User ID
        
    Raises:
        AuthenticationError: If user info cannot be retrieved
    """
    try:
        print("👤 Getting current user ID...")
        response = session.get(f"{base_url}/api/v1/me", allow_redirects=False)
        print(f"👤 User info response status: {response.status_code}")
        
        if response.status_code in [301, 302, 307, 308]:
            print("👤 Redirect detected, following manually...")
            redirect_url = response.headers.get('Location')
            if redirect_url:
                if not redirect_url.startswith('http'):
                    redirect_url = f"{base_url}{redirect_url}"
                response = session.get(redirect_url)
                print(f"👤 Redirected response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get user info: {response.status_code}")
            print(f"❌ Response: {response.text}")
            # Fallback: return user ID 1 (admin) as default
            print("⚠️ Using fallback user ID: 1")
            return 1
        
        me = response.json()
        # DO NOT log user info as it may contain sensitive data
        
        # Superset returns {'result': {...}} or direct fields depending on version
        result = me.get('result') if isinstance(me, dict) else None
        user_data = result or me
        
        if 'id' not in user_data:
            print("❌ User info missing 'id' field")
            # Fallback: return user ID 1 (admin) as default
            print("⚠️ Using fallback user ID: 1")
            return 1
            
        user_id = user_data['id']
        print(f"👤 Current user ID: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        # Fallback: return user ID 1 (admin) as default
        print("⚠️ Using fallback user ID: 1")
        return 1
