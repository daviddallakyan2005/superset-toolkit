"""Test authentication functions."""

import pytest
from unittest.mock import Mock, patch
import requests

from superset_toolkit.auth import create_session, login, attach_csrf_token, get_current_user_id
from superset_toolkit.exceptions import AuthenticationError


def test_create_session():
    """Test session creation."""
    session = create_session()
    assert isinstance(session, requests.Session)


@patch('superset_toolkit.auth.print')  # Mock print to avoid output during tests
def test_login_success(mock_print):
    """Test successful login."""
    # Mock session and response
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'access_token': 'test_token'}
    session.post.return_value = response_mock
    
    # Test login
    token = login(session, "https://test.com", "user", "pass")
    
    # Assertions
    assert token == "test_token"
    session.post.assert_called_once_with(
        "https://test.com/api/v1/security/login",
        json={
            "username": "user",
            "password": "pass",
            "provider": "db",
            "refresh": True
        }
    )
    session.headers.update.assert_called_once_with({'Authorization': 'Bearer test_token'})


@patch('superset_toolkit.auth.print')
def test_login_failure(mock_print):
    """Test login failure."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 401
    response_mock.text = "Unauthorized"
    session.post.return_value = response_mock
    
    with pytest.raises(AuthenticationError, match="Login failed with status 401"):
        login(session, "https://test.com", "user", "wrongpass")


@patch('superset_toolkit.auth.print')
def test_login_no_token(mock_print):
    """Test login with missing access token."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'error': 'no token'}
    session.post.return_value = response_mock
    
    with pytest.raises(AuthenticationError, match="Login failed"):
        login(session, "https://test.com", "user", "pass")


@patch('superset_toolkit.auth.print')
def test_attach_csrf_token_success(mock_print):
    """Test successful CSRF token attachment."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'result': 'test_csrf_token'}
    session.get.return_value = response_mock
    
    token = attach_csrf_token(session, "https://test.com")
    
    assert token == "test_csrf_token"
    session.get.assert_called_once_with("https://test.com/api/v1/security/csrf_token/")
    session.headers.update.assert_called_once_with({'X-CSRFToken': 'test_csrf_token'})


@patch('superset_toolkit.auth.print')
def test_attach_csrf_token_different_format(mock_print):
    """Test CSRF token with different response format."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'csrf_token': 'test_csrf_token'}
    session.get.return_value = response_mock
    
    token = attach_csrf_token(session, "https://test.com")
    
    assert token == "test_csrf_token"


@patch('superset_toolkit.auth.print')
def test_attach_csrf_token_failure(mock_print):
    """Test CSRF token failure."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 404
    response_mock.text = "Not found"
    session.get.return_value = response_mock
    
    token = attach_csrf_token(session, "https://test.com")
    
    assert token is None


@patch('superset_toolkit.auth.print')
def test_get_current_user_id_success(mock_print):
    """Test successful user ID retrieval."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'result': {'id': 123}}
    session.get.return_value = response_mock
    
    user_id = get_current_user_id(session, "https://test.com")
    
    assert user_id == 123
    session.get.assert_called_once_with("https://test.com/api/v1/me", allow_redirects=False)


@patch('superset_toolkit.auth.print')
def test_get_current_user_id_direct_format(mock_print):
    """Test user ID retrieval with direct format."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {'id': 456}
    session.get.return_value = response_mock
    
    user_id = get_current_user_id(session, "https://test.com")
    
    assert user_id == 456


@patch('superset_toolkit.auth.print')
def test_get_current_user_id_fallback(mock_print):
    """Test user ID fallback to 1."""
    session = Mock()
    response_mock = Mock()
    response_mock.status_code = 500
    response_mock.text = "Server error"
    session.get.return_value = response_mock
    
    user_id = get_current_user_id(session, "https://test.com")
    
    assert user_id == 1  # Fallback value
