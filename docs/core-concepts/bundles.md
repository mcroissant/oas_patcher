# Bundle Management

Bundle management is one of the most powerful features of OAS Patcher, allowing you to organize and manage multiple overlays as cohesive units. Bundles enable complex deployment scenarios, environment-specific configurations, and streamlined overlay application workflows.

## What are Bundles?

A bundle is a collection of overlays with associated configuration that defines:

- Which overlays to apply and in what order
- Environment-specific filtering
- Variable definitions and template processing
- Metadata and documentation

Bundles solve the problem of managing multiple overlays that need to be applied together or in specific scenarios.

## Bundle Structure

A typical bundle directory structure looks like this:

```
my-bundle/
├── bundle.yaml          # Bundle configuration
├── overlays/
│   ├── base.yaml
│   ├── security.yaml
│   └── environment.yaml
```

## Bundle Configuration

The `bundle.yaml` file defines the bundle configuration:

```yaml
name: "production-api-bundle"
description: "Production environment configuration for the API"
version: "1.2.0"

# Global variables available to all overlays
variables:
  api_version: "v2"
  company_name: "Acme Corp"
  support_email: "support@acme.com"

# Overlay definitions
overlays:
  - path: "overlays/base.yaml"
    description: "Base configuration updates"
    
  - path: "overlays/security.yaml"
    description: "Security and authentication setup"
    environment: ["production", "staging"]
    
  - path: "overlays/monitoring.yaml"
    description: "Monitoring and observability"
    environment: ["production"]
    variables:
      monitoring_endpoint: "https://metrics.acme.com"
```

## Bundle Discovery and Management

OAS Patcher provides commands to work with bundles in your current directory or project:

```bash
# Create an example bundle in current directory
oas-patch bundle init

# Validate a bundle configuration
oas-patch bundle validate bundle.yaml
```

## Applying Bundles

Apply a complete bundle to an OpenAPI specification:

```bash
# Apply all overlays in a bundle
oas-patch bundle apply openapi.yaml bundle.yaml -o output.yaml

# Apply bundle for specific environment
oas-patch bundle apply openapi.yaml bundle.yaml --environment production -o output.yaml

# Apply with additional variables
oas-patch bundle apply openapi.yaml bundle.yaml \
  --variable region=us-east-1 \
  --variable instance_type=production \
  -o output.yaml
```

## Environment Filtering

Overlays can be configured to apply only in specific environments:

```yaml
overlays:
  - path: "overlays/base.yaml"
    description: "Always applied"
    
  - path: "overlays/development.yaml"
    description: "Development-only settings"
    environment: ["development", "dev"]
    
  - path: "overlays/production.yaml"
    description: "Production-only settings"
    environment: ["production", "prod"]
```

When applying a bundle, only overlays matching the specified environment will be applied:

```bash
# Only base.yaml and development.yaml will be applied
oas-patch bundle apply api.yaml bundle.yaml --environment development

# Only base.yaml and production.yaml will be applied
oas-patch bundle apply api.yaml bundle.yaml --environment production
```

## Variable Management

Bundles support hierarchical variable management:

### Global Variables

Defined at the bundle level and available to all overlays:

```yaml
variables:
  api_base_url: "https://api.example.com"
  company_name: "Example Corp"
```

### Overlay-Specific Variables

Defined for specific overlays and override global variables:

```yaml
overlays:
  - path: "overlays/environment.yaml"
    variables:
      api_base_url: "https://staging-api.example.com"  # Overrides global
      environment: "staging"                          # Overlay-specific
```

### CLI Variables

Provided at runtime and override all other variables:

```bash
oas-patch bundle apply api.yaml bundle.yaml \
  --variable api_base_url=https://custom-api.example.com \
  --variable custom_setting=true
```

## Variable Precedence

Variables are resolved in this order (highest to lowest precedence):
1. CLI variables (`--variable`)
2. Environment variables (when referenced in templates)
3. Overlay-specific variables
4. Bundle global variables


## Advanced Bundle Features

### Conditional Overlays

Use environment filtering for complex conditional logic:

```yaml
overlays:
  # Always applied
  - path: "overlays/base.yaml"
  
  # Only in cloud environments
  - path: "overlays/cloud-config.yaml"
    environment: ["aws", "azure", "gcp"]
  
  # Only for specific cloud provider
  - path: "overlays/aws-specific.yaml"
    environment: ["aws"]
```

### Template Integration

Combine bundles with template engine for dynamic content:

```yaml
overlays:
  - path: "overlays/dynamic-config.yaml"
    variables:
      database_url: "{{ env('DATABASE_URL') }}"
      api_version: "{{ api_version }}"
      deployment_time: "{{ now() }}"
```

## Bundle Organization Best Practices

### 1. Logical Grouping

Group related overlays into bundles:

- **Environment bundles**: Different configurations per environment
- **Feature bundles**: Sets of overlays that enable specific features
- **Compliance bundles**: Security and regulatory requirements

### 2. Clear Naming

Use descriptive names for bundles and overlays:

```yaml
name: "mobile-app-v2-bundle"
description: "Configuration bundle for mobile application API v2"

overlays:
  - path: "overlays/mobile-optimizations.yaml"
    description: "Mobile-specific API optimizations"
  - path: "overlays/push-notifications.yaml"
    description: "Push notification endpoint configuration"
```

### 3. Version Management

Version your bundles for better tracking:

```yaml
name: "api-security-bundle"
version: "2.1.0"
description: "Security configuration bundle - includes OAuth 2.0 and API key auth"
```

## Common Bundle Patterns

### Environment Promotion

Create bundles that transform configurations for environment promotion:

```bash
# Apply development bundle
oas-patch bundle apply base-api.yaml dev-bundle.yaml --environment development

# Apply staging bundle (with additional security)
oas-patch bundle apply base-api.yaml staging-bundle.yaml --environment staging

# Apply production bundle (with all security and monitoring)
oas-patch bundle apply base-api.yaml prod-bundle.yaml --environment production
```

### Feature Flags

Use bundles to manage feature rollouts:

```yaml
overlays:
  - path: "overlays/base-features.yaml"
  - path: "overlays/beta-features.yaml"
    environment: ["beta", "staging"]
  - path: "overlays/experimental-features.yaml"
    environment: ["experimental"]
```

### A/B Testing

Create bundles for different API variations:

```yaml
# Bundle A
name: "api-variant-a"
overlays:
  - path: "overlays/base.yaml"
  - path: "overlays/variant-a-features.yaml"

# Bundle B  
name: "api-variant-b"
overlays:
  - path: "overlays/base.yaml"
  - path: "overlays/variant-b-features.yaml"
```

## Next Steps

- Learn about [Template Engine](templates.md) integration with bundles
- Explore [Environment Variables](environment-variables.md) for dynamic configurations
