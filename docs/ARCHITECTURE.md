# Architecture Overview

## Package Structure

```
superset-toolkit/
├── src/superset_toolkit/          # Main package
│   ├── __init__.py                # Public API exports
│   ├── client.py                  # SupersetClient main class
│   ├── config.py                  # Configuration management
│   ├── auth.py                    # Authentication & session
│   ├── datasets.py                # Dataset CRUD operations
│   ├── charts.py                  # Chart creation functions
│   ├── dashboard.py               # Dashboard management
│   ├── ensure.py                  # Idempotent resource helpers
│   ├── exceptions.py              # Custom exceptions
│   ├── cli.py                     # Command-line interface
│   ├── flows/                     # Orchestrated flows
│   │   ├── __init__.py
│   │   └── timelapse_dash_illustration.py
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       └── metrics.py
├── examples/                      # Usage examples
├── tests/                         # Test suite
├── docs/                         # Documentation
└── pyproject.toml                # Package metadata
```

## Module Responsibilities

### `client.py` - Main Entry Point
- `SupersetClient` class that manages authentication and provides high-level access
- Owns the requests session and configuration
- Provides access to user ID and base URL
- Single entry point for all operations

### `auth.py` - Authentication Management
- Session creation and management
- Login with username/password
- CSRF token handling
- Current user identification
- No business logic, pure authentication concerns

### `config.py` - Configuration Management
- Environment variable resolution
- Default value management
- Configuration validation
- Supports override via constructor parameters

### `datasets.py` - Dataset Operations
- Dataset creation and management
- Metadata refresh operations
- Column discovery
- Main datetime column configuration
- Pure dataset operations without orchestration

### `charts.py` - Chart Creation
- Chart creation functions for all visualization types
- Parameterized chart builders
- Metric configuration handling
- No orchestration, just individual chart operations

### `dashboard.py` - Dashboard Management
- Dashboard creation and management
- Layout composition (2 charts per row)
- Custom CSS application
- Chart-to-dashboard linking
- Position JSON management

### `ensure.py` - Idempotent Operations
- "Ensure" patterns (create-or-get)
- Resource ID lookups by name/criteria
- Chart matching by name, dataset, and owner
- Generic API filtering helpers

### `flows/` - Orchestration
- High-level business flows
- Coordinates multiple operations
- Contains domain-specific logic
- Example: `timelapse_dash_illustration.py` orchestrates the entire dashboard creation

### `utils/` - Utilities
- Metric builders (`build_simple_metric`, `build_sql_metric`)
- Reusable helper functions
- No API calls, pure utility functions

### `exceptions.py` - Error Handling
- Custom exception hierarchy
- Domain-specific error types
- Consistent error handling across modules

### `cli.py` - Command Line Interface
- Typer-based CLI with rich output
- Optional dependency (install with `[cli]` extra)
- Delegates to package API, no business logic

## Design Principles

### 1. Separation of Concerns
- Each module has a single, clear responsibility
- Authentication is separate from business logic
- Configuration is centralized
- Orchestration is separate from individual operations

### 2. Dependency Injection
- `SupersetClient` owns the session and config
- All functions accept `session`, `base_url`, and required parameters
- No global state or hidden dependencies

### 3. Idempotent Operations
- "Ensure" patterns for all resources
- Safe to run multiple times
- Handles existing resources gracefully

### 4. Type Safety
- Full type hints throughout
- Optional parameters clearly marked
- Return types specified

### 5. Error Handling
- Custom exceptions for different error types
- Consistent error propagation
- Graceful fallbacks where appropriate

### 6. Extensibility
- New flows can be added easily
- Chart types are parameterized and extensible
- Configuration supports overrides

## Data Flow

### Authentication Flow
1. `SupersetClient` creates session via `auth.create_session()`
2. Calls `auth.login()` with credentials
3. Calls `auth.attach_csrf_token()` for CSRF protection
4. Caches user ID via `auth.get_current_user_id()`

### Resource Creation Flow
1. Flow calls `ensure.*()` functions to check for existing resources
2. If not found, calls appropriate `create_*()` function
3. Returns resource ID for further operations
4. All operations are idempotent

### Dashboard Creation Flow
1. Ensure all datasets exist and are refreshed
2. Create all required charts
3. Create dashboard
4. Add charts to dashboard layout
5. Apply custom styling

## Extension Points

### Adding New Chart Types
1. Add creation function to `charts.py`
2. Follow existing parameter patterns
3. Return chart ID
4. Add to flows as needed

### Adding New Flows
1. Create new file in `flows/`
2. Accept `SupersetClient` as parameter
3. Coordinate multiple operations
4. Add to `flows/__init__.py`

### Adding New Configuration
1. Add to `Config` class in `config.py`
2. Support environment variable
3. Allow constructor override
4. Update documentation

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock HTTP requests
- Test parameter validation
- Test error handling

### Integration Tests
- Test against real Superset instance
- Use environment variables for configuration
- Skip if credentials not available
- Test complete flows

### Contract Tests
- Test API payload structure
- Ensure compatibility with Superset versions
- Test response parsing
