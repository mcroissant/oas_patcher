# Quick Start

Get started with OAS Patcher in just 5 minutes! This guide will walk you through applying your first overlay to an OpenAPI specification.

## What You'll Learn

By the end of this guide, you'll know how to:
- Apply overlays to OpenAPI documents
- Use the CLI effectively
- Understand basic overlay structure

## Step 1: Prepare Sample Files

Let's start with a simple OpenAPI specification and an overlay.

### Create `petstore.yaml`

Create a basic OpenAPI specification:

```yaml
openapi: 3.0.3
info:
  title: Pet Store API
  version: 1.0.0
  description: A simple pet store API
servers:
  - url: http://localhost:8080
    description: Development server
paths:
  /pets:
    get:
      summary: List all pets
      responses:
        '200':
          description: A list of pets
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    status:
                      type: string
                      enum: [available, pending, sold]
```

### Create `production-overlay.yaml`

Create an overlay that modifies the API for production:

```yaml
overlay: 1.0.0
info:
  title: Production Configuration Overlay
  version: 1.0.0
actions:
  # Replace development server with production server
  - target: "$.servers"
    remove: true
  - target: "$"
    update:
      servers:
        - url: https://api.petstore.com
          description: Production server
        - url: https://api-backup.petstore.com
          description: Backup production server
  
  # Update API info for production
  - target: "$.info"
    update:
      description: "Pet Store API - Production Environment"
      version: "1.1.0"
      contact:
        name: API Support
        url: https://petstore.com/support
        email: api-support@petstore.com
  
  # Add security scheme
  - target: "$.components"
    remove: true
  - target: "$"
    update:
      components:
        securitySchemes:
          ApiKeyAuth:
            type: apiKey
            in: header
            name: X-API-Key
            description: API key for production access
  
  # Add security requirement to the GET /pets endpoint
  - target: "$.paths./pets.get"
    update:
      security:
        - ApiKeyAuth: []
```

## Step 2: Apply the Overlay

Now let's apply the overlay to transform your API specification:

```bash
oas-patch overlay petstore.yaml production-overlay.yaml -o petstore-production.yaml
```

### What This Command Does

- `overlay` - The command to apply an overlay
- `petstore.yaml` - Source OpenAPI specification
- `production-overlay.yaml` - Overlay file with modifications
- `-o petstore-production.yaml` - Output file for the result

## Step 3: Examine the Results

Open `petstore-production.yaml` to see the transformed API:

```yaml
openapi: 3.0.3
info:
  title: Pet Store API
  version: 1.1.0
  description: Pet Store API - Production Environment
  contact:
    name: API Support
    url: https://petstore.com/support
    email: api-support@petstore.com
servers:
  - url: https://api.petstore.com
    description: Production server
  - url: https://api-backup.petstore.com
    description: Backup production server
paths:
  /pets:
    get:
      summary: List all pets
      security:
        - ApiKeyAuth: []
      responses:
        '200':
          description: A list of pets
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
                    status:
                      type: string
                      enum: [available, pending, sold]
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for production access
```

### Key Changes Applied

✅ **Servers Updated**: Development server replaced with production servers  
✅ **API Info Enhanced**: Version, description, and contact information added  
✅ **Security Added**: API key authentication scheme and requirement added  
✅ **Structure Preserved**: All original endpoints and schemas maintained  

## Step 4: Validate the Result

Verify that your overlay was applied correctly:

```bash
# Validate the original overlay file
oas-patch validate production-overlay.yaml

# Check if the result is valid OpenAPI
oas-patch validate petstore-production.yaml --format yaml
```

## Common CLI Commands

Here are the most frequently used commands:

### Apply Overlays
```bash
# Basic overlay application
oas-patch overlay api.yaml overlay.yaml -o result.yaml

# Apply and output to stdout
oas-patch overlay api.yaml overlay.yaml

# Apply with sanitization (remove special characters)
oas-patch overlay api.yaml overlay.yaml --sanitize -o clean-result.yaml
```

### Generate Overlays
```bash
# Create overlay by comparing two OpenAPI files
oas-patch diff original.yaml modified.yaml -o diff-overlay.yaml

# Generate and output to stdout
oas-patch diff original.yaml modified.yaml
```

### Validation
```bash
# Validate overlay syntax
oas-patch validate overlay.yaml

# Validate with different output formats
oas-patch validate overlay.yaml --format yaml
oas-patch validate overlay.yaml --format log
```

## Understanding Overlay Actions

The overlay you created uses several types of actions:

### 1. Remove Action
```yaml
- target: "$.servers"
  remove: true
```
**Purpose**: Removes the existing servers array

### 2. Update Action
```yaml
- target: "$"
  update:
    servers:
      - url: https://api.petstore.com
```
**Purpose**: Adds new content to the root of the document

### 3. Target Selection
- `"$"` - Root of the document
- `"$.servers"` - The servers array
- `"$.info"` - The info object
- `"$.paths./pets.get"` - Specific endpoint operation

## Next Steps

Congratulations! You've successfully applied your first overlay. Here's what to explore next:

### 🎯 Immediate Next Steps
1. [**Your First Overlay**](first-overlay.md) - Create an overlay from scratch
2. [**Core Concepts**](../core-concepts/overlays.md) - Understand overlay fundamentals
3. [**Bundle Management**](../core-concepts/bundles.md) - Organize multiple overlays

### 🚀 Advanced Topics
1. [**Environment Variables**](../core-concepts/environment-variables.md) - Dynamic configuration
2. [**CI/CD Integration**](../tutorials/cicd-integration.md) - Automate your workflow
3. [**Template Engine**](../core-concepts/templates.md) - Dynamic content generation

### 📋 Reference Materials
1. [**CLI Reference**](../cli-reference/overview.md) - Complete command documentation
2. [**Examples**](../examples/simple-modifications.md) - Real-world use cases
3. [**Troubleshooting**](../troubleshooting/common-issues.md) - Common issues and solutions

## Tips for Success

💡 **Start Small**: Begin with simple overlays and gradually add complexity  
🔍 **Use Validation**: Always validate your overlays before applying them  
📚 **Read Examples**: Check out the examples directory for inspiration  
🧪 **Test Thoroughly**: Test overlays in development before production use  
📖 **Know JSONPath**: Understanding JSONPath will help you target elements precisely  

---

**Questions?** Check our [FAQ](../troubleshooting/faq.md) or explore the [Core Concepts](../core-concepts/overlays.md) for deeper understanding.
