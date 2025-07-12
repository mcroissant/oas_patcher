# Multi-Environment Setup

Managing APIs across different environments (development, staging, production) is a common challenge. This tutorial shows you how to use OAS Patcher's bundle management and environment filtering to create a robust multi-environment deployment strategy.

## Prerequisites

- Completed the [Basic Overlay Application](basic-overlay.md) tutorial
- Understanding of [Bundle Management](../core-concepts/bundles.md) concepts
- Familiarity with different deployment environments

## Tutorial Overview

In this tutorial, we'll:
1. Design a multi-environment strategy
2. Create environment-specific overlays
3. Set up bundle configuration
4. Implement environment-specific variables
5. Deploy to different environments
6. Handle environment promotion workflows

## Step 1: Design Your Environment Strategy

Let's start by defining our environments and their characteristics:

| Environment | Purpose | URL | Features |
|-------------|---------|-----|----------|
| Development | Local testing | http://localhost:8080 | Debug headers, verbose logging, test data |
| Staging | Pre-production testing | https://staging-api.example.com | Production-like, monitoring, limited test data |
| Production | Live environment | https://api.example.com | Full security, monitoring, rate limiting |

Create a directory structure for our multi-environment setup:

```
multi-env-bundle/
├── bundle.yaml
├── overlays/
│   ├── base.yaml
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── README.md
```

## Step 2: Create the Base Configuration

Start with a base overlay that applies to all environments. Create `overlays/base.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Base Configuration
  version: 1.0.0
  description: Common configuration applied to all environments
actions:
  # Update API version
  - target: "$.info.version"
    update: "{{ api_version }}"
    
  # Add contact information
  - target: "$.info.contact"
    update:
      name: "API Team"
      email: "api-team@example.com"
      url: "https://example.com/api-docs"
      
  # Add standard tags
  - target: "$.tags"
    update:
      - name: "users"
        description: "User management operations"
      - name: "orders"
        description: "Order processing operations"
      - name: "products"
        description: "Product catalog operations"
        
  # Add basic error responses
  - target: "$.components.responses"
    update:
      UnauthorizedError:
        description: "Authentication information is missing or invalid"
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unauthorized"
                message:
                  type: string
                  example: "Valid authentication credentials required"
      NotFoundError:
        description: "The requested resource was not found"
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Not Found"
                message:
                  type: string
                  example: "The requested resource does not exist"
```

## Step 3: Create Environment-Specific Overlays

### Development Environment

Create `overlays/development.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Development Environment Configuration
  version: 1.0.0
  description: Development-specific settings with debugging and test data
actions:
  # Set development server
  - target: "$.servers"
    update:
      - url: "{{ dev_server_url }}"
        description: "Development server"
        
  # Add debug information to info
  - target: "$.info.x-debug"
    update:
      enabled: true
      log_level: "debug"
      show_sql: true
      
  # Add test endpoints (only in development)
  - target: "$.paths./debug/health"
    update:
      get:
        summary: "Health check endpoint"
        description: "Returns system health information (development only)"
        tags: ["debug"]
        responses:
          '200':
            description: "System health information"
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      example: "healthy"
                    timestamp:
                      type: string
                      format: date-time
                    database:
                      type: string
                      example: "connected"
                      
  # Add example data for testing
  - target: "$.components.examples"
    update:
      TestUser:
        summary: "Test user for development"
        value:
          id: 999
          username: "testuser"
          email: "test@example.com"
          role: "admin"
      TestOrder:
        summary: "Test order for development"
        value:
          id: 999
          user_id: 999
          status: "pending"
          total: 99.99
          
  # Disable rate limiting in development
  - target: "$.info.x-rate-limiting"
    update:
      enabled: false
```

### Staging Environment

Create `overlays/staging.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Staging Environment Configuration
  version: 1.0.0
  description: Staging environment with production-like settings and monitoring
actions:
  # Set staging server
  - target: "$.servers"
    update:
      - url: "{{ staging_server_url }}"
        description: "Staging server"
        
  # Add staging-specific info
  - target: "$.info.x-environment"
    update:
      name: "staging"
      purpose: "Pre-production testing"
      data_retention: "30 days"
      
  # Add basic authentication
  - target: "$.components.securitySchemes"
    update:
      ApiKeyAuth:
        type: apiKey
        in: header
        name: X-API-Key
        description: "API key for staging environment"
        
  # Require authentication for all operations
  - target: "$.security"
    update:
      - ApiKeyAuth: []
      
  # Add monitoring and observability
  - target: "$.info.x-monitoring"
    update:
      enabled: true
      metrics_endpoint: "{{ monitoring_endpoint }}"
      health_check: "/health"
      
  # Enable moderate rate limiting
  - target: "$.info.x-rate-limiting"
    update:
      enabled: true
      requests_per_minute: 1000
      burst_limit: 100
      
  # Add staging-specific headers
  - target: "$.components.headers"
    update:
      X-Environment:
        description: "Environment identifier"
        schema:
          type: string
          example: "staging"
      X-Request-ID:
        description: "Unique request identifier for tracing"
        schema:
          type: string
          format: uuid
```

### Production Environment

Create `overlays/production.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Production Environment Configuration
  version: 1.0.0
  description: Production environment with full security and monitoring
actions:
  # Set production server
  - target: "$.servers"
    update:
      - url: "{{ prod_server_url }}"
        description: "Production server"
        
  # Add production environment info
  - target: "$.info.x-environment"
    update:
      name: "production"
      purpose: "Live production environment"
      sla: "99.9% uptime"
      support: "24/7"
      
  # Add comprehensive security
  - target: "$.components.securitySchemes"
    update:
      BearerAuth:
        type: http
        scheme: bearer
        bearerFormat: JWT
        description: "JWT Bearer token authentication"
      ApiKeyAuth:
        type: apiKey
        in: header
        name: X-API-Key
        description: "API key authentication"
        
  # Require authentication
  - target: "$.security"
    update:
      - BearerAuth: []
      - ApiKeyAuth: []
      
  # Add comprehensive monitoring
  - target: "$.info.x-monitoring"
    update:
      enabled: true
      metrics_endpoint: "{{ prod_monitoring_endpoint }}"
      health_check: "/health"
      alerting: true
      log_level: "info"
      
  # Enable strict rate limiting
  - target: "$.info.x-rate-limiting"
    update:
      enabled: true
      requests_per_minute: 500
      burst_limit: 50
      authenticated_limit: 2000
      
  # Add production headers and metadata
  - target: "$.components.headers"
    update:
      X-Environment:
        description: "Environment identifier"
        schema:
          type: string
          example: "production"
      X-Request-ID:
        description: "Unique request identifier for tracing"
        schema:
          type: string
          format: uuid
      X-Rate-Limit-Remaining:
        description: "Number of requests remaining in current window"
        schema:
          type: integer
      X-Rate-Limit-Reset:
        description: "Time when rate limit window resets"
        schema:
          type: string
          format: date-time
          
  # Add legal and compliance information
  - target: "$.info.termsOfService"
    update: "https://example.com/terms"
    
  - target: "$.info.license"
    update:
      name: "Proprietary"
      url: "https://example.com/license"
      
  # Add production-specific schemas
  - target: "$.components.schemas.ErrorResponse"
    update:
      type: object
      required: ["error", "message", "timestamp", "request_id"]
      properties:
        error:
          type: string
          description: "Error code"
        message:
          type: string
          description: "Human-readable error message"
        timestamp:
          type: string
          format: date-time
          description: "Error timestamp"
        request_id:
          type: string
          format: uuid
          description: "Request ID for support tracking"
```

## Step 4: Configure the Bundle

Create the bundle configuration in `bundle.yaml`:

```yaml
name: "multi-environment-api"
description: "Multi-environment API configuration bundle"
version: "2.0.0"

# Global variables available to all overlays
variables:
  api_version: "2.0.0"
  company_name: "Example Corp"
  api_team_email: "api-team@example.com"

overlays:
  # Base configuration (always applied)
  - path: "overlays/base.yaml"
    description: "Base configuration for all environments"
    
  # Environment-specific configurations
  - path: "overlays/development.yaml"
    description: "Development environment settings"
    environment: ["development", "dev", "local"]
    variables:
      dev_server_url: "http://localhost:8080"
      log_level: "debug"
      
  - path: "overlays/staging.yaml"
    description: "Staging environment settings"
    environment: ["staging", "stage", "test"]
    variables:
      staging_server_url: "https://staging-api.example.com"
      monitoring_endpoint: "https://staging-monitoring.example.com"
      
  - path: "overlays/production.yaml"
    description: "Production environment settings"
    environment: ["production", "prod", "live"]
    variables:
      prod_server_url: "https://api.example.com"
      prod_monitoring_endpoint: "https://monitoring.example.com"
```

## Step 5: Deploy to Different Environments

### Deploy to Development

```bash
# Apply development configuration
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment development \
  -o api-development.yaml

# Or with additional variables
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment development \
  --variable dev_server_url=http://localhost:3000 \
  --variable debug_mode=true \
  -o api-development.yaml
```

### Deploy to Staging

```bash
# Apply staging configuration
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment staging \
  -o api-staging.yaml

# With staging-specific variables
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment staging \
  --variable api_key_required=true \
  --variable test_data_enabled=false \
  -o api-staging.yaml
```

### Deploy to Production

```bash
# Apply production configuration
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment production \
  -o api-production.yaml

# With production variables (often from environment variables)
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment production \
  --variable prod_server_url="$PROD_API_URL" \
  --variable monitoring_enabled=true \
  -o api-production.yaml
```

## Step 6: Environment Promotion Workflows

### Automated Promotion Script

Create a script to handle environment promotions:

```bash
#!/bin/bash
# promote-api.sh

set -e

SOURCE_ENV=${1:-staging}
TARGET_ENV=${2:-production}
API_FILE=${3:-base-api.yaml}
BUNDLE_NAME=${4:-multi-environment-api}

echo "Promoting API from $SOURCE_ENV to $TARGET_ENV..."

# Generate target environment configuration
oas-patch bundle apply "$API_FILE" "$BUNDLE_NAME" \
  --environment "$TARGET_ENV" \
  -o "api-$TARGET_ENV.yaml"

echo "API configuration generated for $TARGET_ENV environment"

# Validate the generated configuration
if command -v swagger-codegen &> /dev/null; then
    swagger-codegen validate -i "api-$TARGET_ENV.yaml"
    echo "✓ API configuration validated"
fi

# Optional: Deploy to target environment
if [[ "$TARGET_ENV" == "production" ]]; then
    echo "🚀 Ready for production deployment!"
    echo "Review api-production.yaml before deploying"
else
    echo "✓ Configuration ready for $TARGET_ENV"
fi
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
# .github/workflows/api-deployment.yml
name: API Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  generate-api-configs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [development, staging, production]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Install OAS Patcher
      run: pip install oas-patch
      
    - name: Generate API configuration for ${{ matrix.environment }}
      run: |
        oas-patch bundle apply base-api.yaml multi-environment-api \
          --environment ${{ matrix.environment }} \
          -o api-${{ matrix.environment }}.yaml
          
    - name: Validate API configuration
      run: |
        oas-patch validate api-${{ matrix.environment }}.yaml
        
    - name: Upload API configuration
      uses: actions/upload-artifact@v3
      with:
        name: api-${{ matrix.environment }}
        path: api-${{ matrix.environment }}.yaml
```

## Step 7: Advanced Environment Management

### Environment-Specific Variables with Templates

Create an overlay that uses environment variables:

```yaml
# overlays/dynamic-config.yaml
overlay: 1.0.0
info:
  title: Dynamic Configuration
  version: 1.0.0
actions:
  - target: "$.info.x-deployment"
    update:
      timestamp: "{{ env('DEPLOYMENT_TIMESTAMP', now()) }}"
      version: "{{ env('BUILD_VERSION', api_version) }}"
      commit: "{{ env('GIT_COMMIT', 'unknown') }}"
      environment: "{{ environment }}"
      
  - target: "$.servers[0].url"
    update: "{{ env('API_BASE_URL') }}"
    
  - target: "$.components.securitySchemes.OAuth2.flows.authorizationCode"
    update:
      authorizationUrl: "{{ env('OAUTH_AUTH_URL') }}"
      tokenUrl: "{{ env('OAUTH_TOKEN_URL') }}"
```

### Conditional Feature Flags

Use environment filtering for feature flags:

```yaml
# Add to bundle.yaml
overlays:
  - path: "overlays/base.yaml"
    description: "Base configuration"
    
  - path: "overlays/feature-new-api.yaml"
    description: "New API endpoints (feature flag)"
    environment: ["development", "staging"]  # Not in production yet
    
  - path: "overlays/feature-beta.yaml"
    description: "Beta features"
    environment: ["development"]  # Only in dev
    
  - path: "overlays/legacy-support.yaml"
    description: "Legacy API support"
    environment: ["production"]  # Only keep in production
```

### Environment-Specific Testing

Create test configurations for each environment:

```bash
# Test development configuration
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment development \
  --variable enable_debug=true \
  | oas-patch validate -

# Test staging configuration  
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment staging \
  --variable api_key_required=true \
  | oas-patch validate -

# Test production configuration
oas-patch bundle apply base-api.yaml multi-environment-api \
  --environment production \
  --variable security_enabled=true \
  | oas-patch validate -
```

## Step 8: Monitoring and Observability

### Environment-Specific Monitoring

Add monitoring overlays for each environment:

```yaml
# overlays/monitoring-development.yaml
overlay: 1.0.0
info:
  title: Development Monitoring
actions:
  - target: "$.info.x-monitoring"
    update:
      enabled: true
      debug_mode: true
      log_requests: true
      log_responses: true

# overlays/monitoring-production.yaml  
overlay: 1.0.0
info:
  title: Production Monitoring
actions:
  - target: "$.info.x-monitoring"
    update:
      enabled: true
      metrics_collection: true
      error_tracking: true
      performance_monitoring: true
      alert_thresholds:
        error_rate: 0.01
        response_time_p95: 500
```

## Best Practices for Multi-Environment Setup

### 1. Environment Naming Consistency

Use consistent environment names across all your tooling:

```yaml
# Good - consistent naming
environment: ["development", "staging", "production"]

# Avoid - inconsistent aliases
environment: ["dev", "stage", "prod", "live", "test"]
```

### 2. Variable Management

Keep environment-specific variables organized:

```yaml
# In bundle.yaml - organize by environment
overlays:
  - path: "overlays/development.yaml"
    environment: ["development"]
    variables:
      debug_mode: true
      log_level: "debug"
      test_data: true
      
  - path: "overlays/production.yaml"
    environment: ["production"]
    variables:
      debug_mode: false
      log_level: "error"
      security_enabled: true
```

### 3. Security Considerations

Gradually increase security from development to production:

```yaml
# Development - minimal security for easy testing
# Staging - production-like security for integration testing  
# Production - full security with all safeguards
```

### 4. Documentation

Document your environment strategy:

```markdown
# Environment Strategy

## Development
- Purpose: Local development and unit testing
- Data: Test data, can be reset anytime
- Security: Minimal for ease of development
- Monitoring: Debug logging enabled

## Staging  
- Purpose: Integration testing and QA
- Data: Production-like test data
- Security: Production equivalent
- Monitoring: Full monitoring for testing

## Production
- Purpose: Live customer-facing environment
- Data: Real customer data
- Security: Maximum security
- Monitoring: Full monitoring and alerting
```

## Next Steps

Now that you have a multi-environment setup:

1. Learn about [CI/CD Integration](cicd-integration.md) for automated deployments
2. Explore [Advanced Templating](advanced-templating.md) for dynamic configurations
3. Set up monitoring and alerting for your environments

## Summary

In this tutorial, you learned how to:
- Design a multi-environment strategy
- Create environment-specific overlays
- Use bundle configuration for environment management
- Deploy to different environments with different configurations
- Implement environment promotion workflows
- Use advanced features like feature flags and conditional overlays

Multi-environment management with OAS Patcher provides a robust foundation for API deployment across different stages of your development lifecycle.
