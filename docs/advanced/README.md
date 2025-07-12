# Advanced Topics

This section covers advanced usage patterns, customization options, and expert-level techniques for OAS Patcher.

## Contents

- **[Custom Template Functions](./custom-template-functions.md)** - Extending the template engine with custom functions
- **[Error Handling](./error-handling.md)** - Advanced error handling strategies and debugging
- **[Performance Optimization](./performance.md)** - Optimizing overlay processing for large specifications
- **[Plugin Development](./plugin-development.md)** - Creating custom plugins and extensions
- **[Migration Strategies](./migration.md)** - Migrating from other tools and legacy specifications
- **[Integration Patterns](./integration-patterns.md)** - Advanced integration with CI/CD and tooling
- **[Debugging Techniques](./debugging.md)** - Advanced debugging and troubleshooting techniques
- **[Schema Validation](./schema-validation.md)** - Custom validation rules and schema enforcement

## Prerequisites

These topics assume familiarity with:

- Basic OAS Patcher usage and concepts
- OpenAPI Specification 3.0+
- Template engines (Jinja2)
- JSONPath expressions
- YAML/JSON data structures
- Command-line tools and scripting

## When to Use Advanced Features

Consider advanced features when you need:

- **Complex transformations** that basic overlays can't handle
- **Custom business logic** in your specification generation
- **Integration** with existing toolchains and workflows
- **Performance optimization** for large or numerous specifications
- **Error handling** beyond the standard error messages
- **Extensibility** for organization-specific requirements

## Best Practices for Advanced Usage

### 1. Start Simple
Always begin with basic overlays and gradually add complexity:

```yaml
# ✅ Start with simple transformations
- target: "$.info.title"
  update: "My API"

# ➡️ Add complexity gradually
- target: "$.info.title"
  update: "{{ API_NAME | title }} API v{{ API_VERSION }}"
```

### 2. Test Thoroughly
Advanced features require more rigorous testing:

```bash
# Test individual components
oas-patcher apply --overlay simple.yaml --dry-run
oas-patcher apply --overlay complex.yaml --dry-run

# Test integration
oas-patcher bundle apply --environment test --validate
```

### 3. Document Everything
Complex configurations need detailed documentation:

```yaml
# Document complex overlays
overlay: 1.0.0
info:
  title: "Complex Business Logic Overlay"
  version: "1.0.0"
  description: |
    This overlay implements custom business rules for:
    - Dynamic endpoint generation based on feature flags
    - Environment-specific security policies
    - Automated compliance annotations
    
    Required variables:
    - FEATURE_FLAGS: comma-separated list of enabled features
    - COMPLIANCE_LEVEL: standard|strict|custom
    
actions:
  # Each action should have detailed descriptions
  - target: "$.paths"
    update: "{{ generate_paths(FEATURE_FLAGS) }}"
    description: "Generate paths based on enabled feature flags"
```

### 4. Handle Errors Gracefully
Implement proper error handling and fallbacks:

```yaml
# Use defensive templating
- target: "$.servers[0].url"
  update: "{{ API_BASE_URL | default('https://localhost:8080') }}"
  description: "Set server URL with fallback"

# Validate inputs
- target: "$.info.version"
  update: |
    {% if API_VERSION | regex_match('^\\d+\\.\\d+\\.\\d+$') %}
    {{ API_VERSION }}
    {% else %}
    {{ error('Invalid API_VERSION format: ' + API_VERSION) }}
    {% endif %}
```

### 5. Optimize for Maintainability
Structure advanced configurations for long-term maintenance:

```
advanced-setup/
├── base/
│   └── openapi.yaml
├── functions/
│   ├── custom_functions.py
│   └── validators.py
├── overlays/
│   ├── core/
│   ├── features/
│   └── environments/
├── templates/
│   ├── schemas/
│   └── paths/
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    └── README.md
```

## Common Advanced Patterns

### 1. Conditional Content Generation

```yaml
# Generate content based on conditions
- target: "$.paths"
  update: |
    {% set paths = {} %}
    {% for endpoint in ENABLED_ENDPOINTS.split(',') %}
      {% set path_config = load_endpoint_config(endpoint) %}
      {% set paths = paths.update({path_config.path: path_config.definition}) %}
    {% endfor %}
    {{ paths }}
```

### 2. Cross-Reference Resolution

```yaml
# Automatically resolve schema references
- target: "$.components.schemas"
  update: "{{ resolve_schema_dependencies(BASE_SCHEMAS) }}"
  description: "Auto-resolve schema dependencies"
```

### 3. Compliance Automation

```yaml
# Add compliance annotations based on endpoint analysis
- target: "$.paths.*.*"
  update: |
    {% if has_personal_data(path, method) %}
    x-compliance:
      gdpr: true
      data-classification: "personal"
      retention-policy: "{{ PERSONAL_DATA_RETENTION }}"
    {% endif %}
```

### 4. Dynamic Schema Generation

```yaml
# Generate schemas from data models
- target: "$.components.schemas"
  update: "{{ generate_schemas_from_models(DATA_MODELS_PATH) }}"
  description: "Generate OpenAPI schemas from data models"
```

## Performance Considerations

### Memory Usage
- Use streaming for large specifications
- Implement lazy loading for complex templates
- Monitor memory usage during processing

### Processing Speed
- Cache template compilation results
- Parallelize independent overlay applications
- Use incremental processing for large bundles

### Scalability
- Design for horizontal scaling in CI/CD environments
- Implement proper resource limits
- Use efficient data structures for large specifications

## Security Considerations

### Template Security
- Sanitize user inputs in templates
- Restrict template function access
- Validate generated content

### Environment Variables
- Use secure secret management
- Implement variable validation
- Audit variable usage

### File Access
- Restrict file system access in templates
- Validate file paths and content
- Use sandboxed execution environments

## Getting Help

When working with advanced features:

1. **Check the source code** - Advanced usage often requires understanding implementation details
2. **Review test cases** - The test suite contains many advanced usage examples
3. **Join the community** - Get help from other advanced users
4. **Contribute back** - Share your advanced patterns with the community

## Contributing to Advanced Features

We welcome contributions to advanced functionality:

- **Custom functions** for common use cases
- **Performance improvements** for large-scale usage
- **Integration examples** with popular tools
- **Documentation** for complex scenarios
- **Test cases** for edge cases and advanced patterns

See the [Contributing Guide](../contributing.md) for details on how to contribute.
