# Environment Variables

Environment variables provide dynamic configuration for your overlays and bundles, making them perfect for CI/CD pipelines and multi-environment deployments.

> **Note**: Environment variable features work with both Overlay 1.0.x and 1.1.x. Examples in this guide use 1.0.0 for simplicity, but you can use 1.1.0 to access additional features like the `copy` action.

## Overview

OAS Patcher supports environment variables through multiple mechanisms:

1. **Template Functions** - Access env vars in Jinja2 templates with `env()`
2. **Environment Namespace** - Access all env vars via `ENV.VARIABLE_NAME`
3. **Variable Substitution** - Use `${VAR_NAME}` syntax in bundle variables
4. **Conditional Logic** - Environment-based conditional content

## Template Functions

### Basic Usage

Use the `env()` function in any Jinja2 template:

```yaml
overlay: 1.0.0
info:
  title: Environment-Aware Overlay
  version: 1.0.0
actions:
  - target: "$.info"
    update:
      description: "API deployed to {{ env('ENVIRONMENT', 'development') }}"
      version: "{{ env('API_VERSION', '1.0.0') }}"
```

### Function Syntax

```jinja2
{{ env('VARIABLE_NAME') }}                    # Get variable (empty if not set)
{{ env('VARIABLE_NAME', 'default_value') }}   # Get variable with default
```

### Examples

```yaml
# Server configuration based on environment
- target: "$"
  update:
    servers:
      - url: "{{ env('API_BASE_URL', 'http://localhost:3000') }}"
        description: "{{ env('ENVIRONMENT', 'development') }} server"

# Build information
- target: "$.info"
  update:
    'x-build-info':
      timestamp: "{{ env('BUILD_TIMESTAMP') }}"
      commit: "{{ env('GIT_COMMIT', 'unknown') }}"
      pipeline: "{{ env('CI_PIPELINE_URL', '') }}"
```

## Environment Namespace

### Accessing All Environment Variables

The `ENV` namespace provides access to all environment variables:

```yaml
- target: "$.info"
  update:
    description: "Built on {{ ENV.BUILD_DATE }} by {{ ENV.CI_RUNNER_ID }}"
    'x-deployment':
      environment: "{{ ENV.DEPLOY_ENVIRONMENT }}"
      region: "{{ ENV.AWS_REGION }}"
```

### Conditional Logic

Use environment variables in conditional statements:

```yaml
- target: "$.info"
  update:
    title: "My API{% if ENV.ENVIRONMENT == 'production' %} - Production{% endif %}"
    'x-security-level': |
      {%- if ENV.ENVIRONMENT == 'production' -%}
      high
      {%- elif ENV.ENVIRONMENT == 'staging' -%}
      medium
      {%- else -%}
      low
      {%- endif -%}
```

## Variable Substitution

### ${VAR_NAME} Syntax

Use `${VAR_NAME}` syntax in bundle and overlay variables:

```yaml
# bundle.yaml
variables:
  api_url: "${API_BASE_URL:https://localhost:3000}"
  app_version: "${APP_VERSION}"
  database_url: "${DATABASE_URL:postgresql://localhost/myapp}"
  debug_mode: "${DEBUG:false}"
```

### With Default Values

Provide fallback values using colon syntax:

```yaml
variables:
  # If API_HOST is not set, use localhost
  api_host: "${API_HOST:localhost}"
  
  # If PORT is not set, use 3000
  api_port: "${PORT:3000}"
  
  # If ENVIRONMENT is not set, use development
  environment: "${ENVIRONMENT:development}"
```

### Nested Variables

Environment variables work in nested structures:

```yaml
variables:
  database:
    host: "${DB_HOST:localhost}"
    port: "${DB_PORT:5432}"
    name: "${DB_NAME:myapp}"
    ssl: "${DB_SSL:false}"
  redis:
    url: "${REDIS_URL:redis://localhost:6379}"
    timeout: "${REDIS_TIMEOUT:5000}"
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy API

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install OAS Patcher
        run: pip install oas-patch
      
      - name: Apply Production Overlay
        env:
          ENVIRONMENT: production
          API_VERSION: ${{ github.ref_name }}
          BUILD_TIMESTAMP: ${{ github.event.head_commit.timestamp }}
          GIT_COMMIT: ${{ github.sha }}
          DEPLOY_URL: https://api.production.com
        run: |
          oas-patch bundle apply production-bundle \
            --environment production \
            -o dist/production-api.yaml
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

variables:
  ENVIRONMENT: production
  API_VERSION: $CI_COMMIT_REF_NAME
  BUILD_TIMESTAMP: $CI_PIPELINE_CREATED_AT
  GIT_COMMIT: $CI_COMMIT_SHA
  CI_PIPELINE_URL: $CI_PIPELINE_URL

build_api:
  stage: build
  script:
    - pip install oas-patch
    - oas-patch bundle apply api-bundle --environment $ENVIRONMENT -o api.yaml
  artifacts:
    paths:
      - api.yaml
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        ENVIRONMENT = 'production'
        API_VERSION = "${env.BUILD_NUMBER}"
        BUILD_TIMESTAMP = "${new Date()}"
        GIT_COMMIT = "${env.GIT_COMMIT}"
    }
    
    stages {
        stage('Build API Spec') {
            steps {
                sh '''
                    pip install oas-patch
                    oas-patch bundle apply api-bundle \
                        --environment ${ENVIRONMENT} \
                        -o production-api.yaml
                '''
            }
        }
    }
}
```

## Real-World Examples

### Multi-Environment Bundle

```yaml
# bundle.yaml
name: Multi-Environment API Bundle
variables:
  app_name: "${APP_NAME:My API}"
  base_version: "${BASE_VERSION:1.0.0}"
  
overlays:
  - path: base-overlay.yaml
    environment: ["base"]
    variables:
      api_url: "${API_URL:http://localhost:3000}"
      
  - path: production-overlay.yaml
    environment: ["production"]
    variables:
      api_url: "${PROD_API_URL:https://api.production.com}"
      monitoring_enabled: "${MONITORING:true}"
      
  - path: staging-overlay.yaml
    environment: ["staging"]
    variables:
      api_url: "${STAGING_API_URL:https://staging.api.com}"
      debug_mode: "${DEBUG:true}"
```

### Production Overlay with Environment Variables

```yaml
# production-overlay.yaml
overlay: 1.0.0
info:
  title: Production Overlay
  version: 1.0.0
actions:
  - target: "$.info"
    update:
      description: "{{ app_name }} - Production Environment"
      version: "{{ env('API_VERSION', base_version) }}"
      'x-build-info':
        timestamp: "{{ ENV.BUILD_TIMESTAMP }}"
        commit: "{{ ENV.GIT_COMMIT }}"
        environment: "{{ ENV.ENVIRONMENT }}"
        pipeline_url: "{{ ENV.CI_PIPELINE_URL }}"
        
  - target: "$"
    update:
      servers:
        - url: "{{ api_url }}"
          description: "Production server"
      
  - target: "$.paths"
    update:
      /health:
        get:
          summary: Health check
          responses:
            '200':
              description: Service health
              content:
                application/json:
                  example:
                    status: "healthy"
                    environment: "{{ ENV.ENVIRONMENT }}"
                    version: "{{ ENV.API_VERSION }}"
                    build_time: "{{ ENV.BUILD_TIMESTAMP }}"
```

### Feature Flags with Environment Variables

```yaml
# feature-flags-overlay.yaml
overlay: 1.0.0
info:
  title: Feature Flags Overlay
  version: 1.0.0
actions:
  # Conditionally add new endpoints based on feature flags
  {% if env('FEATURE_ADVANCED_SEARCH', 'false') == 'true' %}
  - target: "$.paths"
    update:
      /search/advanced:
        post:
          summary: Advanced search
          description: "Advanced search functionality (Feature Flag: FEATURE_ADVANCED_SEARCH)"
          requestBody:
            content:
              application/json:
                schema:
                  type: object
          responses:
            '200':
              description: Search results
  {% endif %}
  
  # Conditionally add security based on environment
  {% if ENV.ENVIRONMENT == 'production' %}
  - target: "$.components.securitySchemes"
    update:
      OAuth2:
        type: oauth2
        flows:
          authorizationCode:
            authorizationUrl: "{{ ENV.OAUTH_AUTH_URL }}"
            tokenUrl: "{{ ENV.OAUTH_TOKEN_URL }}"
            scopes:
              read: Read access
              write: Write access
  {% endif %}
```

## Configuration Options

### Enabling/Disabling Environment Variables

```python
from oas_patch.template_engine import TemplateEngine

# Enable environment variables (default)
template_engine = TemplateEngine(enable_env_vars=True)

# Disable environment variables for security
template_engine = TemplateEngine(enable_env_vars=False)
```

### Environment Variable Validation

```yaml
# Validate required environment variables in overlays
overlay: 1.0.0
info:
  title: Validated Environment Overlay
  version: 1.0.0
actions:
  - target: "$.info"
    update:
      # This will fail if REQUIRED_VAR is not set
      required_field: "{{ env('REQUIRED_VAR') }}"
      
      # This provides a fallback
      optional_field: "{{ env('OPTIONAL_VAR', 'default') }}"
```

## Security Considerations

### Sensitive Information

⚠️ **Never expose sensitive data in API specifications:**

```yaml
# ❌ BAD: Exposes database password
- target: "$.info"
  update:
    'x-database': "{{ ENV.DATABASE_PASSWORD }}"

# ✅ GOOD: Only expose non-sensitive metadata
- target: "$.info"
  update:
    'x-environment': "{{ ENV.ENVIRONMENT }}"
    'x-version': "{{ ENV.API_VERSION }}"
```

### Environment Isolation

```yaml
# Use different variables for different environments
production_overlay.yaml:
  - target: "$.servers"
    update:
      - url: "{{ env('PROD_API_URL') }}"  # Only set in production

staging_overlay.yaml:
  - target: "$.servers"
    update:
      - url: "{{ env('STAGING_API_URL') }}"  # Only set in staging
```

## Best Practices

### 1. Use Descriptive Variable Names

```bash
# ✅ Good
export API_BASE_URL="https://api.production.com"
export DB_CONNECTION_POOL_SIZE="20"
export FEATURE_FLAG_NEW_SEARCH="true"

# ❌ Avoid
export URL="https://api.production.com"
export SIZE="20"
export FLAG="true"
```

### 2. Provide Sensible Defaults

```yaml
variables:
  # Always provide defaults for non-critical settings
  api_timeout: "${API_TIMEOUT:30000}"
  retry_attempts: "${RETRY_ATTEMPTS:3}"
  log_level: "${LOG_LEVEL:info}"
```

### 3. Document Required Variables

```yaml
# Document required environment variables
overlay: 1.0.0
info:
  title: Production Overlay
  description: |
    Required environment variables:
    - API_BASE_URL: Production API base URL
    - API_VERSION: API version for deployment
    - BUILD_TIMESTAMP: Build timestamp for tracking
    
    Optional environment variables:
    - DEBUG_MODE: Enable debug mode (default: false)
    - TIMEOUT: Request timeout in ms (default: 5000)
```

### 4. Validate in CI/CD

```bash
#!/bin/bash
# validate-env.sh - Validate required environment variables

required_vars=("API_BASE_URL" "API_VERSION" "ENVIRONMENT")

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "All required environment variables are set"
```

## Troubleshooting

### Common Issues

**Environment variable not resolving:**
```bash
# Check if variable is set
echo $MY_VAR

# Check with default
echo ${MY_VAR:-default_value}
```

**Template rendering errors:**
- Verify environment variable names are correct
- Check that defaults are provided for optional variables
- Use `oas-patch validate` to check template syntax

**Case sensitivity:**
- Environment variable names are case-sensitive
- Use consistent naming (UPPER_CASE recommended)

## Next Steps

- [**Bundle Management**](bundles.md) - Organize overlays with environment-specific configurations

---
