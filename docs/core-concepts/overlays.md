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
overlay: 1.1.0  # Use 1.1.0 for latest features, or 1.0.0 for compatibility
info:
  title: My API Overlay
  version: 1.0.0
  description: Optional description of what this overlay does
actions:
  - target: "$.info.version"
    update: "2.0.0"
  - target: "$.paths.['/users'].get.summary"
    update: "Retrieve all users"
```

## Key Components

### Overlay Header

Every overlay must include:
- `overlay`: The overlay specification version (use "1.1.0" for latest features, or "1.0.0" for compatibility)
- `info`: Metadata about the overlay including title and version
  - `title`: (required) A descriptive title for the overlay
  - `version`: (required) The overlay version
  - `description`: (optional, Overlay 1.1+) A detailed description of the overlay's purpose

### Actions

Actions define the specific modifications to apply. Each action includes:
- `target`: A JSONPath expression pointing to the element to modify
- `description`: (optional) A description of what this action does
- Operation: One of `update`, `remove`, or `copy` (Overlay 1.1+)

## Overlay Specification Versions

OAS Patcher supports both Overlay 1.0 and 1.1:

- **Overlay 1.0.x**: The original specification with `update` and `remove` actions
- **Overlay 1.1.x**: Enhanced specification with the new `copy` action and `info.description` field

All 1.0.x overlays continue to work without modification. Use 1.1.0 to access new features.

## Action Types

### Update Action

Modifies the value at the specified target:

```yaml
actions:
  - target: "$.info.description"
    update: "Updated API description"
```

### Copy Action (Overlay 1.1+)

The copy action is a powerful feature introduced in Overlay 1.1 that allows you to duplicate content from one location in your OpenAPI document to another. This is particularly useful for:

- Creating schema variations (e.g., AdminUser based on User)
- Replicating response structures
- Duplicating path operations with modifications

**Key Features:**
- Automatically creates the target if it doesn't exist
- Deep copies the source to avoid reference issues
- Supports both bracket notation (`['key']`) and dot notation (`.key`)

**Basic Example:**

```yaml
overlay: 1.1.0
info:
  title: Copy Schema Example
  version: 1.0.0
actions:
  # Copy the User schema to create an Admin schema
  - target: "$.components.schemas.Admin"
    copy: "$.components.schemas.User"
    description: "Create Admin schema based on User"
```

**Before (source document):**
```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

**After applying the overlay:**
```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
    Admin:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

**Advanced Copy Examples:**

```yaml
# Copy and then modify
actions:
  # Step 1: Copy the schema
  - target: "$.components.schemas.AdminUser"
    copy: "$.components.schemas.User"
  
  # Step 2: Add admin-specific fields
  - target: "$.components.schemas.AdminUser.properties"
    update:
      permissions:
        type: array
        items:
          type: string
      isAdmin:
        type: boolean
        default: true

# Copy response structures
actions:
  - target: "$.paths['/admin/users'].get.responses"
    copy: "$.paths['/users'].get.responses"
    description: "Reuse the same response structure"

# Copy security schemes
actions:
  - target: "$.components.securitySchemes.AdminAuth"
    copy: "$.components.securitySchemes.UserAuth"
```

**When to Use Copy vs Update:**

- Use **copy** when you want to duplicate an entire structure
- Use **update** when you want to modify or merge values
- Combine both for powerful schema generation workflows

### Remove Action

Removes the element at the specified target:

```yaml
actions:
  - target: "$.paths.['/deprecated-endpoint']"
    remove: true
```

### Complex Updates

You can update complex objects and arrays:

```yaml
actions:
  - target: "$"
    update:
      components:
        securitySchemes:
          BearerAuth:
            type: http
            scheme: bearer
            bearerFormat: JWT
```

## JSONPath Targeting

Overlays use JSONPath expressions to target specific parts of the OpenAPI document:

- `$.info.version` - Targets the version field in the info object
- `$.paths.['/users'].get` - Targets the GET operation on the /users path
- `$.components.schemas.User.properties.email` - Targets a specific schema property

## Common Use Cases

### Creating Schema Variations with Copy (Overlay 1.1+)

One of the most powerful uses of the copy action is creating schema variations:

```yaml
overlay: 1.1.0
info:
  title: Create User Role Schemas
  version: 1.0.0
actions:
  # Create multiple user types from a base User schema
  - target: "$.components.schemas.AdminUser"
    copy: "$.components.schemas.User"
  
  - target: "$.components.schemas.GuestUser"
    copy: "$.components.schemas.User"
  
  # Now customize each
  - target: "$.components.schemas.AdminUser.properties"
    update:
      adminLevel:
        type: integer
        minimum: 1
        maximum: 5
  
  - target: "$.components.schemas.GuestUser.properties"
    update:
      accessExpiry:
        type: string
        format: date-time
```

### Version Updates

```yaml
actions:
  - target: "$.info.version"
    update: "2.1.0"
```

### Adding Security

```yaml
actions:
  - target: "$"
    update:
      components:
        securitySchemes:
          ApiKeyAuth:
            type: apiKey
            in: header
            name: X-API-Key
  - target: "$.paths.['/users'].get"
    update:
      security:
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


## Working with Arrays

If the array exists you can simply call update action to add a value :

```yaml
# Add a new server to the existing servers array
actions:
  - target: "$.servers"
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
