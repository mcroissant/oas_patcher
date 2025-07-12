# API Versioning

Learn how to manage multiple API versions using OAS Patcher overlays and environment configuration.

## Scenario

You need to maintain multiple versions of your API (v1, v2, v3) with different features and endpoints while keeping a single source specification.

## Problem

- Manual maintenance of multiple OpenAPI files is error-prone
- Common elements are duplicated across versions
- Version-specific changes are scattered and hard to track
- Deployment complexity increases with each version

## Solution

Use OAS Patcher to maintain a base specification and apply version-specific overlays.

## File Structure

```
api-versioning/
├── base/
│   └── openapi.yaml         # Base API specification
├── overlays/
│   ├── v1/
│   │   └── version.yaml     # V1-specific changes
│   ├── v2/
│   │   ├── version.yaml     # V2 base changes
│   │   └── new-features.yaml # V2 new features
│   └── v3/
│       ├── version.yaml     # V3 base changes
│       ├── breaking-changes.yaml # V3 breaking changes
│       └── new-endpoints.yaml # V3 new endpoints
├── bundle.yml               # Bundle configuration
└── .env.example            # Environment variables template
```

## Base Specification

**base/openapi.yaml**
```yaml
openapi: 3.0.3
info:
  title: "My API"
  version: "1.0.0"
  description: "A sample API for demonstration"
  contact:
    name: "API Support"
    email: "support@example.com"

servers:
  - url: "https://api.example.com"
    description: "Production server"

paths:
  /users:
    get:
      summary: "List users"
      operationId: "listUsers"
      responses:
        "200":
          description: "List of users"
          content:
            application/json:
              schema:
                type: "array"
                items:
                  $ref: "#/components/schemas/User"
    
    post:
      summary: "Create user"
      operationId: "createUser"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateUserRequest"
      responses:
        "201":
          description: "User created"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"

  /users/{id}:
    parameters:
      - name: "id"
        in: "path"
        required: true
        schema:
          type: "integer"
    
    get:
      summary: "Get user by ID"
      operationId: "getUserById"
      responses:
        "200":
          description: "User details"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
        "404":
          description: "User not found"

components:
  schemas:
    User:
      type: "object"
      properties:
        id:
          type: "integer"
        name:
          type: "string"
        email:
          type: "string"
          format: "email"
      required: ["id", "name", "email"]
    
    CreateUserRequest:
      type: "object"
      properties:
        name:
          type: "string"
        email:
          type: "string"
          format: "email"
      required: ["name", "email"]
```

## Version-Specific Overlays

### V1 Overlay

**overlays/v1/version.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V1 Version Configuration"
  version: "1.0.0"
  description: "Configures API for version 1"

actions:
  # Set version number
  - target: "$.info.version"
    update: "1.0.0"
    description: "Set API version to 1.0.0"
  
  # Set versioned server URL
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}/v1"
    description: "Set v1 server URL"
  
  # Add version info to description
  - target: "$.info.description"
    update: "A sample API for demonstration (Version 1)"
    description: "Update description for v1"
```

### V2 Overlay

**overlays/v2/version.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V2 Version Configuration"
  version: "1.0.0"
  description: "Configures API for version 2"

actions:
  # Set version number
  - target: "$.info.version"
    update: "2.0.0"
    description: "Set API version to 2.0.0"
  
  # Set versioned server URL
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}/v2"
    description: "Set v2 server URL"
  
  # Update description
  - target: "$.info.description"
    update: "A sample API for demonstration (Version 2 - Enhanced)"
    description: "Update description for v2"
```

**overlays/v2/new-features.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V2 New Features"
  version: "1.0.0"
  description: "Adds new features available in V2"

actions:
  # Add pagination support
  - target: "$.paths./users.get.parameters"
    update:
      - name: "page"
        in: "query"
        required: false
        schema:
          type: "integer"
          minimum: 1
          default: 1
        description: "Page number for pagination"
      
      - name: "limit"
        in: "query"
        required: false
        schema:
          type: "integer"
          minimum: 1
          maximum: 100
          default: 20
        description: "Number of items per page"
    description: "Add pagination parameters to user listing"
  
  # Enhanced user schema with additional fields
  - target: "$.components.schemas.User.properties.createdAt"
    update:
      type: "string"
      format: "date-time"
      description: "User creation timestamp"
    description: "Add createdAt field to User schema"
  
  - target: "$.components.schemas.User.properties.status"
    update:
      type: "string"
      enum: ["active", "inactive", "pending"]
      description: "User account status"
    description: "Add status field to User schema"
  
  # Add bulk operations endpoint
  - target: "$.paths./users/bulk"
    update:
      post:
        summary: "Bulk create users"
        operationId: "bulkCreateUsers"
        requestBody:
          content:
            application/json:
              schema:
                type: "array"
                items:
                  $ref: "#/components/schemas/CreateUserRequest"
        responses:
          "201":
            description: "Users created"
            content:
              application/json:
                schema:
                  type: "object"
                  properties:
                    created:
                      type: "array"
                      items:
                        $ref: "#/components/schemas/User"
                    errors:
                      type: "array"
                      items:
                        type: "object"
                        properties:
                          index:
                            type: "integer"
                          error:
                            type: "string"
    description: "Add bulk operations endpoint"
```

### V3 Overlay

**overlays/v3/version.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V3 Version Configuration"
  version: "1.0.0"
  description: "Configures API for version 3"

actions:
  # Set version number
  - target: "$.info.version"
    update: "3.0.0"
    description: "Set API version to 3.0.0"
  
  # Set versioned server URL
  - target: "$.servers[0].url"
    update: "{{ API_BASE_URL }}/v3"
    description: "Set v3 server URL"
  
  # Update description
  - target: "$.info.description"
    update: "A sample API for demonstration (Version 3 - Latest)"
    description: "Update description for v3"
```

**overlays/v3/breaking-changes.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V3 Breaking Changes"
  version: "1.0.0"
  description: "Implements breaking changes for V3"

actions:
  # Remove deprecated email field, replace with contacts array
  - target: "$.components.schemas.User.properties.email"
    remove: true
    description: "Remove deprecated email field"
  
  - target: "$.components.schemas.User.properties.contacts"
    update:
      type: "array"
      items:
        type: "object"
        properties:
          type:
            type: "string"
            enum: ["email", "phone", "sms"]
          value:
            type: "string"
          primary:
            type: "boolean"
            default: false
        required: ["type", "value"]
      description: "Array of contact methods"
    description: "Add contacts array to replace email field"
  
  # Update required fields
  - target: "$.components.schemas.User.required"
    update: ["id", "name", "contacts"]
    description: "Update required fields for v3"
  
  # Update CreateUserRequest schema
  - target: "$.components.schemas.CreateUserRequest.properties.email"
    remove: true
    description: "Remove email from create request"
  
  - target: "$.components.schemas.CreateUserRequest.properties.contacts"
    update:
      type: "array"
      items:
        type: "object"
        properties:
          type:
            type: "string"
            enum: ["email", "phone", "sms"]
          value:
            type: "string"
          primary:
            type: "boolean"
            default: false
        required: ["type", "value"]
      minItems: 1
      description: "At least one contact method required"
    description: "Add contacts to create request"
  
  - target: "$.components.schemas.CreateUserRequest.required"
    update: ["name", "contacts"]
    description: "Update required fields for create request"
```

**overlays/v3/new-endpoints.yaml**
```yaml
overlay: 1.0.0
info:
  title: "V3 New Endpoints"
  version: "1.0.0"
  description: "Adds new endpoints available in V3"

actions:
  # Add user preferences endpoint
  - target: "$.paths./users/{id}/preferences"
    update:
      parameters:
        - name: "id"
          in: "path"
          required: true
          schema:
            type: "integer"
      
      get:
        summary: "Get user preferences"
        operationId: "getUserPreferences"
        responses:
          "200":
            description: "User preferences"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/UserPreferences"
      
      put:
        summary: "Update user preferences"
        operationId: "updateUserPreferences"
        requestBody:
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/UserPreferences"
        responses:
          "200":
            description: "Preferences updated"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/UserPreferences"
    description: "Add user preferences endpoint"
  
  # Add analytics endpoint
  - target: "$.paths./analytics/users"
    update:
      get:
        summary: "Get user analytics"
        operationId: "getUserAnalytics"
        parameters:
          - name: "from"
            in: "query"
            required: false
            schema:
              type: "string"
              format: "date"
          - name: "to"
            in: "query"
            required: false
            schema:
              type: "string"
              format: "date"
        responses:
          "200":
            description: "User analytics data"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/Analytics"
    description: "Add analytics endpoint"
  
  # Add new schemas
  - target: "$.components.schemas.UserPreferences"
    update:
      type: "object"
      properties:
        theme:
          type: "string"
          enum: ["light", "dark", "auto"]
          default: "auto"
        language:
          type: "string"
          default: "en"
        notifications:
          type: "object"
          properties:
            email:
              type: "boolean"
              default: true
            push:
              type: "boolean"
              default: true
            sms:
              type: "boolean"
              default: false
    description: "Add UserPreferences schema"
  
  - target: "$.components.schemas.Analytics"
    update:
      type: "object"
      properties:
        totalUsers:
          type: "integer"
        activeUsers:
          type: "integer"
        newUsers:
          type: "integer"
        period:
          type: "object"
          properties:
            from:
              type: "string"
              format: "date"
            to:
              type: "string"
              format: "date"
    description: "Add Analytics schema"
```

## Bundle Configuration

**bundle.yml**
```yaml
name: "Multi-Version API Bundle"
version: "1.0.0"
description: "Manages multiple API versions from a single source"

input: "base/openapi.yaml"

environments:
  v1:
    description: "API Version 1 - Stable"
    variables:
      API_BASE_URL: "{{ BASE_URL | default('https://api.example.com') }}"
      API_VERSION: "v1"
    overlays:
      - "overlays/v1/version.yaml"
  
  v2:
    description: "API Version 2 - Enhanced"
    variables:
      API_BASE_URL: "{{ BASE_URL | default('https://api.example.com') }}"
      API_VERSION: "v2"
    overlays:
      - "overlays/v2/version.yaml"
      - "overlays/v2/new-features.yaml"
  
  v3:
    description: "API Version 3 - Latest"
    variables:
      API_BASE_URL: "{{ BASE_URL | default('https://api.example.com') }}"
      API_VERSION: "v3"
    overlays:
      - "overlays/v3/version.yaml"
      - "overlays/v3/breaking-changes.yaml"
      - "overlays/v3/new-endpoints.yaml"

# Global variables available to all environments
variables:
  CONTACT_EMAIL: "support@example.com"
  SUPPORT_URL: "https://support.example.com"
```

## Environment Variables

**.env.example**
```bash
# Base configuration
BASE_URL=https://api.example.com
CONTACT_EMAIL=support@example.com
SUPPORT_URL=https://support.example.com

# Environment-specific (set in deployment)
ENVIRONMENT=production
DEBUG_MODE=false
```

## Usage

### Generate Individual Versions

```bash
# Generate V1 specification
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment v1 \
  --output openapi-v1.yaml

# Generate V2 specification
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment v2 \
  --output openapi-v2.yaml

# Generate V3 specification
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment v3 \
  --output openapi-v3.yaml
```

### Generate All Versions

```bash
# Generate all versions at once
for version in v1 v2 v3; do
  oas-patcher bundle apply \
    --bundle bundle.yml \
    --environment $version \
    --output "openapi-$version.yaml"
done
```

### With Custom Server URL

```bash
# Use custom server URL
BASE_URL=https://staging-api.example.com \
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment v2 \
  --output staging-openapi-v2.yaml
```

## Expected Output Differences

### V1 Features
- Basic CRUD operations
- Simple user schema (id, name, email)
- Standard error responses

### V2 Enhancements
- Pagination support
- Extended user schema (createdAt, status)
- Bulk operations
- Maintains backward compatibility

### V3 Breaking Changes
- Contacts array replaces email field
- New user preferences endpoint
- Analytics endpoint
- Enhanced schemas

## Best Practices

### 1. Organize by Feature
```
overlays/
├── common/          # Shared across versions
├── v1/             # V1-specific
├── v2/             # V2-specific
└── v3/             # V3-specific
```

### 2. Use Semantic Versioning
```yaml
info:
  version: "1.2.3"    # Major.Minor.Patch
```

### 3. Document Breaking Changes
```yaml
# Always describe breaking changes
- target: "$.components.schemas.User.properties.email"
  remove: true
  description: "BREAKING: Removed email field, use contacts array"
```

### 4. Maintain Compatibility
```yaml
# Keep old fields for transition periods
- target: "$.components.schemas.User.properties.email"
  update:
    type: "string"
    format: "email"
    deprecated: true
    description: "DEPRECATED: Use contacts array instead"
```

### 5. Version-Specific Documentation
```yaml
- target: "$.info.description"
  update: |
    My API Version {{ API_VERSION }}
    
    {% if API_VERSION == 'v1' %}
    This is the stable version with core functionality.
    {% elif API_VERSION == 'v2' %}
    Enhanced version with pagination and bulk operations.
    {% elif API_VERSION == 'v3' %}
    Latest version with breaking changes and new features.
    {% endif %}
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Generate API Versions

on:
  push:
    branches: [main]
    paths: ['api/**']

jobs:
  generate-specs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        version: [v1, v2, v3]
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install OAS Patcher
        run: pip install oas-patcher
      
      - name: Generate ${{ matrix.version }} specification
        run: |
          oas-patcher bundle apply \
            --bundle bundle.yml \
            --environment ${{ matrix.version }} \
            --output "dist/openapi-${{ matrix.version }}.yaml"
      
      - name: Validate specification
        run: |
          oas-patcher validate "dist/openapi-${{ matrix.version }}.yaml"
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: "openapi-${{ matrix.version }}"
          path: "dist/openapi-${{ matrix.version }}.yaml"
```

## Troubleshooting

### Common Issues

1. **Version Conflicts**
   ```bash
   # Check what overlays are applied
   oas-patcher bundle show --bundle bundle.yml --environment v2
   ```

2. **Schema Validation Errors**
   ```bash
   # Validate each step
   oas-patcher validate base/openapi.yaml
   oas-patcher validate output.yaml
   ```

3. **Template Resolution Issues**
   ```bash
   # Debug variable resolution
   oas-patcher bundle variables --bundle bundle.yml --environment v2
   ```

### Debugging Tips

- Use `--dry-run` to see changes without applying them
- Validate base specification before applying overlays
- Test overlays individually before combining them
- Use descriptive overlay names and descriptions
