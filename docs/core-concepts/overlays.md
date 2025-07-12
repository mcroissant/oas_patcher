# OpenAPI Overlays

OpenAPI Overlays are a powerful way to modify existing OpenAPI specifications without directly editing the original files. The OAS Patcher tool implements the [OpenAPI Overlay Specification](https://github.com/OAI/Overlay-Specification) to provide a standardized approach to API specification modifications.

## What are Overlays?

An overlay is a document that describes modifications to be applied to an OpenAPI specification. Instead of maintaining multiple versions of your API documentation or making manual edits, overlays allow you to:

- Add, modify, or remove elements from your OpenAPI specification
- Keep your modifications separate from the original specification
- Apply different modifications for different environments or use cases
- Maintain a clean audit trail of changes

## Basic Overlay Structure

An overlay document follows this basic structure:

```yaml
overlay: 1.0.0
info:
  title: My API Overlay
  version: 1.0.0
actions:
  - target: "$.info.version"
    update: "2.0.0"
  - target: "$.paths./users.get.summary"
    update: "Retrieve all users"
```

## Key Components

### Overlay Header

Every overlay must include:
- `overlay`: The overlay specification version (currently "1.0.0")
- `info`: Metadata about the overlay including title and version

### Actions

Actions define the specific modifications to apply. Each action includes:
- `target`: A JSONPath expression pointing to the element to modify
- Operation: One of `update`, `remove`, or other operations

## Action Types

### Update Action

Modifies the value at the specified target:

```yaml
actions:
  - target: "$.info.description"
    update: "Updated API description"
```

### Remove Action

Removes the element at the specified target:

```yaml
actions:
  - target: "$.paths./deprecated-endpoint"
    remove: true
```

### Complex Updates

You can update complex objects and arrays:

```yaml
actions:
  - target: "$.components.securitySchemes"
    update:
      BearerAuth:
        type: http
        scheme: bearer
        bearerFormat: JWT
```

## JSONPath Targeting

Overlays use JSONPath expressions to target specific parts of the OpenAPI document:

- `$.info.version` - Targets the version field in the info object
- `$.paths./users.get` - Targets the GET operation on the /users path
- `$.components.schemas.User.properties.email` - Targets a specific schema property

## Common Use Cases

### Version Updates

```yaml
actions:
  - target: "$.info.version"
    update: "2.1.0"
```

### Adding Security

```yaml
actions:
  - target: "$.components.securitySchemes.ApiKeyAuth"
    update:
      type: apiKey
      in: header
      name: X-API-Key
  - target: "$.security"
    update:
      - ApiKeyAuth: []
```

### Environment-Specific URLs

```yaml
actions:
  - target: "$.servers"
    update:
      - url: "https://staging-api.example.com"
        description: "Staging server"
```

### Adding Response Examples

```yaml
actions:
  - target: "$.paths./users.get.responses.200.content.application/json.example"
    update:
      users:
        - id: 1
          name: "John Doe"
          email: "john@example.com"
```

## Best Practices

### 1. Descriptive Overlay Names

Use clear, descriptive names for your overlays:

```yaml
info:
  title: "Production Environment Configuration"
  description: "Applies production-specific settings including HTTPS URLs and security requirements"
```

### 2. Atomic Changes

Keep each overlay focused on a specific type of change:
- Separate overlays for version updates, security changes, and environment configuration
- Avoid mixing unrelated modifications in a single overlay

### 3. Documentation

Always include descriptions for your actions:

```yaml
actions:
  - target: "$.info.version"
    update: "2.0.0"
    description: "Bump version for new major release"
```

### 4. Target Validation

Ensure your JSONPath targets are correct:
- Test overlays against sample OpenAPI documents
- Use the validation command to check overlay syntax
- Verify targets exist in your OpenAPI specification

## Working with Arrays

When working with arrays, be specific about targeting:

```yaml
# Add a new server to the existing servers array
actions:
  - target: "$.servers[1]"
    update:
      url: "https://api-v2.example.com"
      description: "Version 2 API"
```

## Error Handling

Common overlay errors include:
- Invalid JSONPath expressions
- Targeting non-existent paths
- Type mismatches in update values

Use the validate command to check your overlays:

```bash
oas-patch validate my-overlay.yaml
```

## Next Steps

- Learn about [Bundle Management](bundles.md) for organizing multiple overlays
- Explore [Template Engine](templates.md) for dynamic overlay content
- See [Environment Variables](environment-variables.md) for environment-specific configurations
