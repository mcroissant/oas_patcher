# Validation Commands

Validation commands help ensure the correctness and quality of your OpenAPI overlays, bundles, and configurations. These commands provide comprehensive checking capabilities for different aspects of your overlay management setup.

## Overview

OAS Patcher provides several validation approaches:

- **Single Overlay Validation** - Validate individual overlay files
- **Bundle Validation** - Validate bundle configurations and all contained overlays  
- **Generated API Validation** - Validate the final OpenAPI documents after overlay application
- **Batch Validation** - Validate multiple files or configurations at once

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

### Validation Checks

The validate command performs these checks:

#### Format Validation
- Valid YAML/JSON syntax
- Proper file encoding (UTF-8)
- Correct MIME type detection

#### Overlay Structure
- Required `overlay` field with valid version
- Required `info` object with title and version
- Required `actions` array

#### Action Validation
- Valid action types (`update`, `remove`)
- Required fields for each action type
- Proper target JSONPath syntax
- Update value type compatibility

#### JSONPath Validation
- Syntax correctness
- Proper escaping of special characters
- Valid property and array access patterns
- Reserved character handling

### Output Formats

#### Shell Format (Default)

Good overlay:
```bash
$ oas-patch validate good-overlay.yaml
✓ Overlay validation successful
```

Invalid overlay:
```bash
$ oas-patch validate bad-overlay.yaml
✗ Overlay validation failed:
  - Line 3: Missing required field 'overlay'
  - Line 8: Invalid JSONPath expression '$.invalid..path'
  - Line 12: Action missing 'update' or 'remove' operation
```

#### Log Format

```bash
$ oas-patch validate overlay.yaml --format log
INFO: Starting validation for overlay.yaml
INFO: Checking overlay header...
INFO: Validating action 1 of 3...
ERROR: Line 8: Invalid JSONPath expression '$.paths../users'
INFO: Validating action 2 of 3...
WARNING: Action targets non-standard field 'x-custom-field'
INFO: Validating action 3 of 3...
INFO: Validation complete: 1 error, 1 warning
```

#### YAML Format

```bash
$ oas-patch validate overlay.yaml --format yaml
validation:
  file: "overlay.yaml"
  valid: false
  timestamp: "2024-01-15T10:30:00Z"
  errors:
    - line: 3
      column: 1
      message: "Missing required field: 'overlay'"
      severity: "error"
      code: "MISSING_FIELD"
    - line: 8
      column: 15
      message: "Invalid JSONPath expression"
      severity: "error"
      code: "INVALID_JSONPATH"
      details: "Double dots (..) are not valid in JSONPath"
  warnings:
    - line: 12
      column: 8
      message: "Using non-standard extension field"
      severity: "warning"
      code: "NON_STANDARD_FIELD"
  statistics:
    total_actions: 3
    valid_actions: 1
    invalid_actions: 2
```

### Examples

#### Basic Validation

```bash
# Validate single overlay
oas-patch validate my-overlay.yaml

# Validate with detailed logging
oas-patch validate my-overlay.yaml --format log

# Get machine-readable output
oas-patch validate my-overlay.yaml --format yaml > validation-results.yaml
```

#### Batch Validation

```bash
#!/bin/bash
# validate-all-overlays.sh

echo "Validating all overlay files..."
failed=0

for overlay in overlays/**/*.yaml; do
    echo -n "Validating $(basename "$overlay")... "
    
    if oas-patch validate "$overlay" > /dev/null 2>&1; then
        echo "✅ PASS"
    else
        echo "❌ FAIL"
        oas-patch validate "$overlay" --format log
        failed=$((failed + 1))
    fi
done

echo "Validation complete. $failed failures."
exit $failed
```

#### CI/CD Integration

```yaml
# .github/workflows/validate-overlays.yml
name: Validate Overlays

on:
  pull_request:
    paths: ['overlays/**/*.yaml']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install OAS Patcher
      run: pip install oas-patch
    - name: Validate overlays
      run: |
        find overlays -name "*.yaml" -type f | while read file; do
          echo "Validating $file"
          oas-patch validate "$file" --format log
        done
```

#### Advanced Validation Workflow

```bash
#!/bin/bash
# comprehensive-validation.sh

OVERLAY_DIR=${1:-overlays}
REPORT_FILE=${2:-validation-report.yaml}

echo "🔍 Starting comprehensive validation..."

# Initialize report
cat > "$REPORT_FILE" << EOF
validation_report:
  timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  directory: "$OVERLAY_DIR"
  files: []
EOF

total_files=0
valid_files=0
failed_files=0

# Validate each overlay file
find "$OVERLAY_DIR" -name "*.yaml" -type f | while read file; do
    total_files=$((total_files + 1))
    echo "Validating $file..."
    
    # Validate and capture output
    if validation_output=$(oas-patch validate "$file" --format yaml 2>&1); then
        valid_files=$((valid_files + 1))
        echo "  ✅ Valid"
    else
        failed_files=$((failed_files + 1))
        echo "  ❌ Failed"
        echo "$validation_output"
    fi
    
    # Add to report (simplified for example)
    echo "  - file: \"$file\"" >> "$REPORT_FILE"
    echo "    valid: $([ $? -eq 0 ] && echo true || echo false)" >> "$REPORT_FILE"
done

echo "📊 Validation Summary:"
echo "  Total files: $total_files"
echo "  Valid files: $valid_files"
echo "  Failed files: $failed_files"
echo "  Report saved: $REPORT_FILE"
```

## bundle-validate

Validate bundle configuration and all associated overlay files. This is covered in detail in [Bundle Commands](bundle-commands.md#bundle-validate).

### Quick Reference

```bash
# Validate bundle and all its overlays
oas-patch bundle-validate my-bundle

# Validate with custom config directory
oas-patch bundle-validate my-bundle --config ./custom-overlays
```

## Generated API Validation

While not a specific OAS Patcher command, validating the final generated OpenAPI documents is crucial. Here are recommended approaches:

### Using OpenAPI Validators

```bash
# Install validators
npm install -g @apidevtools/swagger-parser
npm install -g spectral-cli
pip install openapi-spec-validator

# Generate and validate
oas-patch apply api.yaml my-bundle -o generated-api.yaml

# Validate with different tools
swagger-parser validate generated-api.yaml
spectral lint generated-api.yaml --ruleset=spectral:oas
openapi-spec-validator generated-api.yaml
```

### Comprehensive Validation Workflow

```bash
#!/bin/bash
# validate-generated-apis.sh

BUNDLE_NAME=${1:-production-bundle}
BASE_API=${2:-api.yaml}

echo "🚀 Validating generated APIs for all environments..."

for env in development staging production; do
    echo "📝 Generating API for $env..."
    
    output_file="api-$env.yaml"
    
    # Generate API
    if oas-patch apply "$BASE_API" "$BUNDLE_NAME" \
        --env "$env" \
        -o "$output_file"; then
        echo "✅ Generated: $output_file"
        
        # Validate generated API
        echo "🔍 Validating $output_file..."
        
        # Basic OpenAPI validation
        if swagger-parser validate "$output_file"; then
            echo "✅ OpenAPI validation passed"
        else
            echo "❌ OpenAPI validation failed"
            exit 1
        fi
        
        # Linting with Spectral
        if spectral lint "$output_file" --ruleset=spectral:oas; then
            echo "✅ Linting passed"
        else
            echo "⚠️  Linting issues found"
        fi
        
    else
        echo "❌ Failed to generate API for $env"
        exit 1
    fi
done

echo "🎉 All environments validated successfully!"
```

## Validation Best Practices

### 1. Layered Validation Strategy

```bash
# Level 1: Syntax validation
oas-patch validate overlay.yaml

# Level 2: Bundle validation
oas-patch bundle-validate my-bundle

# Level 3: Generated API validation
oas-patch apply api.yaml my-bundle -o temp-api.yaml
swagger-parser validate temp-api.yaml
rm temp-api.yaml

# Level 4: Business logic validation
# Custom scripts to check business rules
```

### 2. Pre-commit Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "🔍 Validating overlays before commit..."

# Find all modified overlay files
modified_overlays=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(yaml|yml)$' | grep overlays/)

if [ -n "$modified_overlays" ]; then
    for file in $modified_overlays; do
        echo "Validating $file..."
        if ! oas-patch validate "$file"; then
            echo "❌ Validation failed for $file"
            echo "Please fix the errors before committing."
            exit 1
        fi
    done
    echo "✅ All overlay validations passed"
fi

# Validate modified bundles
modified_bundles=$(git diff --cached --name-only --diff-filter=ACM | grep bundle.yaml | sed 's|/bundle.yaml||' | sed 's|.*/||')

if [ -n "$modified_bundles" ]; then
    for bundle in $modified_bundles; do
        echo "Validating bundle: $bundle..."
        if ! oas-patch bundle-validate "$bundle"; then
            echo "❌ Bundle validation failed for $bundle"
            exit 1
        fi
    done
    echo "✅ All bundle validations passed"
fi
```

### 3. Continuous Integration

```yaml
# .github/workflows/validation.yml
name: Comprehensive Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate-overlays:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install OAS Patcher
      run: pip install oas-patch[enhanced]
      
    - name: Validate individual overlays
      run: |
        find overlays -name "*.yaml" -path "*/overlays/*" | while read file; do
          echo "Validating $file"
          oas-patch validate "$file" --format log
        done
        
    - name: Validate bundles
      run: |
        find overlays -name "bundle.yaml" | while read file; do
          bundle_name=$(dirname "$file" | basename)
          echo "Validating bundle: $bundle_name"
          oas-patch bundle-validate "$bundle_name"
        done
        
    - name: Generate and validate APIs
      run: |
        # Assuming test-api.yaml exists
        for bundle in $(oas-patch list-bundles | tail -n +2); do
          for env in development staging production; do
            echo "Testing $bundle with $env"
            oas-patch apply test-api.yaml "$bundle" \
              --env "$env" \
              --dry-run
          done
        done
```

### 4. Error Classification

Organize validation errors by severity:

```bash
#!/bin/bash
# categorize-validation-errors.sh

validate_with_categories() {
    local file=$1
    local output=$(oas-patch validate "$file" --format yaml)
    
    # Extract error counts by severity
    critical=$(echo "$output" | yq '.validation.errors[] | select(.severity == "error") | length')
    warnings=$(echo "$output" | yq '.validation.warnings[] | length')
    
    echo "File: $file"
    echo "  Critical errors: ${critical:-0}"
    echo "  Warnings: ${warnings:-0}"
    
    # Fail CI for critical errors
    if [ "${critical:-0}" -gt 0 ]; then
        echo "❌ Critical errors found in $file"
        return 1
    elif [ "${warnings:-0}" -gt 0 ]; then
        echo "⚠️  Warnings found in $file"
        return 0
    else
        echo "✅ $file is valid"
        return 0
    fi
}

# Validate all overlays with categorization
find overlays -name "*.yaml" -type f | while read file; do
    validate_with_categories "$file"
done
```

## Common Validation Errors

### 1. JSONPath Syntax Errors

```yaml
# ❌ Wrong - double dots
actions:
  - target: "$.paths../users"
    update: {}

# ✅ Correct - proper path syntax  
actions:
  - target: "$.paths./users"
    update: {}
```

### 2. Missing Required Fields

```yaml
# ❌ Wrong - missing overlay version
info:
  title: "My Overlay"
actions: []

# ✅ Correct - includes overlay version
overlay: 1.0.0
info:
  title: "My Overlay"
  version: "1.0.0"
actions: []
```

### 3. Invalid Action Structure

```yaml
# ❌ Wrong - missing operation
actions:
  - target: "$.info.version"
    # Missing update or remove

# ✅ Correct - includes operation
actions:
  - target: "$.info.version"
    update: "2.0.0"
```

### 4. Template Syntax Errors

```yaml
# ❌ Wrong - unclosed template
actions:
  - target: "$.info.version"
    update: "{{ version"

# ✅ Correct - properly closed
actions:
  - target: "$.info.version"
    update: "{{ version }}"
```

## Troubleshooting Validation Issues

### Debug Process

1. **Check file syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('overlay.yaml'))"
   ```

2. **Validate incrementally**:
   ```bash
   # Test minimal overlay first
   cat > minimal.yaml << EOF
   overlay: 1.0.0
   info:
     title: "Test"
     version: "1.0.0"
   actions: []
   EOF
   
   oas-patch validate minimal.yaml
   ```

3. **Use verbose formats**:
   ```bash
   oas-patch validate overlay.yaml --format log
   ```

4. **Test JSONPath expressions**:
   ```bash
   # Use online JSONPath testers or tools like jq
   echo '{"info": {"version": "1.0.0"}}' | jq '.info.version'
   ```

### Common Fixes

| Error | Solution |
|-------|----------|
| Invalid YAML | Check indentation, quotes, special characters |
| Missing overlay field | Add `overlay: 1.0.0` at the top |
| Invalid JSONPath | Use proper syntax: `$.path.to.field` |
| Template errors | Check Jinja2 syntax: `{{ variable }}` |
| File not found | Verify file paths and permissions |

## Next Steps

- [Configuration Guide](../configuration/overlay-config.md) - Detailed overlay configuration
- [Basic Overlay Tutorial](../tutorials/basic-overlay.md) - Hands-on validation examples
- [CI/CD Integration](../tutorials/cicd-integration.md) - Automated validation in pipelines
