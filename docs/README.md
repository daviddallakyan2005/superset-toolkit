# 📖 Superset Toolkit Documentation

Complete documentation for the professional Superset Toolkit SDK.

## 🚀 Getting Started

- 📋 **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- ⚙️ **[Superset Setup](SUPERSET_SETUP.md)** - Required server configuration  
- 🔧 **[Configuration Guide](CONFIGURATION.md)** - SDK setup and customization
- 👤 **[User Management](USER_MANAGEMENT.md)** - Username-aware operations and permissions

## 📚 Reference Documentation

- 📖 **[API Reference](API_REFERENCE.md)** - Complete class and function reference
- 🎯 **[Examples Directory](../examples/)** - Ready-to-run code examples

## 🎯 Key Features Covered

### Professional SDK Design
- **Client-Centric Operations**: No more `(session, base_url)` repetition
- **Username-Aware Functions**: Work with usernames directly
- **JWT-Based Authentication**: Robust user ID extraction
- **Composite Workflows**: Complete operations in single calls
- **Batch Operations**: Efficient bulk management
- **Context Managers**: Automatic resource cleanup

### Advanced Capabilities
- **Permission-Aware Fallbacks**: Works with any user type
- **Resource Lifecycle Management**: Query, migrate, cleanup
- **Error Handling**: Professional exception handling
- **Multi-User Support**: Team-based resource management

## 📁 Documentation Structure

```
docs/
├── README.md              # This overview
├── QUICK_START.md         # 5-minute setup guide
├── CONFIGURATION.md       # Setup and config options
├── USER_MANAGEMENT.md     # Username operations & permissions  
└── API_REFERENCE.md       # Complete API documentation
```

## 🎯 Example Categories

```
examples/
├── professional_client_usage.py   # Client-centric patterns
├── standalone_functions.py        # Enhanced standalone functions
├── multi_user_workflows.py        # Team and permission scenarios
├── batch_operations.py            # Efficient bulk operations
├── basic_usage.py                 # Simple getting started
└── custom_config.py               # Configuration patterns
```

## 📊 Architecture Overview

### Before (Traditional SDK)
```python
# Parameter repetition, manual ID resolution, fragmented operations
user_id = get_user_id_by_username(session, base_url, "john")
dataset_id = ensure_dataset(session, base_url, db_id, schema, table)
chart_id = create_table_chart(session, base_url, name, dataset_id, user_id)
dashboard_id = ensure_dashboard(session, base_url, title, slug)
link_chart_to_dashboard(session, base_url, chart_id, dashboard_id)
```

### After (Professional SDK)
```python
# Clean, username-first, composite operations
with SupersetClient() as client:
    chart_id = client.create_table_chart("Report", table="sales", owner="john")
    dashboard_id = client.create_dashboard("Dashboard", "dash", charts=["Report"])
```

## 🛡️ Permission Handling

The SDK gracefully handles different user permission levels:

| User Type | Capabilities | Limitations | SDK Behavior |
|-----------|--------------|-------------|--------------|
| **Admin** | Full access to all operations | None | ✅ Full functionality |
| **Regular** | Can create charts/dashboards | Cannot query other users | ✅ JWT extraction, graceful fallbacks |
| **Limited** | Basic operations | Restricted permissions | ✅ Safe fallbacks to user_id=1 |

## 🎯 Common Use Cases

1. **[Single User Automation](../examples/professional_client_usage.py)** - Personal dashboards
2. **[Team Resource Management](../examples/multi_user_workflows.py)** - Multi-user scenarios  
3. **[Bulk Operations](../examples/batch_operations.py)** - Efficient mass creation
4. **[Legacy Migration](../examples/standalone_functions.py)** - Upgrading existing code

## 🔍 Troubleshooting

### Common Issues

**Authentication Problems**
- Check credentials in configuration
- Verify Superset instance URL
- See [Configuration Guide](CONFIGURATION.md#troubleshooting)

**Permission Errors** 
- SDK handles most gracefully with JWT extraction
- Admin users have full capabilities
- See [User Management](USER_MANAGEMENT.md#permission-scenarios)

**Resource Not Found**
- Verify table/database names
- Check user permissions
- Use `client.validate_connection()` for diagnostics

## 🚀 Best Practices

1. **Use client methods** for new code (professional patterns)
2. **Use context managers** for production deployments
3. **Specify usernames explicitly** for multi-user environments
4. **Handle permissions gracefully** - SDK provides automatic fallbacks
5. **Validate connections** before bulk operations
6. **Use batch operations** for multiple resources

## 📞 Support & Contributing

- 🐛 **Issues**: File issues for bugs or feature requests
- 📖 **Documentation**: Contributions to docs are welcome
- 🔧 **Development**: See development guidelines in main README
- 💬 **Community**: Share usage patterns and improvements

---

**The Superset Toolkit provides professional-grade automation for Apache Superset with modern SDK patterns and robust permission handling.**
