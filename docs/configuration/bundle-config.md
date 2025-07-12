# Bundle Configuration

Bundle configuration is the heart of OAS Patcher's advanced overlay management system. A well-structured bundle configuration enables organized, maintainable, and environment-specific API modifications.

## Bundle Configuration File

Every bundle requires a `bundle.yaml` file that defines the bundle's metadata, variables, and overlay configurations.

### Basic Structure

```yaml
name: "my-bundle"                    # Bundle identifier
description: "Description of bundle" # Human-readable description
version: "1.0.0"                    # Semantic version
variables:                          # Global variables (optional)
  key: "value"
overlays:                          # List of overlay configurations
  - path: "overlay1.yaml"
    description: "First overlay"
```

### Complete Example

```yaml
name: "production-api-bundle"
description: "Production environment configuration for the API"
version: "2.1.0"
author: "API Team <api-team@example.com>"
documentation: "https://docs.example.com/api-bundle"

# Global variables available to all overlays
variables:
  api_version: "v2.1"
  company_name: "Acme Corporation"
  support_email: "support@acme.com"
  base_timeout: 30
  retry_count: 3

# Overlay definitions
overlays:
  # Base configuration (always applied)
  - path: "overlays/base.yaml"
    description: "Base API configuration"
    
  # Environment-specific overlays
  - path: "overlays/development.yaml"
    description: "Development environment settings"
    environment: ["development", "dev"]
    variables:
      log_level: "debug"
      enable_debug: true
      
  - path: "overlays/staging.yaml"
    description: "Staging environment settings"
    environment: ["staging", "stage"]
    variables:
      log_level: "info"
      monitoring_enabled: true
      
  - path: "overlays/production.yaml"
    description: "Production environment settings"
    environment: ["production", "prod"]
    variables:
      log_level: "error"
      monitoring_enabled: true
      security_enabled: true
      rate_limiting: true
      
  # Feature-specific overlays
  - path: "overlays/analytics.yaml"
    description: "Analytics and tracking features"
    environment: ["staging", "production"]
    variables:
      analytics_endpoint: "https://analytics.acme.com"
      tracking_enabled: true
      
  - path: "overlays/experimental.yaml"
    description: "Experimental features"
    environment: ["development"]
    variables:
      experimental_features: true
```

## Configuration Fields

### Required Fields

#### name
- **Type**: String
- **Description**: Unique identifier for the bundle
- **Example**: `"production-api-bundle"`
- **Rules**: 
  - Must be unique within your configuration directory
  - Should use kebab-case for consistency
  - Avoid spaces and special characters

#### overlays
- **Type**: Array of overlay configurations
- **Description**: List of overlays included in the bundle
- **Minimum**: At least one overlay required

### Optional Fields

#### description
- **Type**: String
- **Description**: Human-readable description of the bundle's purpose
- **Example**: `"Production environment configuration for the API"`
- **Best Practice**: Include what the bundle does and when to use it

#### version
- **Type**: String
- **Description**: Semantic version of the bundle
- **Example**: `"2.1.0"`
- **Best Practice**: Follow semantic versioning (major.minor.patch)

#### author
- **Type**: String
- **Description**: Bundle author or team information
- **Example**: `"API Team <api-team@example.com>"`

#### documentation
- **Type**: String (URL)
- **Description**: Link to additional documentation
- **Example**: `"https://docs.example.com/api-bundle"`

#### variables
- **Type**: Object
- **Description**: Global variables available to all overlays
- **Example**:
  ```yaml
  variables:
    api_version: "v2.0"
    timeout: 30
  ```

## Overlay Configuration

Each overlay in the `overlays` array can have these properties:

### Required Fields

#### path
- **Type**: String
- **Description**: Relative path to the overlay file
- **Example**: `"overlays/security.yaml"`
- **Rules**: 
  - Path is relative to the bundle directory
  - File must exist and be a valid overlay

### Optional Fields

#### description
- **Type**: String
- **Description**: Description of what this overlay does
- **Example**: `"Adds security headers and authentication"`

#### environment
- **Type**: Array of strings
- **Description**: Environment names where this overlay applies
- **Example**: `["production", "staging"]`
- **Default**: Applied to all environments if not specified

#### variables
- **Type**: Object
- **Description**: Overlay-specific variables
- **Example**:
  ```yaml
  variables:
    log_level: "debug"
    feature_enabled: true
  ```
- **Note**: Overlay variables override global variables

## Variable Management

### Variable Precedence

Variables are resolved in this order (highest to lowest precedence):

1. **CLI variables** (`--var key=value`)
2. **Environment variables** (when referenced in templates)
3. **Overlay-specific variables**
4. **Bundle global variables**

### Variable Types

Variables can be any valid YAML type:

```yaml
variables:
  # String values
  api_version: "v2.0"
  environment: "production"
  
  # Numeric values
  timeout: 30
  port: 8080
  rate_limit: 1000
  
  # Boolean values
  debug_enabled: false
  monitoring_enabled: true
  
  # Arrays
  allowed_origins:
    - "https://app.example.com"
    - "https://admin.example.com"
    
  # Objects
  database_config:
    host: "db.example.com"
    port: 5432
    ssl_enabled: true
    
  # Complex nested structures
  service_endpoints:
    auth:
      url: "https://auth.example.com"
      timeout: 10
    payment:
      url: "https://payments.example.com"
      timeout: 30
      retry_count: 3
```

### Template Variable Usage

Variables are used in overlay templates with Jinja2 syntax:

```yaml
# In overlay file
overlay: 1.0.0
info:
  title: "{{ bundle_name }} API"
  version: "{{ api_version }}"
actions:
  - target: "$.servers[0]"
    update:
      url: "{{ base_url }}"
      description: "{{ environment | title }} server"
      
  - target: "$.info.x-config"
    update:
      timeout: {{ timeout }}
      debug: {{ debug_enabled }}
      features: {{ enabled_features | to_json }}
```

## Environment Filtering

### Basic Environment Filtering

```yaml
overlays:
  # Always applied
  - path: "base.yaml"
    
  # Only in development
  - path: "debug.yaml"
    environment: ["development"]
    
  # Multiple environments
  - path: "monitoring.yaml"
    environment: ["staging", "production"]
```

### Advanced Environment Patterns

```yaml
overlays:
  # Cloud environments
  - path: "cloud-config.yaml"
    environment: ["aws", "azure", "gcp"]
    
  # Non-production environments
  - path: "testing-features.yaml"
    environment: ["development", "staging", "qa"]
    
  # Production-like environments
  - path: "performance-config.yaml"
    environment: ["staging", "production"]
    
  # Specific environment combinations
  - path: "aws-production.yaml"
    environment: ["aws-prod", "aws-production"]
```

## Bundle Organization Patterns

### Feature-Based Organization

```yaml
# Feature bundles
overlays:
  - path: "core/base.yaml"
    description: "Core API functionality"
    
  - path: "features/authentication.yaml"
    description: "Authentication and authorization"
    
  - path: "features/analytics.yaml"
    description: "Analytics and tracking"
    
  - path: "features/notifications.yaml"
    description: "Notification system"
```

### Layer-Based Organization

```yaml
# Layered approach
overlays:
  # Infrastructure layer
  - path: "layers/infrastructure.yaml"
    description: "Basic infrastructure setup"
    
  # Security layer
  - path: "layers/security.yaml"
    description: "Security policies and configurations"
    
  # Application layer
  - path: "layers/application.yaml"
    description: "Application-specific configurations"
    
  # Environment layer
  - path: "layers/environment.yaml"
    description: "Environment-specific overrides"
```

### Service-Based Organization

```yaml
# Microservices bundles
overlays:
  - path: "services/user-service.yaml"
    description: "User management service endpoints"
    
  - path: "services/order-service.yaml"
    description: "Order processing service endpoints"
    
  - path: "services/payment-service.yaml"
    description: "Payment processing service endpoints"
    
  - path: "gateway/routing.yaml"
    description: "API gateway routing configuration"
```

## Configuration Validation

### Schema Validation

Bundle configurations are validated against this schema:

```yaml
# Bundle schema (conceptual)
type: object
required: [name, overlays]
properties:
  name:
    type: string
    pattern: "^[a-z0-9-]+$"
  description:
    type: string
  version:
    type: string
    pattern: "^\\d+\\.\\d+\\.\\d+$"
  author:
    type: string
  documentation:
    type: string
    format: uri
  variables:
    type: object
  overlays:
    type: array
    minItems: 1
    items:
      type: object
      required: [path]
      properties:
        path:
          type: string
        description:
          type: string
        environment:
          type: array
          items:
            type: string
        variables:
          type: object
```

### Validation Commands

```bash
# Validate bundle configuration
oas-patch bundle validate bundle.yaml

# Validate specific bundle file
oas-patch validate bundles/my-bundle/bundle.yaml
```

## Configuration Examples

### Simple Development Bundle

```yaml
name: "development-bundle"
description: "Development environment configuration"
version: "1.0.0"

variables:
  debug_mode: true
  log_level: "debug"

overlays:
  - path: "base.yaml"
    description: "Base development configuration"
  - path: "debug-headers.yaml"
    description: "Add debug headers"
  - path: "test-data.yaml"
    description: "Include test data examples"
```

### Multi-Environment Bundle

```yaml
name: "multi-env-bundle"
description: "Multi-environment deployment bundle"
version: "2.0.0"

variables:
  api_version: "v2"
  company: "Acme Corp"

overlays:
  - path: "base.yaml"
    description: "Base configuration for all environments"
    
  - path: "development.yaml"
    environment: ["development"]
    variables:
      server_url: "http://localhost:8080"
      debug: true
      
  - path: "staging.yaml"
    environment: ["staging"]
    variables:
      server_url: "https://staging-api.acme.com"
      monitoring: true
      
  - path: "production.yaml"
    environment: ["production"]
    variables:
      server_url: "https://api.acme.com"
      monitoring: true
      security: true
```

### Enterprise Bundle

```yaml
name: "enterprise-api-bundle"
description: "Enterprise-grade API configuration with full features"
version: "3.1.0"
author: "Platform Team <platform@enterprise.com>"
documentation: "https://docs.enterprise.com/api-platform"

variables:
  # API Configuration
  api_version: "v3.1"
  api_name: "Enterprise API Platform"
  
  # Company Information
  company_name: "Enterprise Corporation"
  support_email: "api-support@enterprise.com"
  legal_url: "https://enterprise.com/legal"
  
  # Technical Configuration
  default_timeout: 30
  max_retry_count: 3
  default_page_size: 20

overlays:
  # Core configuration
  - path: "core/metadata.yaml"
    description: "API metadata and basic information"
    
  - path: "core/servers.yaml"
    description: "Server configurations"
    
  # Security configurations
  - path: "security/authentication.yaml"
    description: "Authentication schemes"
    environment: ["staging", "production"]
    
  - path: "security/authorization.yaml"
    description: "Authorization policies"
    environment: ["staging", "production"]
    
  - path: "security/rate-limiting.yaml"
    description: "Rate limiting configuration"
    environment: ["production"]
    variables:
      rate_limit: 5000
      burst_limit: 500
      
  # Monitoring and observability
  - path: "monitoring/health-checks.yaml"
    description: "Health check endpoints"
    
  - path: "monitoring/metrics.yaml"
    description: "Metrics and monitoring configuration"
    environment: ["staging", "production"]
    
  - path: "monitoring/logging.yaml"
    description: "Logging configuration"
    variables:
      log_retention_days: 90
      
  # Environment-specific configurations
  - path: "environments/development.yaml"
    description: "Development environment specifics"
    environment: ["development"]
    variables:
      log_level: "debug"
      mock_external_services: true
      
  - path: "environments/staging.yaml"
    description: "Staging environment specifics"
    environment: ["staging"]
    variables:
      log_level: "info"
      external_service_timeout: 10
      
  - path: "environments/production.yaml"
    description: "Production environment specifics"
    environment: ["production"]
    variables:
      log_level: "warn"
      external_service_timeout: 5
      performance_monitoring: true
```

## Best Practices

### 1. Bundle Naming

```yaml
# Good: Descriptive, kebab-case
name: "mobile-app-v2-bundle"
name: "security-compliance-bundle"
name: "microservices-gateway-bundle"

# Avoid: Generic or unclear names
name: "bundle1"
name: "my_bundle"
name: "api bundle"
```

### 2. Version Management

```yaml
# Use semantic versioning
version: "1.0.0"    # Initial release
version: "1.1.0"    # New features added
version: "1.1.1"    # Bug fixes
version: "2.0.0"    # Breaking changes
```

### 3. Variable Organization

```yaml
# Group related variables
variables:
  # API Information
  api_name: "My API"
  api_version: "v2"
  
  # Server Configuration
  server_timeout: 30
  server_retry_count: 3
  
  # Feature Flags
  analytics_enabled: true
  new_features_enabled: false
```

### 4. Environment Strategy

```yaml
# Clear environment names
environment: ["development", "staging", "production"]

# Avoid ambiguous names
environment: ["dev", "test", "prod", "live"]
```

### 5. Documentation

```yaml
# Always include descriptions
description: "Comprehensive description of what this bundle does, when to use it, and any special considerations"

# Document each overlay
overlays:
  - path: "security.yaml"
    description: "Adds OAuth 2.0 authentication, API key support, and security headers"
```

## Next Steps

- [Overlay Configuration](overlay-config.md) - Detailed overlay file configuration
- [Environment Configuration](environment-config.md) - Environment management
- [Multi-Environment Tutorial](../tutorials/multi-environment.md) - Hands-on bundle examples
