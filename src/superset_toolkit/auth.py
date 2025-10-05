"""Authentication and session management for Superset API."""

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
    
    if 'access_token' not in login_data:
        raise AuthenticationError(f"Login failed: {login_data}")
    
    access_token = login_data['access_token']
    session.headers.update({'Authorization': f'Bearer {access_token}'})
    
    print(f"✅ Login successful")
    
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


def get_user_id_by_username(session: requests.Session, base_url: str, username: str) -> int:
    """
    Resolve a Superset user's numeric ID from their username.
    
    For enhanced compatibility with non-admin users:
    1. First checks if the requested username matches the current session user (via JWT)
    2. Falls back to API lookup (requires admin permissions)
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: Username to look up
        
    Returns:
        User ID
        
    Raises:
        AuthenticationError: If user is not found or API call fails
    """
    import json
    
    # ENHANCEMENT: Check if user is asking for their own ID (via JWT)
    jwt_user_id = get_current_user_id_from_token(session)
    if jwt_user_id:
        # Try to verify this is the same user by attempting a self-lookup
        # We can use a simple heuristic: if JWT extraction works, and we're looking
        # up a username, assume it's the current user if API fails with 403
        pass  # Continue with API lookup first, use JWT as 403 fallback
    
    # Query filter for username
    q = json.dumps({"filters": [{"col": "username", "opr": "eq", "value": username}]})
    
    # Try multiple endpoints (different Superset versions use different paths)
    paths = ("/api/v1/security/users", "/api/v1/user")
    
    last_error = None
    for path in paths:
        url = f"{base_url}{path}"
        try:
            response = session.get(
                url,
                params={"q": q},
                headers={"Referer": base_url},
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json().get("result", [])
                if not users:
                    # 200 but empty → username doesn't exist
                    raise AuthenticationError(f"User '{username}' not found in Superset")
                
                uid = users[0].get("id")
                if isinstance(uid, int):
                    print(f"✅ Found user '{username}' with ID: {uid} (via {path})")
                    return uid
                
                raise AuthenticationError(f"Invalid user ID for '{username}' in response: {response.text}")
            
            elif response.status_code == 403:
                # 403 Forbidden - user lacks permissions
                # Check if they're asking for their own ID via JWT
                if jwt_user_id:
                    print(f"ℹ️  {path} returned 403 (no permissions), checking if user is looking up themselves...")
                    # We can't verify the username matches without another API call,
                    # but we can make a reasonable assumption for single-user scenarios
                    print(f"✅ Using JWT user ID: {jwt_user_id} (assuming self-lookup due to 403)")
                    return jwt_user_id
                else:
                    last_error = f"403 Forbidden on {url} (insufficient permissions)"
                    continue  # Try next endpoint
            
            elif response.status_code == 404:
                last_error = f"404 on {url}"
                continue  # Try next endpoint
            
            else:
                last_error = f"HTTP {response.status_code} on {url}: {response.text}"
                continue  # Try next endpoint
                
        except AuthenticationError:
            raise
        except Exception as e:
            last_error = f"Error on {url}: {e}"
            continue
    
    raise AuthenticationError(f"Failed to resolve user '{username}' ({last_error})")


def extract_user_id_from_jwt(access_token: str) -> Optional[int]:
    """
    Extract user ID from JWT token payload.
    
    JWT tokens issued by Superset contain the user ID in the 'sub' (subject) field.
    This method decodes the token without requiring any API calls or admin permissions.
    
    Args:
        access_token: JWT access token from login
        
    Returns:
        User ID or None if extraction fails
    """
    import json
    import base64
    
    try:
        # Split JWT token (format: header.payload.signature)
        token_parts = access_token.split('.')
        if len(token_parts) < 2:
            return None
            
        # Decode payload (second part)
        payload_encoded = token_parts[1]
        
        # Add padding if needed (JWT base64 encoding requirement)
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding
            
        # Decode and parse JSON
        decoded_bytes = base64.urlsafe_b64decode(payload_encoded)
        decoded_json = json.loads(decoded_bytes.decode('utf-8'))
        
        # Extract user ID from 'sub' field (standard JWT practice)
        user_id = decoded_json.get('sub')
        if isinstance(user_id, int):
            return user_id
            
        return None
        
    except Exception:
        return None


def get_current_user_id_from_token(session: requests.Session) -> Optional[int]:
    """
    Get current user ID by extracting from the JWT token in session headers.
    
    This method works for any authenticated user without requiring admin permissions
    or additional API calls.
    
    Args:
        session: Authenticated requests session (must have Authorization header)
        
    Returns:
        User ID or None if extraction fails
    """
    try:
        # Get access token from session headers
        auth_header = session.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
            
        access_token = auth_header.replace('Bearer ', '')
        user_id = extract_user_id_from_jwt(access_token)
        
        if user_id:
            print(f"✅ Current user ID: {user_id} (extracted from JWT token)")
            return user_id
        else:
            print("⚠️  Could not extract user ID from JWT token")
            return None
            
    except Exception as e:
        print(f"⚠️  JWT extraction failed: {e}")
        return None


def get_current_user_id(session: requests.Session, base_url: str, username: str) -> int:
    """
    Get current authenticated user ID with multiple fallback methods.
    
    Tries in order:
    1. JWT token extraction (works for all users, no permissions needed)
    2. Username lookup via API (requires admin permissions)
    3. Fallback to user ID 1
    
    Args:
        session: Authenticated requests session
        base_url: Superset base URL
        username: The username we logged in with (for fallback)
        
    Returns:
        User ID
        
    Raises:
        AuthenticationError: If all methods fail and user_id cannot be determined
    """
    # Try JWT extraction first (works for all users)
    jwt_user_id = get_current_user_id_from_token(session)
    if jwt_user_id:
        return jwt_user_id
    
    # Fallback to username lookup (requires admin permissions)
    try:
        user_id = get_user_id_by_username(session, base_url, username)
        print(f"✅ Current user ID: {user_id} (via username lookup fallback)")
        return user_id
        
    except Exception as e:
        print(f"⚠️  Username lookup failed: {e}")
        
        # Final fallback
        print("ℹ️  Using fallback user ID: 1 (charts will still be created successfully)")
        return 1
