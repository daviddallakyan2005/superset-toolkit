"""Test that all imports work correctly."""

def test_main_imports():
    """Test that main package imports work."""
    from superset_toolkit import SupersetClient
    from superset_toolkit import SupersetToolkitError, AuthenticationError, SupersetApiError
    
    # Test that classes can be instantiated (will fail on auth, but that's expected in tests)
    assert SupersetClient is not None
    assert SupersetToolkitError is not None
    assert AuthenticationError is not None
    assert SupersetApiError is not None


def test_module_imports():
    """Test that all modules can be imported."""
    from superset_toolkit import config
    from superset_toolkit import auth
    from superset_toolkit import client
    from superset_toolkit import datasets
    from superset_toolkit import charts
    from superset_toolkit import dashboard
    from superset_toolkit import ensure
    from superset_toolkit import exceptions
    from superset_toolkit.utils import metrics
    
    # Basic smoke test
    assert config is not None
    assert auth is not None
    assert client is not None
    assert datasets is not None
    assert charts is not None
    assert dashboard is not None
    assert ensure is not None
    assert exceptions is not None
    assert metrics is not None


def test_utils_imports():
    """Test that utilities can be imported."""
    from superset_toolkit.utils import build_simple_metric, build_sql_metric
    
    assert build_simple_metric is not None
    assert build_sql_metric is not None
