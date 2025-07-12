# Bundle Commands

Bundle commands provide advanced overlay management capabilities, including environment-specific configurations, template processing, and organized overlay collections. These commands require enhanced dependencies.

## Prerequisites

Bundle commands require enhanced features:

```bash
pip install oas-patch[enhanced]
# or
pip install Jinja2 rich click
```

## apply

Apply overlay bundle to OpenAPI document with environment support and template processing.

### Syntax

```bash
oas-patch apply OPENAPI_FILE BUNDLE_NAME [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `OPENAPI_FILE` | Path to the OpenAPI document (YAML/JSON) |
| `BUNDLE_NAME` | Name of the overlay bundle to apply |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path (auto-generated if not specified) |
| `--env` | `-e` | Environment name to use for filtering overlays |
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--format` | `-f` | Output format: `yaml` or `json` |
| `--var` |  | Variables in key=value format (repeatable) |
| `--dry-run` |  | Preview changes without saving |
| `--verbose` | `-v` | Verbose output with progress indicators |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Bundle Application

```bash
# Apply all overlays in bundle
oas-patch apply api.yaml my-bundle -o output.yaml

# Apply with auto-generated output filename
oas-patch apply api.yaml production-bundle
# Creates: api-production-bundle.yaml
```

#### Environment-Specific Application

```bash
# Apply only development overlays
oas-patch apply api.yaml app-bundle --env development -o api-dev.yaml

# Apply production overlays
oas-patch apply api.yaml app-bundle --env production -o api-prod.yaml

# Apply staging with verbose output
oas-patch apply api.yaml app-bundle --env staging --verbose
```

#### Variable Substitution

```bash
# Pass variables to templates
oas-patch apply api.yaml app-bundle \
  --var api_version=v2.1 \
  --var base_url=https://api.example.com \
  -o api-configured.yaml

# Multiple variables for environment
oas-patch apply api.yaml deploy-bundle \
  --env production \
  --var region=us-east-1 \
  --var instance_type=production \
  --var monitoring_enabled=true
```

#### Dry Run and Testing

```bash
# Preview changes without saving
oas-patch apply api.yaml test-bundle --env development --dry-run

# Test with variables
oas-patch apply api.yaml config-bundle \
  --var debug_mode=true \
  --var log_level=debug \
  --dry-run
```

#### Advanced Configuration

```bash
# Custom configuration directory
oas-patch apply api.yaml my-bundle \
  --config ./custom-overlays \
  --env production

# Force JSON output format
oas-patch apply api.yaml my-bundle \
  --format json \
  -o api-bundle.json

# Verbose mode with progress tracking
oas-patch apply api.yaml large-bundle \
  --env production \
  --verbose \
  -o production-api.yaml
```

### Output Behavior

#### Auto-Generated Filenames

When `--output` is not specified, filenames are generated as:
- Pattern: `{input_stem}-{bundle_name}.{extension}`
- Example: `petstore.yaml` + `production-bundle` = `petstore-production-bundle.yaml`

#### Format Detection

Output format is determined by:
1. `--format` option (highest priority)
2. Input file extension
3. Default to YAML

### Return Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (bundle not found, overlay errors, etc.) |
| 130 | Interrupted by user (Ctrl+C) |

## list-bundles

List all available overlay bundles in the configuration directory.

### Syntax

```bash
oas-patch list-bundles [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--verbose` | `-v` | Show detailed information |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Listing

```bash
# List all bundles
oas-patch list-bundles

# Output:
# Available Bundles
#   development-bundle
#   production-bundle
#   security-bundle
```

#### Detailed Information

```bash
# Show detailed bundle information
oas-patch list-bundles --verbose
```

Example verbose output:
```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Bundle Name        ┃ Description                     ┃ Overlays  ┃ Status     ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ development-bundle │ Development environment config  │ 3         │ ✓ Valid    │
│ production-bundle  │ Production environment config   │ 5         │ ✓ Valid    │
│ security-bundle    │ Security enhancements          │ 2         │ ✓ Valid    │
└────────────────────┴─────────────────────────────────┴───────────┴────────────┘
```

#### Custom Configuration Directory

```bash
# List bundles from custom directory
oas-patch list-bundles --config ./my-overlays

# Verbose listing with custom config
oas-patch list-bundles --config ./project-configs --verbose
```

### Bundle Discovery

The command discovers bundles by scanning for `bundle.yaml` files:

```
overlays/
├── app-bundle/
│   └── bundle.yaml     # Found: "app-bundle"
├── security-bundle/
│   └── bundle.yaml     # Found: "security-bundle"
└── legacy/
    └── old-config.yaml # Ignored: not named "bundle.yaml"
```

## list-environments

List all available environment configurations.

### Syntax

```bash
oas-patch list-environments [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--verbose` | `-v` | Show detailed information |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Listing

```bash
# List all environments
oas-patch list-environments

# Output:
# Available Environments
#   development
#   staging
#   production
```

#### Detailed Information

```bash
# Show environment details
oas-patch list-environments --verbose
```

Example verbose output:
```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Environment   ┃ Description                          ┃ Variables ┃ Status     ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ development   │ Development environment config       │ 5         │ ✓ Valid    │
│ staging       │ Staging environment for testing      │ 7         │ ✓ Valid    │
│ production    │ Production environment               │ 8         │ ✓ Valid    │
└───────────────┴──────────────────────────────────────┴───────────┴────────────┘
```

### Environment Discovery

Environments are discovered from:
- `environments/` directory with `.yaml` files
- Environment-specific subdirectories
- Bundle-embedded environment configurations

## info

Show detailed information about a specific bundle.

### Syntax

```bash
oas-patch info BUNDLE_NAME [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `BUNDLE_NAME` | Name of the bundle to inspect |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--help` |  | Show help message and exit |

### Examples

#### Bundle Information

```bash
# Show bundle details
oas-patch info my-bundle
```

Example output:
```
╭─────────────────────────── Bundle Information ───────────────────────────╮
│                                                                           │
│  📦 Bundle: my-bundle                                                     │
│  📝 Description: Application deployment bundle for multiple environments  │
│  🏷️  Version: 2.1.0                                                       │
│                                                                           │
│  📊 Statistics:                                                           │
│    • Overlays: 4                                                         │
│    • Variables: 6                                                        │
│    • Environments: development, staging, production                      │
│                                                                           │
│  📄 Overlays:                                                             │
│    1. base-config.yaml (All environments)                                │
│       └── Base application configuration                                 │
│    2. database.yaml (staging, production)                                │
│       └── Database connection settings                                   │
│    3. monitoring.yaml (production)                                       │
│       └── Production monitoring configuration                            │
│    4. debug.yaml (development)                                           │
│       └── Development debugging features                                 │
│                                                                           │
│  🔧 Variables:                                                            │
│    • api_version: v2.1                                                   │
│    • base_url: https://api.example.com                                   │
│    • timeout: 30                                                         │
│    • retry_count: 3                                                      │
│    • enable_cache: true                                                  │
│    • log_level: info                                                     │
│                                                                           │
╰───────────────────────────────────────────────────────────────────────────╯
```

#### Bundle with Custom Config

```bash
# Show info from custom directory
oas-patch info production-bundle --config ./deployments
```

## bundle-validate

Validate bundle configuration and all associated overlay files.

### Syntax

```bash
oas-patch bundle-validate BUNDLE_NAME [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `BUNDLE_NAME` | Name of the bundle to validate |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Validation

```bash
# Validate bundle
oas-patch bundle-validate my-bundle

# Output on success:
# ✓ Bundle 'my-bundle' validation successful

# Output on failure:
# ✗ Bundle 'my-bundle' validation failed:
#   - Overlay 'invalid.yaml': Missing required field 'overlay'
#   - Variable 'undefined_var' referenced but not defined
```

#### Validation with Custom Config

```bash
# Validate from custom directory
oas-patch bundle-validate production-bundle --config ./configs
```

### Validation Checks

The command validates:

#### Bundle Configuration
- Valid YAML syntax
- Required fields (`name`, `overlays`)
- Proper overlay references
- Variable definitions

#### Overlay Files
- File existence
- Valid overlay format
- JSONPath syntax
- Template syntax (if using templates)

#### Variable References
- All referenced variables are defined
- No circular dependencies
- Proper template syntax

#### Example Valid Bundle

```yaml
name: "example-bundle"
description: "Example bundle configuration"
version: "1.0.0"
variables:
  api_version: "v1"
  base_url: "https://api.example.com"
overlays:
  - path: "base.yaml"
    description: "Base configuration"
  - path: "production.yaml"
    environment: ["production"]
    variables:
      log_level: "error"
```

## init

Create example overlay configuration to get started quickly.

### Syntax

```bash
oas-patch init [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Configuration directory (default: overlays) |
| `--force` |  | Overwrite existing configurations |
| `--help` |  | Show help message and exit |

### Examples

#### Initialize Default Configuration

```bash
# Create example configuration
oas-patch init

# Output:
# Creating configuration structure in overlays
# Example configuration created successfully!
# Try the following commands:
#   oas-patch list-bundles --config overlays
#   oas-patch list-environments --config overlays
#   oas-patch info example-bundle --config overlays
#   oas-patch bundle-validate example-bundle --config overlays
```

#### Custom Directory

```bash
# Initialize in custom directory
oas-patch init --config ./my-overlays
```

#### Force Overwrite

```bash
# Overwrite existing configuration
oas-patch init --force
```

### Generated Structure

The `init` command creates this structure:

```
overlays/
├── example-bundle/
│   ├── bundle.yaml          # Bundle configuration
│   ├── add-version.yaml     # Example overlay
│   └── add-server.yaml      # Example overlay
└── environments/
    ├── staging.yaml         # Staging environment
    └── production.yaml      # Production environment
```

### Generated Files Content

#### bundle.yaml
```yaml
name: 'example-bundle'
description: 'Example overlay bundle configuration'
version: '1.0.0'
variables:
  api_version: 'v1'
  base_url: 'https://api.example.com'
overlays:
  - path: 'add-version.yaml'
    description: 'Add API version to info section'
    environment: ['staging', 'production']
  - path: 'add-server.yaml'
    description: 'Add server configuration'
    variables:
      server_description: 'Example API Server'
```

#### Example Overlays
- **add-version.yaml**: Adds API version information
- **add-server.yaml**: Adds server configuration with templates

#### Environment Files
- **staging.yaml**: Staging environment variables
- **production.yaml**: Production environment variables

### Testing Generated Configuration

```bash
# After initialization, test the examples
oas-patch list-bundles
oas-patch info example-bundle
oas-patch bundle-validate example-bundle

# Apply to a test API (if you have one)
oas-patch apply your-api.yaml example-bundle --env staging --dry-run
```

## Common Bundle Workflows

### Development Workflow

```bash
# 1. Initialize configuration
oas-patch init

# 2. Create your bundle
mkdir overlays/my-app-bundle
cat > overlays/my-app-bundle/bundle.yaml << EOF
name: "my-app-bundle"
description: "My application bundle"
version: "1.0.0"
overlays:
  - path: "base.yaml"
EOF

# 3. Validate bundle
oas-patch bundle-validate my-app-bundle

# 4. Test application
oas-patch apply api.yaml my-app-bundle --dry-run

# 5. Apply for real
oas-patch apply api.yaml my-app-bundle -o output.yaml
```

### CI/CD Integration

```bash
#!/bin/bash
# deploy.sh - Bundle deployment script

BUNDLE_NAME=${1:-production-bundle}
ENVIRONMENT=${2:-production}
API_FILE=${3:-api.yaml}

echo "Validating bundle..."
if ! oas-patch bundle-validate "$BUNDLE_NAME"; then
    echo "❌ Bundle validation failed"
    exit 1
fi

echo "Applying bundle for $ENVIRONMENT..."
oas-patch apply "$API_FILE" "$BUNDLE_NAME" \
    --env "$ENVIRONMENT" \
    --var build_number="$BUILD_NUMBER" \
    --var git_commit="$GIT_COMMIT" \
    -o "api-$ENVIRONMENT.yaml"

echo "✅ Deployment complete: api-$ENVIRONMENT.yaml"
```

### Multi-Environment Deployment

```bash
#!/bin/bash
# deploy-all-environments.sh

BUNDLE_NAME=${1:-app-bundle}
API_FILE=${2:-api.yaml}

for env in development staging production; do
    echo "🚀 Deploying to $env..."
    
    if oas-patch apply "$API_FILE" "$BUNDLE_NAME" \
        --env "$env" \
        --verbose \
        -o "api-$env.yaml"; then
        echo "✅ $env deployment successful"
    else
        echo "❌ $env deployment failed"
        exit 1
    fi
done

echo "🎉 All environments deployed successfully!"
```

## Troubleshooting

### Common Issues

#### Bundle Not Found

```bash
$ oas-patch apply api.yaml missing-bundle
Error: Bundle 'missing-bundle' not found in overlays directory
```

**Solution**: Check bundle name and ensure `bundle.yaml` exists in the bundle directory.

#### Environment Not Found

```bash
$ oas-patch apply api.yaml my-bundle --env missing-env
Warning: No overlays found for specified environment
```

**Solution**: Check environment name and overlay environment filters.

#### Template Errors

```bash
$ oas-patch apply api.yaml my-bundle --var incomplete=
Error: Template processing failed: 'undefined_var' is undefined
```

**Solution**: Provide all required variables or add defaults in templates.

#### Variable Resolution

```bash
# Debug variable issues with verbose mode
oas-patch apply api.yaml my-bundle --env production --verbose

# Check bundle info for variable requirements
oas-patch info my-bundle
```

### Debug Techniques

```bash
# Use dry-run to preview changes
oas-patch apply api.yaml my-bundle --env production --dry-run

# Enable verbose mode for detailed output
oas-patch apply api.yaml my-bundle --verbose

# Validate bundle configuration
oas-patch bundle-validate my-bundle

# Check bundle information
oas-patch info my-bundle
```

## Next Steps

- [Validation Commands](validation-commands.md) - Additional validation options
- [Multi-Environment Setup](../tutorials/multi-environment.md) - Hands-on bundle examples
- [CI/CD Integration](../tutorials/cicd-integration.md) - Automated bundle deployment
