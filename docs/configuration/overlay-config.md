# Overlay Configuration

This guide covers the structure and configuration of overlay files in OAS Patcher. Overlays define the modifications to be applied to OpenAPI specifications.

## Basic Structure

Every overlay file follows the OpenAPI Overlay specification v1.0 and must include these required sections:

```yaml
overlay: 1.0.0
info:
  title: My Overlay
  version: 1.0.0
  description: Description of what this overlay does
actions:
  - target: "$.info.title"
    update: "Updated API Title"
```

## Required Fields

### `overlay`
- **Type**: `string`
- **Pattern**: `^1\.0\.\d+$`
- **Description**: Specifies the overlay specification version
- **Example**: `1.0.0`

### `info`
- **Type**: `object`
- **Description**: Metadata about the overlay
- **Required fields**:
  - `title` (string): Name of the overlay
  - `version` (string): Version of the overlay
- **Optional fields**:
  - `description` (string): Description of the overlay's purpose

### `actions`
- **Type**: `array`
- **Description**: List of modifications to apply
- **Minimum items**: 1
- **Unique items**: true

## Action Objects

Each action in the `actions` array defines a specific modification:

### Required Fields

#### `target`
- **Type**: `string`
- **Pattern**: `^\$`
- **Description**: JSONPath expression pointing to the element to modify
- **Examples**:
  - `$.info.title` - Target the API title
  - `$.paths./users.get` - Target the GET /users operation
  - `$.components.schemas.User` - Target the User schema

### Optional Fields

#### `description`
- **Type**: `string`
- **Description**: Human-readable description of what this action does
- **Example**: `"Add API key authentication to all endpoints"`

#### `update`
- **Type**: `string | boolean | object | array | number | null`
- **Description**: New value to set at the target location
- **Behavior**: Replaces the existing value or creates a new one

#### `remove`
- **Type**: `boolean`
- **Default**: `false`
- **Description**: Whether to remove the target element
- **Note**: Cannot be used with `update`

## Action Types

### Update Actions

Replace or create values at the target location:

```yaml
actions:
  # Update a simple string value
  - target: "$.info.title"
    update: "My Updated API"
    description: "Update the API title"
  
  # Update an object
  - target: "$.info.contact"
    update:
      name: "API Support"
      email: "support@example.com"
      url: "https://example.com/support"
  
  # Add new paths
  - target: "$.paths./health"
    update:
      get:
        summary: "Health check endpoint"
        responses:
          "200":
            description: "Service is healthy"
```

### Remove Actions

Delete elements from the specification:

```yaml
actions:
  # Remove a field
  - target: "$.info.license"
    remove: true
    description: "Remove license information"
  
  # Remove an entire path
  - target: "$.paths./deprecated-endpoint"
    remove: true
    description: "Remove deprecated endpoint"
  
  # Remove a schema
  - target: "$.components.schemas.LegacyModel"
    remove: true
```

## Complex Targeting

### Path Operations

Target specific HTTP operations:

```yaml
actions:
  # Target a specific operation
  - target: "$.paths./users/{id}.get"
    update:
      summary: "Get user by ID (updated)"
  
  # Target all operations on a path
  - target: "$.paths./users"
    update:
      description: "User management endpoints"
```

### Schema Modifications

Modify component schemas:

```yaml
actions:
  # Add a new property to a schema
  - target: "$.components.schemas.User.properties.email"
    update:
      type: "string"
      format: "email"
      description: "User's email address"
  
  # Update schema validation
  - target: "$.components.schemas.User.required"
    update:
      - "id"
      - "name"
      - "email"
```

### Security Schemes

Add or modify security configurations:

```yaml
actions:
  # Add API key security scheme
  - target: "$.components.securitySchemes.ApiKeyAuth"
    update:
      type: "apiKey"
      in: "header"
      name: "X-API-Key"
  
  # Apply security globally
  - target: "$.security"
    update:
      - ApiKeyAuth: []
```

## Environment-Specific Overlays

Use templating for environment-specific configurations:

```yaml
overlay: 1.0.0
info:
  title: Environment Overlay
  version: 1.0.0
actions:
  # Update server URL based on environment
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}"
    description: "Set environment-specific server URL"
  
  # Add environment-specific contact info
  - target: "$.info.contact.email"
    update: "{{ CONTACT_EMAIL }}"
```

## Conditional Logic

While not directly supported in the overlay format, you can create environment-specific overlay files:

```
overlays/
├── base.yaml           # Common changes
├── dev.yaml           # Development-specific
├── staging.yaml       # Staging-specific
└── production.yaml    # Production-specific
```

## Validation Rules

### Target Path Validation
- Must start with `$`
- Must be a valid JSONPath expression
- Should point to an existing or creatable location

### Action Validation
- Cannot have both `update` and `remove` in the same action
- `remove` must be boolean if present
- `target` is always required

### Value Type Validation
- `update` values must be valid YAML/JSON types
- Object merging follows JSON Merge Patch rules
- Arrays are replaced entirely, not merged

## Best Practices

### Organization
```yaml
overlay: 1.0.0
info:
  title: "Security Enhancement Overlay"
  version: "1.2.0"
  description: "Adds authentication and rate limiting"

actions:
  # Group related actions with descriptions
  - target: "$.components.securitySchemes"
    description: "Add security schemes"
    update:
      BearerAuth:
        type: "http"
        scheme: "bearer"
        bearerFormat: "JWT"
  
  - target: "$.security"
    description: "Apply security globally"
    update:
      - BearerAuth: []
```

### Error Prevention
- Always include descriptions for complex actions
- Test overlays on sample specifications first
- Use specific targets to avoid unintended modifications
- Validate overlay files before use

### Performance
- Keep overlays focused and minimal
- Use multiple small overlays instead of one large overlay
- Order actions from least to most specific

## Common Patterns

### API Versioning
```yaml
actions:
  - target: "$.info.version"
    update: "{{ API_VERSION }}"
  
  - target: "$.servers[0].url"
    update: "{{ BASE_URL }}/v{{ MAJOR_VERSION }}"
```

### Adding Authentication
```yaml
actions:
  - target: "$.components.securitySchemes.oauth2"
    update:
      type: "oauth2"
      flows:
        authorizationCode:
          authorizationUrl: "{{ AUTH_URL }}/oauth/authorize"
          tokenUrl: "{{ AUTH_URL }}/oauth/token"
          scopes:
            read: "Read access"
            write: "Write access"
```

### Response Enhancement
```yaml
actions:
  - target: "$.paths./users.get.responses.200.headers"
    update:
      X-Total-Count:
        schema:
          type: "integer"
        description: "Total number of users"
```

## Troubleshooting

### Common Issues

1. **Invalid Target Path**
   ```
   Error: Invalid JSONPath expression
   ```
   - Ensure the path starts with `$`
   - Check for proper escaping of special characters
   - Validate the path exists in the target specification

2. **Action Conflicts**
   ```
   Error: Cannot use both 'update' and 'remove'
   ```
   - Use only one action type per action object
   - Split into multiple actions if needed

3. **Type Mismatches**
   ```
   Error: Cannot update array with object
   ```
   - Ensure update values match the expected type
   - Use proper YAML formatting for complex objects

### Debugging Tips
- Use `oas-patcher validate` to check overlay syntax
- Test with minimal overlay files first
- Check the generated output for unexpected changes
- Use verbose mode for detailed processing information
