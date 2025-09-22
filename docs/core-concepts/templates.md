# Template Engine

The OAS Patcher template engine provides powerful dynamic content generation capabilities using Jinja2 templating. This allows you to create overlays that adapt to different environments, incorporate runtime variables, and generate content programmatically.

## Template Engine Overview

The template engine processes overlay files before they are applied to OpenAPI specifications. It supports:

- **Jinja2 templating syntax** for dynamic content generation
- **Environment variable resolution** with multiple syntax options
- **Custom filters** for data transformation
- **Variable inheritance** from bundles and CLI
- **Conditional logic** for environment-specific configurations

## Basic Template Syntax

Templates use Jinja2 syntax with double curly braces for variable substitution:

```yaml
overlay: 1.0.0
info:
  title: "{{ bundle_name }} Overlay"
  version: "{{ api_version }}"
actions:
  - target: "$.info.version"
    update: "{{ api_version }}"
  - target: "$.servers[0].url"
    update: "{{ base_url }}/{{ api_version }}"
```

## Variable Sources

Variables can come from multiple sources with a clear precedence order:

### 1. CLI Variables (Highest Precedence)

```bash
oas-patch bundle apply api.yaml my-bundle \
  --variable api_version=v2.1 \
  --variable environment=production
```

### 2. Environment Variables

```yaml
# Direct environment variable access
actions:
  - target: "$.info.version"
    update: "{{ env('API_VERSION') }}"
    
  # With default values
  - target: "$.servers[0].url"
    update: "{{ env('API_BASE_URL', 'https://api.example.com') }}"
```

### 3. Bundle Variables

```yaml
# In bundle.yaml
variables:
  api_version: "v2.0"
  company_name: "Acme Corp"
```

### 4. Overlay Variables

```yaml
# In bundle.yaml overlay configuration
overlays:
  - path: "overlays/environment.yaml"
    variables:
      deployment_region: "us-west-2"
      cache_ttl: 3600
```

## Environment Variable Syntax

The template engine supports multiple ways to access environment variables:

### Jinja2 Function Syntax

```yaml
# Basic usage
database_url: "{{ env('DATABASE_URL') }}"

# With default value
database_url: "{{ env('DATABASE_URL', 'postgresql://localhost:5432/myapp') }}"

# Complex default
api_config:
  base_url: "{{ env('API_BASE_URL', 'https://api.example.com') }}"
  timeout: "{{ env('API_TIMEOUT', '30') | int }}"
```

### ENV Namespace

```yaml
# Access via ENV namespace
database_url: "{{ ENV.DATABASE_URL }}"
api_key: "{{ ENV.API_SECRET_KEY }}"

# Can be combined with filters
timeout: "{{ ENV.REQUEST_TIMEOUT | default(30) | int }}"
```

### Shell-Style Substitution

```yaml
# Basic substitution
database_url: "${DATABASE_URL}"

# With default values
api_url: "${API_BASE_URL:https://api.example.com}"
port: "${API_PORT:8080}"
```

## Custom Filters

The template engine includes custom filters for common transformations:

### to_yaml Filter

Convert objects to YAML format:

```yaml
actions:
  - target: "$.components.examples.UserExample"
    update: |
      {{ user_data | to_yaml }}
```

### to_json Filter

Convert objects to JSON format:

```yaml
actions:
  - target: "$.paths./config.get.responses.200.content.application/json.example"
    update: "{{ config_object | to_json }}"
```

### Built-in Jinja2 Filters

All standard Jinja2 filters are available:

```yaml
# String manipulation
api_name: "{{ service_name | upper }}-API"
version: "{{ version_number | replace('.', '-') }}"

# Type conversion
port: "{{ port_string | int }}"
enabled: "{{ feature_flag | bool }}"

# Default values
timeout: "{{ request_timeout | default(30) }}"
```

## Conditional Logic

Use Jinja2 conditional statements for environment-specific configurations:

```yaml
overlay: 1.0.0
info:
  title: "API Configuration"
actions:
  {% if environment == "production" %}
  - target: "$.servers"
    update:
      - url: "https://api.example.com"
        description: "Production server"
  {% elif environment == "staging" %}
  - target: "$.servers"
    update:
      - url: "https://staging-api.example.com"
        description: "Staging server"
  {% else %}
  - target: "$.servers"
    update:
      - url: "http://localhost:3000"
        description: "Development server"
  {% endif %}
  
  {% if enable_security %}
  - target: "$.security"
    update:
      - BearerAuth: []
  {% endif %}
```

## Loops and Iteration

Generate repetitive configurations using loops:

```yaml
actions:
  # Generate multiple server configurations
  {% for region in regions %}
  - target: "$.servers[{{ loop.index0 }}]"
    update:
      url: "https://{{ region }}-api.example.com"
      description: "{{ region | title }} region server"
  {% endfor %}
  
  # Generate schema properties
  {% for field in user_fields %}
  - target: "$.components.schemas.User.properties.{{ field.name }}"
    update:
      type: "{{ field.type }}"
      description: "{{ field.description }}"
  {% endfor %}
```

## Complex Template Examples

### Multi-Environment Server Configuration

```yaml
overlay: 1.0.0
info:
  title: "Environment Server Configuration"
actions:
  - target: "$.servers"
    update:
      {% if environment == "production" %}
      - url: "{{ env('PROD_API_URL', 'https://api.example.com') }}"
        description: "Production server"
      {% elif environment == "staging" %}
      - url: "{{ env('STAGING_API_URL', 'https://staging-api.example.com') }}"
        description: "Staging server"
      {% else %}
      - url: "{{ env('DEV_API_URL', 'http://localhost:8080') }}"
        description: "Development server"
      {% endif %}
```

### Dynamic Security Configuration

```yaml
overlay: 1.0.0
info:
  title: "Security Configuration"
actions:
  {% if auth_type == "oauth2" %}
  - target: "$.components.securitySchemes.OAuth2"
    update:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: "{{ oauth_auth_url }}"
          tokenUrl: "{{ oauth_token_url }}"
          scopes:
            {% for scope in oauth_scopes %}
            {{ scope.name }}: "{{ scope.description }}"
            {% endfor %}
  {% elif auth_type == "apikey" %}
  - target: "$.components.securitySchemes.ApiKeyAuth"
    update:
      type: apiKey
      in: header
      name: "{{ api_key_header | default('X-API-Key') }}"
  {% endif %}
```

### Database Configuration Template

```yaml
overlay: 1.0.0
info:
  title: "Database Configuration"
actions:
  - target: "$.info.x-database-config"
    update:
      host: "{{ env('DB_HOST') }}"
      port: "{{ env('DB_PORT', '5432') | int }}"
      database: "{{ env('DB_NAME') }}"
      ssl: "{{ env('DB_SSL_ENABLED', 'true') | bool }}"
      pool_size: "{{ env('DB_POOL_SIZE', '10') | int }}"
      {% if environment == "production" %}
      read_replicas:
        {% for i in range(replica_count | int) %}
        - host: "{{ env('DB_READ_REPLICA_' + loop.index|string + '_HOST') }}"
          port: "{{ env('DB_PORT', '5432') | int }}"
        {% endfor %}
      {% endif %}
```

## Template Best Practices

### 1. Use Meaningful Variable Names

```yaml
# Good
api_base_url: "{{ env('API_BASE_URL') }}"
database_connection_string: "{{ env('DATABASE_URL') }}"

# Avoid
url: "{{ env('URL') }}"
db: "{{ env('DB') }}"
```

### 2. Provide Default Values

```yaml
# Always provide sensible defaults
timeout: "{{ env('API_TIMEOUT', '30') | int }}"
rate_limit: "{{ env('RATE_LIMIT', '1000') | int }}"
debug_mode: "{{ env('DEBUG', 'false') | bool }}"
```

### 3. Use Comments for Complex Logic

```yaml
actions:
  # Configure servers based on deployment environment
  # Production uses HTTPS with custom domain
  # Staging uses HTTPS with staging subdomain  
  # Development uses HTTP with localhost
  {% if environment == "production" %}
  - target: "$.servers[0]"
    update:
      url: "{{ env('PROD_API_URL') }}"
  {% endif %}
```

### 4. Validate Template Variables

```yaml
# Ensure required variables are present
{% if not api_version %}
  {% set _ = error("api_version variable is required") %}
{% endif %}

# Validate environment values
{% if environment not in ["development", "staging", "production"] %}
  {% set _ = error("Invalid environment: " + environment) %}
{% endif %}
```

### 5. Keep Templates Readable

Break complex templates into smaller, focused overlays:

```yaml
# Instead of one massive template, use multiple focused overlays
overlays:
  - path: "overlays/servers.yaml"          # Server configuration
  - path: "overlays/security.yaml"        # Security settings
  - path: "overlays/database.yaml"        # Database configuration
  - path: "overlays/monitoring.yaml"      # Monitoring setup
```

## Template Testing

Test your templates with different variable combinations:

```bash
# Test with development variables
oas-patch bundle apply api.yaml my-bundle \
  --environment development \
  --variable debug_mode=true \
  --variable log_level=debug

# Test with production variables
oas-patch bundle apply api.yaml my-bundle \
  --environment production \
  --variable debug_mode=false \
  --variable log_level=error
```

## Error Handling

Common template errors and solutions:

### Undefined Variables

```yaml
# Error: Variable 'undefined_var' is undefined
# Solution: Use default filter or conditional
value: "{{ undefined_var | default('default_value') }}"

# Or check if defined
{% if undefined_var is defined %}
value: "{{ undefined_var }}"
{% endif %}
```

### Type Mismatches

```yaml
# Error: Cannot convert string to integer
# Solution: Use type conversion filters
port: "{{ port_string | int }}"
enabled: "{{ enabled_string | bool }}"
```

### Template Syntax Errors

```yaml
# Error: Unclosed template block
# Solution: Ensure all blocks are properly closed
{% if condition %}
  # content
{% endif %}  # Don't forget the endif
```

## Advanced Features

### Custom Template Functions

You can extend the template engine with custom functions (advanced usage):

```python
# Custom function example (in advanced configurations)
def current_timestamp():
    import datetime
    return datetime.datetime.now().isoformat()

template_engine.jinja_env.globals['now'] = current_timestamp
```

### Template Inheritance

Use Jinja2 template inheritance for complex overlay hierarchies:

```yaml
# base-overlay.yaml
overlay: 1.0.0
info:
  title: "Base Overlay"
actions:
  {% block base_actions %}
  - target: "$.info.version"
    update: "{{ api_version }}"
  {% endblock %}
  
  {% block environment_actions %}
  # Override in child templates
  {% endblock %}
```

## Next Steps

- Learn about [Environment Variables](environment-variables.md) in detail
- Explore [Bundle Management](bundles.md) for organizing templated overlays
