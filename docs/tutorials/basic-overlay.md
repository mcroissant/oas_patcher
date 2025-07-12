# Basic Overlay Application

This tutorial will walk you through creating and applying your first OpenAPI overlay. You'll learn the fundamental concepts of overlay creation, validation, and application.

## Prerequisites

- OAS Patcher installed on your system
- A basic understanding of OpenAPI/Swagger specifications
- A text editor or IDE

## Tutorial Overview

In this tutorial, we'll:
1. Start with a simple OpenAPI specification
2. Create an overlay to modify it
3. Apply the overlay and see the results
4. Validate our overlay
5. Explore different types of modifications

## Step 1: Prepare Your OpenAPI Specification

Let's start with a simple API specification. Create a file called `petstore.yaml`:

```yaml
openapi: 3.0.0
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
                  $ref: '#/components/schemas/Pet'
  /pets/{id}:
    get:
      summary: Get a pet by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: A single pet
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
components:
  schemas:
    Pet:
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

## Step 2: Create Your First Overlay

Now let's create an overlay to make some improvements to our API. Create a file called `improvements-overlay.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Pet Store API Improvements
  version: 1.0.0
  description: Adds better descriptions, examples, and production server configuration
actions:
  # Update the API version to 1.1.0
  - target: "$.info.version"
    update: "1.1.0"
    
  # Add a production server
  - target: "$.servers[1]"
    update:
      url: "https://api.petstore.com"
      description: "Production server"
      
  # Improve the API description
  - target: "$.info.description"
    update: "A comprehensive pet store API with full CRUD operations for managing pets, including status tracking and detailed pet information."
    
  # Add response examples
  - target: "$.paths./pets.get.responses.200.content.application/json.example"
    update:
      - id: 1
        name: "Fluffy"
        status: "available"
      - id: 2
        name: "Rex"
        status: "pending"
        
  # Improve operation descriptions
  - target: "$.paths./pets.get.description"
    update: "Retrieves a paginated list of all pets in the store. Use query parameters to filter by status or search by name."
    
  - target: "$.paths./pets/{id}.get.description"
    update: "Retrieves detailed information about a specific pet using its unique identifier."
    
  # Add schema descriptions
  - target: "$.components.schemas.Pet.description"
    update: "Represents a pet in the store with basic information and availability status"
    
  - target: "$.components.schemas.Pet.properties.id.description"
    update: "Unique identifier for the pet"
    
  - target: "$.components.schemas.Pet.properties.name.description"
    update: "The pet's name"
    
  - target: "$.components.schemas.Pet.properties.status.description"
    update: "Current availability status of the pet"
```

## Step 3: Validate Your Overlay

Before applying the overlay, let's validate it to ensure there are no syntax errors:

```bash
oas-patch validate improvements-overlay.yaml
```

If the overlay is valid, you should see output indicating success. If there are errors, the command will provide details about what needs to be fixed.

## Step 4: Apply the Overlay

Now let's apply the overlay to our OpenAPI specification:

```bash
oas-patch overlay petstore.yaml improvements-overlay.yaml -o petstore-improved.yaml
```

This command:
- Takes `petstore.yaml` as the base OpenAPI document
- Applies the modifications from `improvements-overlay.yaml`
- Saves the result to `petstore-improved.yaml`

## Step 5: Examine the Results

Open `petstore-improved.yaml` and compare it to the original. You should see:

1. **Version updated** to 1.1.0
2. **Additional server** for production
3. **Enhanced descriptions** throughout the API
4. **Response examples** added to the GET /pets endpoint
5. **Schema documentation** improved

Here's a snippet of what the improved version looks like:

```yaml
openapi: 3.0.0
info:
  title: Pet Store API
  version: 1.1.0  # Updated!
  description: A comprehensive pet store API with full CRUD operations for managing pets, including status tracking and detailed pet information.  # Enhanced!
servers:
  - url: http://localhost:8080
    description: Development server
  - url: https://api.petstore.com  # New production server!
    description: Production server
paths:
  /pets:
    get:
      summary: List all pets
      description: Retrieves a paginated list of all pets in the store. Use query parameters to filter by status or search by name.  # Enhanced!
      responses:
        '200':
          description: A list of pets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Pet'
              example:  # New example!
                - id: 1
                  name: "Fluffy"
                  status: "available"
                - id: 2
                  name: "Rex"
                  status: "pending"
```

## Step 6: Understanding Different Action Types

Let's explore different types of overlay actions by creating another overlay. Create `additional-changes.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Additional Changes
  version: 1.0.0
actions:
  # Remove the development server (keeping only production)
  - target: "$.servers[0]"
    remove: true
    
  # Add new security scheme
  - target: "$.components.securitySchemes"
    update:
      ApiKeyAuth:
        type: apiKey
        in: header
        name: X-API-Key
        
  # Add security requirement to all operations
  - target: "$.security"
    update:
      - ApiKeyAuth: []
      
  # Add a new endpoint
  - target: "$.paths./pets.post"
    update:
      summary: Create a new pet
      description: Adds a new pet to the store
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
      responses:
        '201':
          description: Pet created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
        '400':
          description: Invalid input
```

Apply this overlay to the already improved specification:

```bash
oas-patch overlay petstore-improved.yaml additional-changes.yaml -o petstore-final.yaml
```

## Step 7: Working with Arrays and Complex Objects

Let's create an overlay that demonstrates working with arrays and nested objects. Create `complex-modifications.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Complex Modifications
  version: 1.0.0
actions:
  # Add tags to organize operations
  - target: "$.tags"
    update:
      - name: "pets"
        description: "Pet management operations"
      - name: "store"
        description: "Store management operations"
        
  # Tag the existing operations
  - target: "$.paths./pets.get.tags"
    update: ["pets"]
    
  - target: "$.paths./pets/{id}.get.tags"
    update: ["pets"]
    
  - target: "$.paths./pets.post.tags"
    update: ["pets"]
    
  # Add query parameters to the pets list endpoint
  - target: "$.paths./pets.get.parameters"
    update:
      - name: status
        in: query
        description: Filter pets by status
        schema:
          type: string
          enum: [available, pending, sold]
      - name: limit
        in: query
        description: Maximum number of pets to return
        schema:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
          
  # Add additional properties to the Pet schema
  - target: "$.components.schemas.Pet.properties.category"
    update:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
      description: "Pet category information"
      
  - target: "$.components.schemas.Pet.properties.photoUrls"
    update:
      type: array
      items:
        type: string
        format: uri
      description: "Array of photo URLs for this pet"
```

Apply this overlay:

```bash
oas-patch overlay petstore-final.yaml complex-modifications.yaml -o petstore-complete.yaml
```

## Step 8: Common Patterns and Best Practices

### Pattern 1: Versioning Changes

Create an overlay specifically for version updates:

```yaml
overlay: 1.0.0
info:
  title: Version Update
  version: 1.0.0
actions:
  - target: "$.info.version"
    update: "2.0.0"
  - target: "$.info.title"
    update: "Pet Store API v2"
```

### Pattern 2: Environment-Specific Changes

Create overlays for different environments:

```yaml
# production-overlay.yaml
overlay: 1.0.0
info:
  title: Production Configuration
  version: 1.0.0
actions:
  - target: "$.servers"
    update:
      - url: "https://api.petstore.com"
        description: "Production server"
  - target: "$.info.contact"
    update:
      name: "API Support"
      email: "support@petstore.com"
      url: "https://petstore.com/support"
```

### Pattern 3: Security Enhancements

Create a dedicated security overlay:

```yaml
# security-overlay.yaml
overlay: 1.0.0
info:
  title: Security Enhancements
  version: 1.0.0
actions:
  - target: "$.components.securitySchemes"
    update:
      BearerAuth:
        type: http
        scheme: bearer
        bearerFormat: JWT
  - target: "$.security"
    update:
      - BearerAuth: []
```

## Step 9: Troubleshooting Common Issues

### Issue 1: Invalid JSONPath

```yaml
# Wrong - this path doesn't exist
- target: "$.info.invalid_field"
  update: "value"
  
# Correct - ensure the path is valid
- target: "$.info.description"
  update: "value"
```

### Issue 2: Type Mismatches

```yaml
# Wrong - trying to set a string where an object is expected
- target: "$.servers[0]"
  update: "https://api.example.com"
  
# Correct - provide the full object structure
- target: "$.servers[0]"
  update:
    url: "https://api.example.com"
    description: "Production server"
```

### Issue 3: Array Index Out of Bounds

```yaml
# Wrong - trying to access array index that doesn't exist
- target: "$.servers[5]"
  update:
    url: "https://api.example.com"
    
# Correct - append to array or use existing index
- target: "$.servers[1]"  # Add as second server
  update:
    url: "https://api.example.com"
```

## Next Steps

Now that you've mastered basic overlay application, you can:

1. Learn about [Multi-Environment Setup](multi-environment.md) for managing different deployment environments
2. Explore [Bundle Management](../core-concepts/bundles.md) for organizing multiple overlays
3. Try [Advanced Templating](advanced-templating.md) for dynamic overlay content

## Practice Exercises

1. **Exercise 1**: Create an overlay that adds OpenAPI contact information and license details
2. **Exercise 2**: Build an overlay that removes all development-related endpoints and adds production monitoring endpoints
3. **Exercise 3**: Design an overlay that enhances error responses with detailed error schemas

## Summary

In this tutorial, you learned:
- How to create basic overlays with different action types
- How to validate overlays before applying them
- How to apply overlays to OpenAPI specifications
- Common patterns for organizing overlay modifications
- How to troubleshoot common overlay issues

Overlays provide a powerful way to modify OpenAPI specifications without touching the original files, enabling better version control, environment management, and collaborative API development.
