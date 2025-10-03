"""Custom exceptions for Superset Toolkit."""


class SupersetToolkitError(Exception):
    """Base exception for all Superset Toolkit errors."""
    pass


class AuthenticationError(SupersetToolkitError):
    """Raised when authentication fails."""
    pass


class SupersetApiError(SupersetToolkitError):
    """Raised when Superset API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class DatasetNotFoundError(SupersetToolkitError):
    """Raised when a dataset cannot be found."""
    pass


class ChartCreationError(SupersetToolkitError):
    """Raised when chart creation fails."""
    pass


class DashboardError(SupersetToolkitError):
    """Raised when dashboard operations fail."""
    pass
