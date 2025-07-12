# Common Issues

This guide helps you troubleshoot the most frequently encountered issues when using OAS Patcher.

## Quick Diagnosis

First, run these commands to get basic diagnostic information:

```bash
# Check OAS Patcher version
oas-patcher --version

# Validate your base specification
oas-patcher validate input.yaml

# Test overlay syntax
oas-patcher validate overlay.yaml

# Dry run to see what would change
oas-patcher apply --input input.yaml --overlay overlay.yaml --dry-run
```

## Installation Issues

### Command Not Found

**Error**: `oas-patcher: command not found`

**Causes**:
- OAS Patcher not installed
- Installation directory not in PATH
- Using wrong Python environment

**Solutions**:
```bash
# Check if installed
pip list | grep oas-patcher

# Install if missing
pip install oas-patcher

# For conda environments
conda install -c conda-forge oas-patcher

# Check PATH (add if needed)
echo $PATH

# Verify installation
which oas-patcher
```

### Permission Errors

**Error**: `Permission denied when installing`

**Causes**:
- Insufficient privileges
- Virtual environment issues
- System Python conflicts

**Solutions**:
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install oas-patcher

# User installation
pip install --user oas-patcher

# System installation (not recommended)
sudo pip install oas-patcher
```

### Dependency Conflicts

**Error**: `Could not find a version that satisfies the requirement`

**Causes**:
- Python version incompatibility
- Conflicting package versions
- Outdated pip

**Solutions**:
```bash
# Update pip
pip install --upgrade pip

# Check Python version (3.8+ required)
python --version

# Install with specific requirements
pip install oas-patcher==latest

# Use dependency resolver
pip install --use-feature=2020-resolver oas-patcher
```

## File Format Issues

### Invalid YAML Syntax

**Error**: `yaml.scanner.ScannerError: while scanning...`

**Causes**:
- Incorrect indentation
- Missing quotes
- Invalid characters
- Mixed tabs/spaces

**Examples and Fixes**:

```yaml
# ❌ Incorrect indentation
overlay: 1.0.0
info:
title: My Overlay  # Wrong indentation

# ✅ Correct indentation
overlay: 1.0.0
info:
  title: My Overlay
```

```yaml
# ❌ Missing quotes for special characters
- target: $.info.x-custom
  update: value with: colon

# ✅ Proper quoting
- target: "$.info.x-custom"
  update: "value with: colon"
```

```yaml
# ❌ Inconsistent data types
- target: "$.info.version"
  update: 1.0  # Number instead of string

# ✅ Consistent types
- target: "$.info.version"
  update: "1.0"
```

**Debugging Tips**:
```bash
# Use YAML validator
python -c "import yaml; print(yaml.safe_load(open('file.yaml')))"

# Check with yamllint
yamllint overlay.yaml

# Use online YAML validators
```

### Invalid JSON Paths

**Error**: `Invalid JSONPath expression`

**Causes**:
- Incorrect JSONPath syntax
- Missing `$` prefix
- Invalid property names
- Escaping issues

**Examples and Fixes**:

```yaml
# ❌ Missing $ prefix
- target: "info.title"
  update: "New Title"

# ✅ Correct JSONPath
- target: "$.info.title"
  update: "New Title"
```

```yaml
# ❌ Incorrect array access
- target: "$.servers.0.url"
  update: "https://api.example.com"

# ✅ Correct array access
- target: "$.servers[0].url"
  update: "https://api.example.com"
```

```yaml
# ❌ Unescaped special characters
- target: "$.paths./api/v1/users.get"
  update: {...}

# ✅ Properly escaped
- target: "$.paths['/api/v1/users'].get"
  update: {...}
```

**Testing JSONPath**:
```bash
# Test JSONPath expressions online
# Use jsonpath.com or similar tools

# Test with command line tools
echo '{"info":{"title":"test"}}' | jq '.info.title'
```

## Overlay Application Issues

### Target Not Found

**Error**: `Target path not found: $.path.to.property`

**Causes**:
- Path doesn't exist in source document
- Typo in target path
- Incorrect document structure assumption

**Solutions**:

1. **Verify the path exists**:
```bash
# Inspect the source document
oas-patcher inspect input.yaml --path "$.info"

# Use jq to explore structure
cat input.yaml | yq eval '.info' -
```

2. **Create missing intermediate paths**:
```yaml
# ❌ Assumes servers array exists
- target: "$.servers[0].url"
  update: "https://api.example.com"

# ✅ Create servers array first
- target: "$.servers"
  update:
    - url: "https://api.example.com"
      description: "Main server"
```

3. **Use conditional targeting**:
```yaml
# Check if path exists before updating
- target: "$.servers"
  update: |
    {% if servers is defined %}
    {{ servers | merge([{"url": API_URL}]) }}
    {% else %}
    [{"url": "{{ API_URL }}", "description": "Main server"}]
    {% endif %}
```

### Action Conflicts

**Error**: `Cannot use both 'update' and 'remove' in the same action`

**Cause**: Invalid action configuration

**Solution**:
```yaml
# ❌ Conflicting actions
- target: "$.info.license"
  update: {...}
  remove: true

# ✅ Separate actions
- target: "$.info.license"
  remove: true
  description: "Remove old license"

- target: "$.info.license"
  update: {...}
  description: "Add new license"
```

### Type Mismatches

**Error**: `Cannot merge object with array`

**Causes**:
- Trying to update array with object
- Type mismatch in update value
- Incorrect assumption about existing type

**Examples and Fixes**:

```yaml
# ❌ Updating array with object
- target: "$.servers"  # servers is an array
  update:
    url: "https://api.example.com"

# ✅ Provide array value
- target: "$.servers"
  update:
    - url: "https://api.example.com"
      description: "Main server"
```

```yaml
# ❌ String where object expected
- target: "$.info.contact"
  update: "support@example.com"

# ✅ Proper object structure
- target: "$.info.contact"
  update:
    email: "support@example.com"
    name: "Support Team"
```

## Template Issues

### Variable Not Defined

**Error**: `Variable 'API_URL' is not defined`

**Causes**:
- Environment variable not set
- Typo in variable name
- Variable not passed to template

**Solutions**:

1. **Set the variable**:
```bash
# Set environment variable
export API_URL="https://api.example.com"

# Pass via command line
oas-patcher apply --env API_URL=https://api.example.com
```

2. **Use default values**:
```yaml
- target: "$.servers[0].url"
  update: "{{ API_URL | default('https://localhost:8080') }}"
```

3. **Check variable names**:
```bash
# List available variables
oas-patcher bundle variables --bundle bundle.yml --environment dev
```

### Template Syntax Errors

**Error**: `TemplateSyntaxError: unexpected token`

**Causes**:
- Invalid Jinja2 syntax
- Unmatched brackets or quotes
- Reserved keywords used incorrectly

**Examples and Fixes**:

```yaml
# ❌ Unmatched brackets
- target: "$.info.title"
  update: "{{ API_NAME | default('API') }"

# ✅ Matched brackets
- target: "$.info.title"
  update: "{{ API_NAME | default('API') }}"
```

```yaml
# ❌ Invalid filter usage
- target: "$.info.version"
  update: "{{ VERSION | upper() }}"

# ✅ Correct filter syntax
- target: "$.info.version"
  update: "{{ VERSION | upper }}"
```

```yaml
# ❌ Complex logic in YAML
- target: "$.servers"
  update: |
    {% if ENVIRONMENT == 'prod' %}
    [{"url": "https://api.example.com"}]
    {% else %}
    [{"url": "https://dev-api.example.com"}]
    {% endif

# ✅ Fixed syntax
- target: "$.servers"
  update: |
    {% if ENVIRONMENT == 'prod' %}
    [{"url": "https://api.example.com"}]
    {% else %}
    [{"url": "https://dev-api.example.com"}]
    {% endif %}
```

## Bundle Issues

### Bundle Not Found

**Error**: `Bundle configuration file not found`

**Causes**:
- Incorrect file path
- File doesn't exist
- Permission issues

**Solutions**:
```bash
# Check file exists
ls -la bundle.yml

# Use absolute path
oas-patcher bundle apply --bundle /full/path/to/bundle.yml

# Check current directory
pwd
```

### Environment Not Found

**Error**: `Environment 'staging' not found in bundle`

**Causes**:
- Typo in environment name
- Environment not defined in bundle
- Case sensitivity issues

**Solutions**:

1. **List available environments**:
```bash
oas-patcher bundle environments --bundle bundle.yml
```

2. **Check bundle configuration**:
```yaml
# Ensure environment is defined
environments:
  development:  # Note: case sensitive
    variables: {...}
  staging:
    variables: {...}
```

3. **Use correct name**:
```bash
# Check exact spelling
oas-patcher bundle apply --environment development  # not 'dev'
```

### Circular Dependencies

**Error**: `Circular dependency detected in overlays`

**Causes**:
- Overlay A depends on B, B depends on A
- Complex dependency chains
- Incorrect overlay ordering

**Solutions**:

1. **Redesign dependencies**:
```yaml
# ❌ Circular dependency
# overlay-a.yaml extends overlay-b.yaml
# overlay-b.yaml extends overlay-a.yaml

# ✅ Linear dependency
# base.yaml <- common.yaml <- specific.yaml
```

2. **Break circular references**:
```yaml
# Create a common base overlay
# Extract shared logic to avoid circles
```

## Performance Issues

### Slow Processing

**Symptoms**:
- Long processing times
- High memory usage
- System becomes unresponsive

**Causes**:
- Large OpenAPI specifications
- Complex templates
- Many overlays
- Inefficient operations

**Solutions**:

1. **Optimize overlays**:
```yaml
# ❌ Multiple small updates
- target: "$.info.title"
  update: "New Title"
- target: "$.info.description"
  update: "New Description"
- target: "$.info.version"
  update: "2.0.0"

# ✅ Single update
- target: "$.info"
  update:
    title: "New Title"
    description: "New Description"
    version: "2.0.0"
```

2. **Use specific targeting**:
```yaml
# ❌ Broad targeting
- target: "$.paths.*.*"
  update: {...}

# ✅ Specific targeting
- target: "$.paths./users.get"
  update: {...}
```

3. **Profile and monitor**:
```bash
# Enable verbose output
oas-patcher apply --verbose

# Monitor system resources
top -p $(pgrep oas-patcher)

# Use profiling tools
python -m cProfile oas-patcher apply ...
```

### Memory Issues

**Error**: `MemoryError: Unable to allocate memory`

**Causes**:
- Very large specifications
- Memory leaks in templates
- Inefficient data structures

**Solutions**:

1. **Process in chunks**:
```bash
# Split large specifications
oas-patcher split --input large-spec.yaml --output chunks/

# Process chunks separately
for chunk in chunks/*.yaml; do
  oas-patcher apply --input "$chunk" --overlay overlay.yaml
done
```

2. **Use streaming mode**:
```bash
# Enable streaming for large files
oas-patcher apply --stream --input large-spec.yaml
```

3. **Increase memory limits**:
```bash
# Set memory limits
export PYTHONMAXMEMORY=4G
oas-patcher apply ...
```

## Validation Issues

### Schema Validation Failures

**Error**: `Schema validation failed: ...`

**Causes**:
- Invalid OpenAPI structure
- Missing required fields
- Type violations
- Constraint violations

**Solutions**:

1. **Validate incrementally**:
```bash
# Validate base specification
oas-patcher validate input.yaml

# Validate after each overlay
oas-patcher apply --overlay overlay1.yaml --validate
oas-patcher apply --overlay overlay2.yaml --validate
```

2. **Fix common validation errors**:
```yaml
# ❌ Missing required fields
paths:
  /users:
    get:
      # Missing responses
      summary: "Get users"

# ✅ Complete operation
paths:
  /users:
    get:
      summary: "Get users"
      responses:
        "200":
          description: "List of users"
```

3. **Use schema debugging**:
```bash
# Get detailed validation errors
oas-patcher validate --verbose input.yaml

# Check specific sections
oas-patcher validate --section paths input.yaml
```

## Integration Issues

### CI/CD Pipeline Failures

**Common scenarios**:

1. **Environment variables not set**:
```yaml
# ❌ In CI pipeline
steps:
  - name: Generate spec
    run: oas-patcher apply --overlay overlay.yaml

# ✅ With environment
steps:
  - name: Generate spec
    env:
      API_URL: ${{ secrets.API_URL }}
      API_VERSION: ${{ github.ref_name }}
    run: oas-patcher apply --overlay overlay.yaml
```

2. **File path issues**:
```bash
# ❌ Relative paths in different working directory
oas-patcher apply --input ../specs/input.yaml

# ✅ Use absolute paths or proper working directory
cd specs && oas-patcher apply --input input.yaml
```

3. **Permission issues**:
```bash
# Set proper permissions in CI
chmod +x scripts/generate-specs.sh
```

### Version Compatibility

**Error**: `Unsupported OpenAPI version`

**Causes**:
- Using OpenAPI 2.0 (Swagger)
- Unsupported specification version
- Version mismatch

**Solutions**:

1. **Convert specifications**:
```bash
# Convert Swagger 2.0 to OpenAPI 3.0
swagger-codegen convert --input-spec swagger.yaml --output-spec openapi.yaml
```

2. **Check version support**:
```bash
# Check supported versions
oas-patcher --help | grep -i version
```

## Getting Help

### Enable Debug Mode

```bash
# Maximum verbosity
oas-patcher apply --verbose --debug

# Log to file
oas-patcher apply --verbose 2> debug.log
```

### Collect Information

When reporting issues, include:

1. **Version information**:
```bash
oas-patcher --version
python --version
pip list | grep -E "(oas-patcher|yaml|json)"
```

2. **Minimal reproduction case**:
```yaml
# Minimal input.yaml
openapi: 3.0.3
info:
  title: Test API
  version: 1.0.0
paths: {}

# Minimal overlay.yaml
overlay: 1.0.0
info:
  title: Test Overlay
  version: 1.0.0
actions:
  - target: "$.info.title"
    update: "Updated Title"
```

3. **Command and output**:
```bash
# Exact command used
oas-patcher apply --input input.yaml --overlay overlay.yaml --output output.yaml

# Full error output
[Include complete error message and stack trace]
```

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share tips
- **Documentation**: Check the latest documentation
- **Examples**: Review example repositories
- **Stack Overflow**: Search for existing solutions

### Professional Support

For enterprise usage:
- Consider professional support options
- Engage with OAS Patcher maintainers
- Contribute back improvements
- Sponsor development efforts
