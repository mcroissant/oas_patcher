# Environment Configuration

This guide covers how to configure and use environment variables with OAS Patcher for dynamic overlay processing and multi-environment deployments.

## Overview

OAS Patcher supports environment variables for:
- Template substitution in overlays
- Dynamic configuration based on deployment environments
- Conditional processing and filtering
- Runtime parameter injection

## Environment Variable Sources

### 1. System Environment Variables

Variables set in your operating system environment:

```bash
# Linux/macOS
export API_BASE_URL="https://api.example.com"
export API_VERSION="v2"

# Windows Command Prompt
set API_BASE_URL=https://api.example.com
set API_VERSION=v2

# Windows PowerShell
$env:API_BASE_URL = "https://api.example.com"
$env:API_VERSION = "v2"
```

### 2. .env Files

Create `.env` files for environment-specific configurations:

```bash
# .env.development
API_BASE_URL=https://dev-api.example.com
API_VERSION=v1
DEBUG_MODE=true
CONTACT_EMAIL=dev@example.com

# .env.staging
API_BASE_URL=https://staging-api.example.com
API_VERSION=v2
DEBUG_MODE=false
CONTACT_EMAIL=staging@example.com

# .env.production
API_BASE_URL=https://api.example.com
API_VERSION=v2
DEBUG_MODE=false
CONTACT_EMAIL=support@example.com
```

### 3. Command Line Variables

Pass variables directly via CLI:

```bash
# Set variables for a single command
oas-patcher apply \
  --input openapi.yaml \
  --overlay overlay.yaml \
  --env API_BASE_URL=https://custom-api.com \
  --env API_VERSION=v3 \
  --output result.yaml
```

### 4. Bundle Configuration

Define variables in bundle configuration files:

```yaml
# bundle.yml
name: "My API Bundle"
version: "1.0.0"
environments:
  development:
    variables:
      API_BASE_URL: "https://dev-api.example.com"
      API_VERSION: "v1"
      DEBUG_MODE: "true"
  production:
    variables:
      API_BASE_URL: "https://api.example.com"
      API_VERSION: "v2"
      DEBUG_MODE: "false"
```

## Variable Precedence

Variables are resolved in this order (highest to lowest priority):

1. Command line variables (`--env`)
2. Environment-specific `.env` files
3. General `.env` file
4. Bundle configuration variables
5. System environment variables

## Template Syntax

### Basic Substitution

Use Jinja2 template syntax for variable substitution:

```yaml
# overlay.yaml
overlay: 1.0.0
info:
  title: "My API Overlay"
  version: 1.0.0
actions:
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}"
    description: "Set server URL from environment"
  
  - target: "$.info.version"
    update: "{{ API_VERSION }}"
    description: "Set API version"
  
  - target: "$.info.contact.email"
    update: "{{ CONTACT_EMAIL }}"
    description: "Set contact email"
```

### Default Values

Provide fallback values for missing variables:

```yaml
actions:
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL | default('https://localhost:8080') }}"
  
  - target: "$.info.description"
    update: "{{ API_DESCRIPTION | default('API Documentation') }}"
  
  - target: "$.paths./health.get.responses.200.description"
    update: "{{ HEALTH_RESPONSE | default('Service is running') }}"
```

### Conditional Logic

Use Jinja2 conditionals for environment-specific behavior:

```yaml
actions:
  # Add debug info only in development
  - target: "$.info.x-debug"
    update: "{% if DEBUG_MODE == 'true' %}{{ {'enabled': true, 'level': 'verbose'} }}{% else %}{{ {'enabled': false} }}{% endif %}"
  
  # Different security schemes per environment
  - target: "$.components.securitySchemes.auth"
    update: |
      {% if ENVIRONMENT == 'development' %}
      type: "http"
      scheme: "basic"
      {% else %}
      type: "oauth2"
      flows:
        authorizationCode:
          authorizationUrl: "{{ OAUTH_AUTH_URL }}"
          tokenUrl: "{{ OAUTH_TOKEN_URL }}"
      {% endif %}
```

### Complex Objects

Build complex objects using templates:

```yaml
actions:
  - target: "$.info.contact"
    update:
      name: "{{ CONTACT_NAME | default('API Support') }}"
      email: "{{ CONTACT_EMAIL }}"
      url: "{{ CONTACT_URL | default('https://example.com/support') }}"
  
  - target: "$.servers"
    update:
      - url: "{{ API_BASE_URL }}"
        description: "{{ SERVER_DESCRIPTION | default('Main API server') }}"
      {% if FALLBACK_URL %}
      - url: "{{ FALLBACK_URL }}"
        description: "Fallback server"
      {% endif %}
```

## Environment Filtering

### Environment-Specific Overlays

Organize overlays by environment:

```
overlays/
├── common/
│   ├── security.yaml
│   └── formatting.yaml
├── development/
│   ├── debug.yaml
│   └── cors.yaml
├── staging/
│   ├── monitoring.yaml
│   └── rate-limiting.yaml
└── production/
    ├── caching.yaml
    └── security-enhanced.yaml
```

### Bundle Environment Filtering

Use bundle configuration to apply environment-specific overlays:

```yaml
# bundle.yml
name: "API Bundle"
version: "1.0.0"

overlays:
  # Always applied
  - path: "overlays/common/security.yaml"
  - path: "overlays/common/formatting.yaml"
  
  # Environment-specific
  - path: "overlays/development/debug.yaml"
    environments: ["development"]
  
  - path: "overlays/staging/monitoring.yaml"
    environments: ["staging"]
  
  - path: "overlays/production/caching.yaml"
    environments: ["production"]

environments:
  development:
    variables:
      API_BASE_URL: "https://dev-api.example.com"
      DEBUG_MODE: "true"
  
  staging:
    variables:
      API_BASE_URL: "https://staging-api.example.com"
      DEBUG_MODE: "false"
  
  production:
    variables:
      API_BASE_URL: "https://api.example.com"
      DEBUG_MODE: "false"
```

## Advanced Patterns

### Dynamic Schema Generation

Generate schemas based on environment:

```yaml
actions:
  - target: "$.components.schemas.Config"
    update:
      type: "object"
      properties:
        environment:
          type: "string"
          enum: ["{{ ENVIRONMENT }}"]
        debug:
          type: "boolean"
          default: {{ DEBUG_MODE | lower }}
        features:
          type: "object"
          properties:
            {% for feature in ENABLED_FEATURES.split(',') %}
            {{ feature.strip() }}:
              type: "boolean"
              default: true
            {% endfor %}
```

### Version-Specific Configuration

Handle API versioning with environment variables:

```yaml
actions:
  - target: "$.info.version"
    update: "{{ API_VERSION }}"
  
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}/{% if API_VERSION.startswith('v') %}{{ API_VERSION }}{% else %}v{{ API_VERSION }}{% endif %}"
  
  # Add version-specific endpoints
  {% if API_VERSION == 'v2' %}
  - target: "$.paths./v2/advanced-feature"
    update:
      get:
        summary: "Advanced feature (v2 only)"
        responses:
          "200":
            description: "Success"
  {% endif %}
```

### Multi-Region Configuration

Configure for different geographical regions:

```yaml
# .env.us-east
REGION=us-east-1
API_BASE_URL=https://us-api.example.com
CDN_URL=https://us-cdn.example.com

# .env.eu-west
REGION=eu-west-1
API_BASE_URL=https://eu-api.example.com
CDN_URL=https://eu-cdn.example.com
```

```yaml
# overlay.yaml
actions:
  - target: "$.servers"
    update:
      - url: "{{ API_BASE_URL }}"
        description: "{{ REGION | title }} API Server"
  
  - target: "$.info.x-region"
    update: "{{ REGION }}"
  
  - target: "$.paths./assets.get.responses.200.headers.Location.example"
    update: "{{ CDN_URL }}/path/to/asset"
```

## Best Practices

### Variable Naming

```bash
# Use descriptive, consistent naming
API_BASE_URL=https://api.example.com
API_VERSION=v2
API_TIMEOUT=30

# Group related variables with prefixes
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp

# Use UPPER_CASE for environment variables
OAUTH_CLIENT_ID=abc123
OAUTH_CLIENT_SECRET=secret456
```

### Security Considerations

```bash
# ❌ Don't commit secrets to version control
echo "SECRET_KEY=abc123" >> .env

# ✅ Use separate files for secrets
echo "SECRET_KEY=abc123" >> .env.local
echo ".env.local" >> .gitignore

# ✅ Use environment-specific secret management
# Production: Use proper secret management systems
# Development: Use .env.local files
```

### Documentation

```yaml
# bundle.yml - Document required variables
name: "API Bundle"
version: "1.0.0"

# Required environment variables:
# - API_BASE_URL: Base URL for the API server
# - API_VERSION: API version (e.g., v1, v2)
# - CONTACT_EMAIL: Support contact email
# - DEBUG_MODE: Enable debug features (true/false)

environments:
  development:
    # Development environment uses local services
    variables:
      API_BASE_URL: "http://localhost:8080"
      DEBUG_MODE: "true"
```

### Testing

```bash
# Test with different environment configurations
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment development \
  --output dev-openapi.yaml

oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment production \
  --output prod-openapi.yaml

# Validate the outputs
oas-patcher validate dev-openapi.yaml
oas-patcher validate prod-openapi.yaml
```

## Troubleshooting

### Common Issues

1. **Undefined Variable Error**
   ```
   Error: Variable 'API_BASE_URL' is not defined
   ```
   - Check variable name spelling
   - Ensure variable is set in the environment
   - Use default values in templates

2. **Template Syntax Error**
   ```
   Error: Invalid Jinja2 syntax
   ```
   - Validate template syntax
   - Check for proper quoting in YAML
   - Use YAML literal blocks for complex templates

3. **Environment Not Found**
   ```
   Error: Environment 'staging' not found in bundle
   ```
   - Check environment name in bundle configuration
   - Ensure environment is properly defined
   - Use `oas-patch bundle validate bundle.yaml` to check bundle configuration

### Debugging Tips

```bash
# Validate bundle configuration (shows environment info)
oas-patch bundle validate bundle.yaml

# Test bundle application with verbose output
oas-patch bundle apply api.yaml bundle-name \
  --env development \
  --verbose \
  --dry-run

# Dry run to see template resolution
oas-patcher apply \
  --input openapi.yaml \
  --overlay overlay.yaml \
  --dry-run \
  --verbose
```

### Environment Variable Validation

Create validation scripts:

```bash
#!/bin/bash
# validate-env.sh

required_vars=(
  "API_BASE_URL"
  "API_VERSION"
  "CONTACT_EMAIL"
)

for var in "${required_vars[@]}"; do
  if [[ -z "${!var}" ]]; then
    echo "Error: Required variable $var is not set"
    exit 1
  fi
done

echo "All required environment variables are set"
```

## Integration Examples

### Docker

```dockerfile
# Dockerfile
FROM alpine:latest

# Set default environment variables
ENV API_BASE_URL=https://api.example.com
ENV API_VERSION=v1
ENV DEBUG_MODE=false

# Copy and process specifications
COPY . /app
WORKDIR /app

RUN oas-patcher bundle apply \
    --bundle bundle.yml \
    --environment production \
    --output openapi.yaml
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy API Specs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [development, staging, production]
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup environment variables
        run: |
          case "${{ matrix.environment }}" in
            development)
              echo "API_BASE_URL=https://dev-api.example.com" >> $GITHUB_ENV
              echo "DEBUG_MODE=true" >> $GITHUB_ENV
              ;;
            staging)
              echo "API_BASE_URL=https://staging-api.example.com" >> $GITHUB_ENV
              echo "DEBUG_MODE=false" >> $GITHUB_ENV
              ;;
            production)
              echo "API_BASE_URL=https://api.example.com" >> $GITHUB_ENV
              echo "DEBUG_MODE=false" >> $GITHUB_ENV
              ;;
          esac
      
      - name: Generate OpenAPI specification
        run: |
          oas-patcher bundle apply \
            --bundle bundle.yml \
            --environment ${{ matrix.environment }} \
            --output openapi-${{ matrix.environment }}.yaml
      
      - name: Deploy specification
        run: |
          # Deploy to appropriate environment
          echo "Deploying to ${{ matrix.environment }}"
```
