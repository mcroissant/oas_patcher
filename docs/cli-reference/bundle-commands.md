# Bundle Commands

Bundle commands provide advanced overlay management capabilities, including environment-specific configurations, template processing, and organized overlay collections. These commands require enhanced dependencies.

## Prerequisites

Bundle commands require enhanced features:

```bash
pip install oas-patch[enhanced]
# or
pip install Jinja2 rich click
```

## bundle apply

Apply overlay bundle to OpenAPI document with environment support and template processing.

### Syntax

```bash
oas-patch bundle apply OPENAPI_FILE BUNDLE_FILE [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `OPENAPI_FILE` | Path to the OpenAPI document (YAML/JSON) |
| `BUNDLE_FILE` | Path to the bundle configuration file (e.g., bundle.yaml) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output file path (auto-generated if not specified) |
| `--env` | `-e` | Environment name to use for filtering overlays |
| `--format` | `-f` | Output format: `yaml` or `json` |
| `--var` |  | Variables in key=value format (repeatable) |
| `--dry-run` |  | Preview changes without saving |
| `--verbose` | `-v` | Verbose output with progress indicators |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Bundle Application

```bash
# Apply all overlays in bundle
oas-patch bundle apply api.yaml bundle.yaml -o output.yaml

# Apply with auto-generated output filename
oas-patch bundle apply api.yaml bundle.yaml
# Creates: api-example-bundle.yaml
```

#### Environment-Specific Application

```bash
# Apply only development overlays
oas-patch bundle apply api.yaml bundle.yaml --env development -o api-dev.yaml

# Apply production overlays
oas-patch bundle apply api.yaml bundle.yaml --env production -o api-prod.yaml

# Apply staging with verbose output
oas-patch bundle apply api.yaml bundle.yaml --env staging --verbose
```

#### Variable Substitution

```bash
# Pass variables to templates
oas-patch bundle apply api.yaml bundle.yaml \
  --var api_version=v2.1 \
  --var base_url=https://api.example.com \
  -o api-configured.yaml

# Multiple variables for environment
oas-patch bundle apply api.yaml deploy-bundle.yaml \
  --env production \
  --var region=us-east-1 \
  --var instance_type=production \
  --var monitoring_enabled=true
```

#### Dry Run and Testing

```bash
# Preview changes without saving
oas-patch bundle apply api.yaml bundle.yaml --env development --dry-run

# Test with variables
oas-patch bundle apply api.yaml config-bundle.yaml \
  --var debug_mode=true \
  --var log_level=debug \
  --dry-run
```

#### Advanced Configuration

```bash
# Force JSON output format
oas-patch bundle apply api.yaml bundle.yaml \
  --format json \
  -o api-bundle.json

# Verbose mode with progress tracking
oas-patch bundle apply api.yaml large-bundle.yaml \
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

## bundle validate

Validate bundle configuration and all associated overlay files.

### Syntax

```bash
oas-patch bundle validate BUNDLE_FILE [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `BUNDLE_FILE` | Path to the bundle configuration file (e.g., bundle.yaml) |

### Examples

#### Basic Validation

```bash
# Validate bundle
oas-patch bundle validate bundle.yaml

# Output on success:
# ✓ Bundle 'example-bundle' validation successful

# Output on failure:
# ✗ Bundle 'example-bundle' validation failed:
#   - Overlay 'invalid.yaml': Missing required field 'overlay'
#   - Variable 'undefined_var' referenced but not defined
```

### Validation Checks

The command validates:

#### Bundle Configuration
- Valid YAML syntax
- Required fields (`name`, `overlays`)
- Proper overlay references
- Variable definitions

#### Overlay Files
- File existence (relative to bundle file)
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
  - path: "overlays/base.yaml"
    description: "Base configuration"
  - path: "overlays/production.yaml"
    environment: ["production"]
    variables:
      log_level: "error"
```

## bundle init

Create example overlay bundle in current directory.

### Syntax

```bash
oas-patch bundle init [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--force` |  | Overwrite existing files |
| `--help` |  | Show help message and exit |

### Examples

#### Create Example Bundle

```bash
# Create example bundle in current directory
oas-patch bundle init

# Output:
# Example bundle created successfully!
# Created files:
#   - bundle.yaml (bundle configuration)
#   - overlays/add-version.yaml (version overlay)
#   - overlays/add-server.yaml (server overlay)
```

#### Force Overwrite

```bash
# Overwrite existing files
oas-patch bundle init --force
```

### Created Structure

The command creates:

```
./
├── bundle.yaml              # Bundle configuration
└── overlays/
    ├── add-version.yaml     # Version overlay example
    └── add-server.yaml      # Server overlay example
```

#### Example Bundle Configuration

```yaml
name: "example-bundle"
description: "Example overlay bundle configuration"
version: "1.0.0"
variables:
  api_version: "v1"
  base_url: "https://api.example.com"
overlays:
  - path: "overlays/add-version.yaml"
    description: "Add API version to info section"
  - path: "overlays/add-server.yaml"
    description: "Add server configuration"
    variables:
      server_description: "Example API Server"
## Troubleshooting

### Common Issues

#### Bundle File Not Found

```bash
$ oas-patch bundle apply api.yaml missing-bundle.yaml
Error: Path 'missing-bundle.yaml' does not exist.
```

**Solution**: Check bundle file path and ensure the bundle.yaml file exists.

#### Environment Not Found

```bash
$ oas-patch bundle apply api.yaml bundle.yaml --env missing-env
Warning: No overlays found for specified environment
```

**Solution**: Check environment name and overlay environment filters.

#### Template Errors

```bash
$ oas-patch bundle apply api.yaml bundle.yaml --var incomplete=
Error: Template processing failed: 'undefined_var' is undefined
```

**Solution**: Provide all required variables or add defaults in templates.

#### Variable Resolution

```bash
# Debug variable issues with verbose mode
oas-patch bundle apply api.yaml bundle.yaml --env production --verbose
```

### Debug Techniques

```bash
# Use dry-run to preview changes
oas-patch bundle apply api.yaml bundle.yaml --env production --dry-run

# Enable verbose mode for detailed output
oas-patch bundle apply api.yaml bundle.yaml --verbose

# Validate bundle configuration
oas-patch bundle validate bundle.yaml
```

## Next Steps

- [Validation Commands](validation-commands.md) - Additional validation options
- [Multi-Environment Setup](../tutorials/multi-environment.md) - Hands-on bundle examples
- [CI/CD Integration](../tutorials/cicd-integration.md) - Automated bundle deployment

# Enable verbose mode for detailed output
oas-patch bundle apply api.yaml my-bundle --verbose

# Validate bundle configuration
oas-patch bundle validate bundle.yaml
```

## Next Steps

- [Validation Commands](validation-commands.md) - Additional validation options
- [Multi-Environment Setup](../tutorials/multi-environment.md) - Hands-on bundle examples
- [CI/CD Integration](../tutorials/cicd-integration.md) - Automated bundle deployment
