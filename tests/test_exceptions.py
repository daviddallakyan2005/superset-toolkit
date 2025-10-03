"""Test custom exceptions."""

from superset_toolkit.exceptions import (
    SupersetToolkitError,
    AuthenticationError,
    SupersetApiError,
    DatasetNotFoundError,
    ChartCreationError,
    DashboardError
)


def test_superset_toolkit_error():
    """Test base SupersetToolkitError."""
    error = SupersetToolkitError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_authentication_error():
    """Test AuthenticationError inherits from SupersetToolkitError."""
    error = AuthenticationError("Auth failed")
    assert str(error) == "Auth failed"
    assert isinstance(error, SupersetToolkitError)


def test_superset_api_error():
    """Test SupersetApiError with additional attributes."""
    error = SupersetApiError("API error", status_code=400, response_text="Bad request")
    assert str(error) == "API error"
    assert error.status_code == 400
    assert error.response_text == "Bad request"
    assert isinstance(error, SupersetToolkitError)


def test_superset_api_error_minimal():
    """Test SupersetApiError with just message."""
    error = SupersetApiError("Simple API error")
    assert str(error) == "Simple API error"
    assert error.status_code is None
    assert error.response_text is None


def test_dataset_not_found_error():
    """Test DatasetNotFoundError."""
    error = DatasetNotFoundError("Dataset not found")
    assert str(error) == "Dataset not found"
    assert isinstance(error, SupersetToolkitError)


def test_chart_creation_error():
    """Test ChartCreationError."""
    error = ChartCreationError("Chart creation failed")
    assert str(error) == "Chart creation failed"
    assert isinstance(error, SupersetToolkitError)


def test_dashboard_error():
    """Test DashboardError."""
    error = DashboardError("Dashboard operation failed")
    assert str(error) == "Dashboard operation failed"
    assert isinstance(error, SupersetToolkitError)
