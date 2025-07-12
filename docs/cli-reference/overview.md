# CLI Reference Overview

OAS Patcher provides a comprehensive command-line interface for managing OpenAPI specifications through overlays and bundles. The CLI supports both legacy overlay functionality and enhanced bundle management with environment-specific configurations.

## Command Categories

The OAS Patcher CLI is organized into several command categories:

### Core Commands
- **overlay** - Apply single overlays to OpenAPI documents
- **diff** - Generate overlays from document differences  
- **validate** - Validate overlay documents

### Bundle Management Commands (Enhanced)
- **apply** - Apply overlay bundles to OpenAPI documents
- **list-bundles** - List available overlay bundles
- **info** - Show detailed bundle information
- **bundle-validate** - Validate bundle configurations

### Environment Commands (Enhanced)
- **list-environments** - List available environments
- **init** - Initialize example configuration

### Utility Commands
- **--version** - Show version information
- **--help** - Show help information

## Global Options

Most commands support these global options:

| Option | Short | Description |
|--------|--------|-------------|
| `--help` | `-h` | Show help message and exit |
| `--version` |  | Show the version and exit |
| `--verbose` | `-v` | Enable verbose output |
| `--config` | `-c` | Configuration directory (default: overlays) |

## Enhanced Features

Enhanced commands require additional dependencies and provide:

- **Bundle Management** - Organize multiple overlays with configuration
- **Environment Support** - Environment-specific overlay application
- **Template Processing** - Jinja2 templating with variable substitution
- **Progress Indicators** - Visual progress feedback
- **Rich Output** - Colored and formatted console output

To enable enhanced features:

```bash
pip install oas-patch[enhanced]
# or
pip install Jinja2 rich click
```

## Basic Usage Patterns

### Simple Overlay Application

```bash
# Apply a single overlay
oas-patch overlay api.yaml my-overlay.yaml -o output.yaml

# Validate an overlay
oas-patch validate my-overlay.yaml
```

### Bundle Management

```bash
# Apply a bundle
oas-patch apply api.yaml my-bundle -e production -o output.yaml

# List available bundles
oas-patch list-bundles

# Get bundle information
oas-patch info my-bundle
```

### Environment-Specific Deployment

```bash
# Apply bundle for development
oas-patch apply api.yaml my-bundle --env development

# Apply bundle for production with variables
oas-patch apply api.yaml my-bundle --env production \
  --var api_url=https://api.example.com \
  --var version=v2.0
```

## Output Formats

OAS Patcher automatically detects and preserves the input format (YAML or JSON), but you can override this:

| Format | Description | Extension |
|--------|-------------|-----------|
| `yaml` | YAML format (default) | `.yaml`, `.yml` |
| `json` | JSON format | `.json` |

## File Path Resolution

The CLI supports various path formats:

- **Absolute paths**: `/path/to/file.yaml`
- **Relative paths**: `./overlays/my-overlay.yaml`
- **Bundle paths**: Resolved relative to bundle directory
- **URL schemes**: `http://`, `https://` (if supported)

## Error Handling

The CLI provides clear error messages and appropriate exit codes:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error (file not found, invalid format, etc.) |
| 2 | Validation error |
| 130 | Interrupted by user (Ctrl+C) |

## Verbose Mode

Enable verbose mode (`-v` or `--verbose`) for detailed output including:

- Progress indicators for bundle processing
- Detailed error messages with stack traces
- Variable resolution information
- Overlay application status
- Performance timing information

## Configuration Directory Structure

OAS Patcher expects this directory structure when using bundle commands:

```
overlays/                    # Default config directory
├── bundle-name/
│   ├── bundle.yaml         # Bundle configuration
│   └── overlays/           # Overlay files
│       ├── overlay1.yaml
│       └── overlay2.yaml
├── environments/           # Environment configurations
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
└── another-bundle/
    ├── bundle.yaml
    └── overlays/
```

## Common Workflows

### Development Workflow

```bash
# Initialize configuration
oas-patch init

# Validate bundle
oas-patch bundle-validate my-bundle

# Test bundle application
oas-patch apply api.yaml my-bundle --env development --dry-run

# Apply bundle
oas-patch apply api.yaml my-bundle --env development -o api-dev.yaml
```

### CI/CD Workflow

```bash
# Validate all configurations
oas-patch bundle-validate production-bundle

# Apply production configuration
oas-patch apply base-api.yaml production-bundle \
  --env production \
  --var build_number=$BUILD_NUMBER \
  --var git_commit=$GIT_COMMIT \
  -o api-production.yaml

# Validate generated output
oas-patch validate api-production.yaml
```

### Multi-Environment Deployment

```bash
# Generate configurations for all environments
for env in development staging production; do
    oas-patch apply api.yaml app-bundle \
      --env $env \
      -o api-$env.yaml
done
```

## Shell Completion

OAS Patcher supports shell completion for bash, zsh, and fish. To enable:

### Bash
```bash
eval "$(_OAS_PATCH_COMPLETE=bash_source oas-patch)"
```

### Zsh
```bash
eval "$(_OAS_PATCH_COMPLETE=zsh_source oas-patch)"
```

### Fish
```bash
eval (env _OAS_PATCH_COMPLETE=fish_source oas-patch)
```

Add these lines to your shell's configuration file (`.bashrc`, `.zshrc`, etc.) for persistent completion.

## Environment Variables

The CLI respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OAS_PATCH_CONFIG_DIR` | Default configuration directory | `overlays` |
| `OAS_PATCH_DEFAULT_ENV` | Default environment name | None |
| `OAS_PATCH_VERBOSE` | Enable verbose mode | `false` |
| `NO_COLOR` | Disable colored output | Not set |

## Getting Help

Each command provides detailed help information:

```bash
# General help
oas-patch --help

# Command-specific help
oas-patch overlay --help
oas-patch apply --help

# List all commands
oas-patch --help
```

## Next Steps

- [Overlay Commands](overlay-commands.md) - Detailed reference for overlay operations
- [Bundle Commands](bundle-commands.md) - Complete bundle management reference
- [Validation Commands](validation-commands.md) - Validation and testing commands
