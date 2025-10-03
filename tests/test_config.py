"""Test configuration management."""

import os
import pytest
from unittest.mock import patch

from superset_toolkit.config import Config, get_default_config


def test_config_with_all_parameters():
    """Test Config with all parameters provided."""
    config = Config(
        superset_url="https://test.example.com",
        username="testuser",
        password="testpass",
        schema="testschema",
        database_name="TestDB"
    )
    
    assert config.superset_url == "https://test.example.com"
    assert config.username == "testuser"
    assert config.password == "testpass"
    assert config.schema == "testschema"
    assert config.database_name == "TestDB"


@patch.dict(os.environ, {
    'SUPERSET_URL': 'https://env.example.com',
    'SUPERSET_USERNAME': 'envuser',
    'SUPERSET_PASSWORD': 'envpass',
    'SUPERSET_SCHEMA': 'envschema',
    'SUPERSET_DATABASE_NAME': 'EnvDB'
})
def test_config_from_environment():
    """Test Config loading from environment variables."""
    config = Config()
    
    assert config.superset_url == "https://env.example.com"
    assert config.username == "envuser"
    assert config.password == "envpass"
    assert config.schema == "envschema"
    assert config.database_name == "EnvDB"


def test_config_missing_credentials():
    """Test Config raises error when credentials are missing."""
    with pytest.raises(ValueError, match="SUPERSET_USERNAME and SUPERSET_PASSWORD must be set"):
        Config()


@patch.dict(os.environ, {'SUPERSET_USERNAME': 'testuser', 'SUPERSET_PASSWORD': 'testpass'})
def test_config_defaults():
    """Test Config uses defaults when not provided."""
    config = Config()
    
    assert config.superset_url == "https://your-superset-instance.com"
    assert config.schema == "reports"
    assert config.database_name == "Trino"


@patch.dict(os.environ, {'SUPERSET_USERNAME': 'testuser', 'SUPERSET_PASSWORD': 'testpass'})
def test_get_default_config():
    """Test get_default_config function."""
    config = get_default_config()
    assert isinstance(config, Config)
    assert config.username == "testuser"
