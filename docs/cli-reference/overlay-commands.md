# Overlay Commands

Overlay commands provide core functionality for applying, generating, and validating individual OpenAPI overlays. These commands work with single overlay files and don't require the enhanced bundle management features.

## overlay

Apply an OpenAPI overlay to your OpenAPI document.

### Syntax

```bash
oas-patch overlay OPENAPI OVERLAY [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `OPENAPI` | Path to the OpenAPI description (YAML/JSON) |
| `OVERLAY` | Path to the Overlay document (YAML/JSON) |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Path to save the modified OpenAPI document. Defaults to stdout. |
| `--sanitize` |  | Remove special characters from the OpenAPI document |
| `--help` |  | Show help message and exit |

### Examples

#### Basic Overlay Application

```bash
# Apply overlay and save to file
oas-patch overlay petstore.yaml security-overlay.yaml -o petstore-secure.yaml

# Apply overlay and output to stdout
oas-patch overlay api.yaml version-update.yaml

# Apply overlay with sanitization
oas-patch overlay api.yaml cleanup-overlay.yaml --sanitize -o clean-api.yaml
```

#### Output Format Detection

The command automatically detects output format based on the input file:

```bash
# YAML input produces YAML output
oas-patch overlay api.yaml overlay.yaml -o output.yaml

# JSON input produces JSON output  
oas-patch overlay api.json overlay.json -o output.json

# Mixed formats work too
oas-patch overlay api.yaml overlay.json -o output.yaml
```

#### Piping and Redirection

```bash
# Pipe output to other commands
oas-patch overlay api.yaml overlay.yaml | grep "version"

# Redirect output to file
oas-patch overlay api.yaml overlay.yaml > modified-api.yaml

# Use with other tools
oas-patch overlay api.yaml overlay.yaml | swagger-codegen validate -
```

### Return Codes

| Code | Description |
|------|-------------|
| 0 | Success - overlay applied successfully |
| 1 | Error - file not found, invalid format, or application failed |

### Error Scenarios

#### File Not Found

```bash
$ oas-patch overlay missing.yaml overlay.yaml
Error: [Errno 2] No such file or directory: 'missing.yaml'
```

#### Invalid Format

```bash
$ oas-patch overlay invalid.yaml overlay.yaml  
Error: YAML parsing error: expected '<document start>', but found '<scalar>'
```

#### Invalid Overlay

```bash
$ oas-patch overlay api.yaml bad-overlay.yaml
Error: Invalid overlay format: missing required 'overlay' field
```

## diff

Generate an OpenAPI Overlay from the differences between two OpenAPI documents.

### Syntax

```bash
oas-patch diff ORIGINAL MODIFIED [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `ORIGINAL` | Path to the original OpenAPI document |
| `MODIFIED` | Path to the modified OpenAPI document |

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Path to save the generated OpenAPI Overlay |
| `--help` |  | Show help message and exit |

### Examples

#### Generate Basic Overlay

```bash
# Compare two API versions and generate overlay
oas-patch diff api-v1.yaml api-v2.yaml -o upgrade-overlay.yaml

# Output overlay to stdout for inspection
oas-patch diff original.yaml modified.yaml
```

#### Version Control Integration

```bash
# Generate overlay from git diff
git show HEAD:api.yaml > api-old.yaml
oas-patch diff api-old.yaml api.yaml -o recent-changes.yaml

# Compare with previous version
oas-patch diff api-v1.0.0.yaml api-v1.1.0.yaml -o v1.1.0-changes.yaml
```

#### Workflow Examples

```bash
# 1. Make manual changes to API
cp api.yaml api-backup.yaml
# ... edit api.yaml manually ...

# 2. Generate overlay from changes
oas-patch diff api-backup.yaml api.yaml -o manual-changes.yaml

# 3. Apply overlay to other environments
oas-patch overlay base-api.yaml manual-changes.yaml -o staging-api.yaml
```

### Generated Overlay Format

The diff command produces overlays in this format:

```yaml
overlay: 1.0.0
info:
  title: Generated Overlay
  version: 1.0.0
actions:
  - target: "$.info.version"
    update: "2.0.0"
  - target: "$.paths./new-endpoint"
    update:
      get:
        summary: "New endpoint"
        responses:
          '200':
            description: "Success"
```

### Limitations

- Only generates `update` actions (not `remove`)
- May produce verbose overlays for complex changes
- Doesn't preserve comments or formatting

## validate

Validate an OpenAPI Overlay document against the specification.

### Syntax

```bash
oas-patch validate OVERLAY_FILE [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `OVERLAY_FILE` | Path to the overlay document to validate (YAML/JSON) |

### Options

| Option | Description |
|--------|-------------|
| `--format` | Output format: `sh` (shell), `log`, or `yaml`. Default: `sh` |
| `--help` | Show help message and exit |

### Output Formats

#### Shell Format (default)

```bash
$ oas-patch validate good-overlay.yaml
✓ Overlay validation successful
```

```bash
$ oas-patch validate bad-overlay.yaml
✗ Overlay validation failed:
  - Missing required field: 'overlay'
  - Invalid action target: '$.invalid..path'
```

#### Log Format

```bash
$ oas-patch validate overlay.yaml --format log
INFO: Starting overlay validation
INFO: Checking overlay header
INFO: Validating actions
ERROR: Invalid JSONPath in action 1: $.invalid..path
ERROR: Missing required field 'overlay'
```

#### YAML Format

```bash
$ oas-patch validate overlay.yaml --format yaml
validation:
  valid: false
  errors:
    - message: "Missing required field: 'overlay'"
      location: "overlay"
    - message: "Invalid JSONPath expression"
      location: "actions[0].target"
  warnings: []
```

### Examples

#### Validate Single Overlay

```bash
# Basic validation
oas-patch validate my-overlay.yaml

# Verbose output
oas-patch validate my-overlay.yaml --format log

# Machine-readable output
oas-patch validate my-overlay.yaml --format yaml
```

#### Batch Validation

```bash
# Validate all overlays in directory
find overlays/ -name "*.yaml" -exec oas-patch validate {} \;

# Validate with error collection
for file in overlays/*.yaml; do
    echo "Validating $file"
    oas-patch validate "$file" --format log
done
```

#### CI/CD Integration

```bash
#!/bin/bash
# validate-overlays.sh

failed=0
for overlay in overlays/*.yaml; do
    if ! oas-patch validate "$overlay"; then
        echo "❌ Validation failed: $overlay"
        failed=1
    else
        echo "✅ Valid: $overlay"
    fi
done

exit $failed
```

### Validation Rules

The validate command checks for:

#### Required Fields

- `overlay` field with valid version
- `info` object with title and version
- `actions` array with valid action objects

#### Action Validation

- Valid `target` JSONPath expressions
- Proper action types (`update`, `remove`, etc.)
- Required fields for each action type

#### JSONPath Validation

- Syntax correctness
- Proper escaping of special characters
- Valid property and array access

#### Example Valid Overlay

```yaml
overlay: 1.0.0
info:
  title: "Example Overlay"
  version: "1.0.0"
actions:
  - target: "$.info.version"
    update: "2.0.0"
  - target: "$.paths./users.get.summary"
    update: "Get all users"
```

#### Example Invalid Overlay

```yaml
# Missing overlay version
info:
  title: "Bad Overlay"
actions:
  - target: "$.invalid..path"  # Invalid JSONPath
    update: "value"
  - target: "$.info.version"
    # Missing update/remove action
```

### Return Codes

| Code | Description |
|------|-------------|
| 0 | Valid overlay |
| 1 | Invalid overlay or file error |

## Common Patterns

### Development Workflow

```bash
# 1. Create overlay
cat > my-overlay.yaml << EOF
overlay: 1.0.0
info:
  title: "Development Overlay"
  version: "1.0.0"
actions:
  - target: "$.info.version"
    update: "dev-$(date +%Y%m%d)"
EOF

# 2. Validate overlay
oas-patch validate my-overlay.yaml

# 3. Apply if valid
if oas-patch validate my-overlay.yaml; then
    oas-patch overlay api.yaml my-overlay.yaml -o api-dev.yaml
    echo "✅ Overlay applied successfully"
else
    echo "❌ Overlay validation failed"
    exit 1
fi
```

### Testing Overlays

```bash
# Test overlay application without saving
oas-patch overlay api.yaml test-overlay.yaml | head -20

# Compare before and after
oas-patch overlay api.yaml my-overlay.yaml > modified.yaml
diff api.yaml modified.yaml
```

### Overlay Chaining

```bash
# Apply multiple overlays in sequence
oas-patch overlay api.yaml base-overlay.yaml > temp1.yaml
oas-patch overlay temp1.yaml feature-overlay.yaml > temp2.yaml
oas-patch overlay temp2.yaml env-overlay.yaml > final.yaml
rm temp1.yaml temp2.yaml
```

## Troubleshooting

### Common Issues

#### JSONPath Errors

```bash
# Wrong - double dots
"$.paths..get"

# Correct - single dots for navigation
"$.paths./users.get"
```

#### File Encoding

```bash
# If you get encoding errors, ensure UTF-8
file --mime-encoding overlay.yaml

# Convert if necessary
iconv -f ISO-8859-1 -t UTF-8 overlay.yaml > overlay-utf8.yaml
```

#### YAML Syntax

```bash
# Use a YAML validator for syntax issues
python -c "import yaml; yaml.safe_load(open('overlay.yaml'))"
```

### Debug Techniques

```bash
# Check file format
file overlay.yaml

# Validate YAML syntax
python -c "import yaml; print(yaml.safe_load(open('overlay.yaml')))"

# Test JSONPath expressions
# Use online JSONPath testers or tools like jq
```

## Next Steps

- [Bundle Commands](bundle-commands.md) - Learn about advanced bundle management
- [Validation Commands](validation-commands.md) - Additional validation options
- [Basic Overlay Tutorial](../tutorials/basic-overlay.md) - Hands-on overlay examples
