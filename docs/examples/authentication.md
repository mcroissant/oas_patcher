# Authentication Setup

Learn how to add various authentication and authorization schemes to your OpenAPI specifications using OAS Patcher.

## Scenario

You need to add authentication to an existing API specification that currently has no security requirements. The API should support multiple authentication methods for different use cases.

## Problem

- Existing API has no authentication
- Need to support multiple auth methods (API keys, OAuth2, JWT)
- Different endpoints require different security levels
- Must maintain backward compatibility during migration

## Solution

Use OAS Patcher overlays to systematically add authentication schemes and apply them to appropriate endpoints.

## File Structure

```
authentication/
├── base/
│   └── openapi.yaml         # Base API without auth
├── overlays/
│   ├── security-schemes.yaml    # Add security schemes
│   ├── api-key-auth.yaml       # Apply API key auth
│   ├── oauth2-auth.yaml        # Apply OAuth2 auth
│   └── mixed-auth.yaml         # Mixed security requirements
├── bundle.yml               # Bundle configuration
└── .env.example            # Environment variables
```

## Base Specification

**base/openapi.yaml**
```yaml
openapi: 3.0.3
info:
  title: "E-commerce API"
  version: "1.0.0"
  description: "API for managing products and orders"

servers:
  - url: "https://api.example.com"
    description: "Production server"

paths:
  # Public endpoints (no auth needed)
  /products:
    get:
      summary: "List products"
      operationId: "listProducts"
      parameters:
        - name: "category"
          in: "query"
          schema:
            type: "string"
      responses:
        "200":
          description: "List of products"
          content:
            application/json:
              schema:
                type: "array"
                items:
                  $ref: "#/components/schemas/Product"

  /products/{id}:
    parameters:
      - name: "id"
        in: "path"
        required: true
        schema:
          type: "string"
    
    get:
      summary: "Get product details"
      operationId: "getProduct"
      responses:
        "200":
          description: "Product details"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Product"

  # User-specific endpoints (need auth)
  /orders:
    get:
      summary: "List user orders"
      operationId: "listOrders"
      responses:
        "200":
          description: "List of orders"
          content:
            application/json:
              schema:
                type: "array"
                items:
                  $ref: "#/components/schemas/Order"
    
    post:
      summary: "Create order"
      operationId: "createOrder"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateOrderRequest"
      responses:
        "201":
          description: "Order created"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Order"

  # Admin endpoints (need higher privileges)
  /admin/products:
    post:
      summary: "Create product"
      operationId: "createProduct"
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateProductRequest"
      responses:
        "201":
          description: "Product created"

  /admin/orders/{id}/status:
    parameters:
      - name: "id"
        in: "path"
        required: true
        schema:
          type: "string"
    
    put:
      summary: "Update order status"
      operationId: "updateOrderStatus"
      requestBody:
        content:
          application/json:
            schema:
              type: "object"
              properties:
                status:
                  type: "string"
                  enum: ["pending", "processing", "shipped", "delivered", "cancelled"]
      responses:
        "200":
          description: "Status updated"

components:
  schemas:
    Product:
      type: "object"
      properties:
        id:
          type: "string"
        name:
          type: "string"
        description:
          type: "string"
        price:
          type: "number"
          format: "decimal"
        category:
          type: "string"
      required: ["id", "name", "price"]
    
    Order:
      type: "object"
      properties:
        id:
          type: "string"
        userId:
          type: "string"
        items:
          type: "array"
          items:
            type: "object"
            properties:
              productId:
                type: "string"
              quantity:
                type: "integer"
              price:
                type: "number"
        status:
          type: "string"
        total:
          type: "number"
      required: ["id", "userId", "items", "status", "total"]
    
    CreateOrderRequest:
      type: "object"
      properties:
        items:
          type: "array"
          items:
            type: "object"
            properties:
              productId:
                type: "string"
              quantity:
                type: "integer"
            required: ["productId", "quantity"]
      required: ["items"]
    
    CreateProductRequest:
      type: "object"
      properties:
        name:
          type: "string"
        description:
          type: "string"
        price:
          type: "number"
        category:
          type: "string"
      required: ["name", "price"]
```

## Security Schemes Overlay

**overlays/security-schemes.yaml**
```yaml
overlay: 1.0.0
info:
  title: "Security Schemes Setup"
  version: "1.0.0"
  description: "Adds security scheme definitions"

actions:
  # Add API Key authentication
  - target: "$.components.securitySchemes.ApiKeyAuth"
    update:
      type: "apiKey"
      in: "header"
      name: "X-API-Key"
      description: "API key for basic authentication"
    description: "Add API key security scheme"
  
  # Add Bearer token authentication (JWT)
  - target: "$.components.securitySchemes.BearerAuth"
    update:
      type: "http"
      scheme: "bearer"
      bearerFormat: "JWT"
      description: "JWT token authentication"
    description: "Add Bearer token security scheme"
  
  # Add OAuth2 authentication
  - target: "$.components.securitySchemes.OAuth2"
    update:
      type: "oauth2"
      description: "OAuth2 authentication"
      flows:
        authorizationCode:
          authorizationUrl: "{{ OAUTH_AUTH_URL | default('https://auth.example.com/oauth/authorize') }}"
          tokenUrl: "{{ OAUTH_TOKEN_URL | default('https://auth.example.com/oauth/token') }}"
          scopes:
            read: "Read access to resources"
            write: "Write access to resources"
            admin: "Administrative access"
        clientCredentials:
          tokenUrl: "{{ OAUTH_TOKEN_URL | default('https://auth.example.com/oauth/token') }}"
          scopes:
            read: "Read access to resources"
            write: "Write access to resources"
            admin: "Administrative access"
    description: "Add OAuth2 security scheme"
  
  # Add Basic authentication (for admin tools)
  - target: "$.components.securitySchemes.BasicAuth"
    update:
      type: "http"
      scheme: "basic"
      description: "Basic HTTP authentication"
    description: "Add Basic auth security scheme"
  
  # Add common error responses for authentication
  - target: "$.components.responses.UnauthorizedError"
    update:
      description: "Authentication required"
      content:
        application/json:
          schema:
            type: "object"
            properties:
              error:
                type: "string"
                example: "Authentication required"
              code:
                type: "string"
                example: "UNAUTHORIZED"
    description: "Add unauthorized error response"
  
  - target: "$.components.responses.ForbiddenError"
    update:
      description: "Insufficient permissions"
      content:
        application/json:
          schema:
            type: "object"
            properties:
              error:
                type: "string"
                example: "Insufficient permissions"
              code:
                type: "string"
                example: "FORBIDDEN"
    description: "Add forbidden error response"
```

## API Key Authentication Overlay

**overlays/api-key-auth.yaml**
```yaml
overlay: 1.0.0
info:
  title: "API Key Authentication"
  version: "1.0.0"
  description: "Applies API key authentication to user endpoints"

actions:
  # Apply API key auth to user order endpoints
  - target: "$.paths./orders.get.security"
    update:
      - ApiKeyAuth: []
    description: "Require API key for listing orders"
  
  - target: "$.paths./orders.post.security"
    update:
      - ApiKeyAuth: []
    description: "Require API key for creating orders"
  
  # Add auth error responses to order endpoints
  - target: "$.paths./orders.get.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to get orders"
  
  - target: "$.paths./orders.post.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to create order"
  
  # Add security information to operation descriptions
  - target: "$.paths./orders.get.description"
    update: "Retrieves all orders for the authenticated user. Requires valid API key."
    description: "Update get orders description"
  
  - target: "$.paths./orders.post.description"
    update: "Creates a new order for the authenticated user. Requires valid API key."
    description: "Update create order description"
```

## OAuth2 Authentication Overlay

**overlays/oauth2-auth.yaml**
```yaml
overlay: 1.0.0
info:
  title: "OAuth2 Authentication"
  version: "1.0.0"
  description: "Applies OAuth2 authentication with scope-based access"

actions:
  # Apply OAuth2 with read scope to order listing
  - target: "$.paths./orders.get.security"
    update:
      - OAuth2: ["read"]
    description: "Require OAuth2 read scope for listing orders"
  
  # Apply OAuth2 with write scope to order creation
  - target: "$.paths./orders.post.security"
    update:
      - OAuth2: ["write"]
    description: "Require OAuth2 write scope for creating orders"
  
  # Apply OAuth2 with admin scope to admin endpoints
  - target: "$.paths./admin/products.post.security"
    update:
      - OAuth2: ["admin"]
    description: "Require OAuth2 admin scope for creating products"
  
  - target: "$.paths./admin/orders/{id}/status.put.security"
    update:
      - OAuth2: ["admin"]
    description: "Require OAuth2 admin scope for updating order status"
  
  # Add auth error responses
  - target: "$.paths./orders.get.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to get orders"
  
  - target: "$.paths./orders.get.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to get orders"
  
  - target: "$.paths./orders.post.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to create order"
  
  - target: "$.paths./orders.post.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to create order"
  
  - target: "$.paths./admin/products.post.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to create product"
  
  - target: "$.paths./admin/products.post.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to create product"
  
  - target: "$.paths./admin/orders/{id}/status.put.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to update order status"
  
  - target: "$.paths./admin/orders/{id}/status.put.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to update order status"
```

## Mixed Authentication Overlay

**overlays/mixed-auth.yaml**
```yaml
overlay: 1.0.0
info:
  title: "Mixed Authentication"
  version: "1.0.0"
  description: "Applies different auth methods to different endpoints"

actions:
  # User endpoints: API Key OR Bearer token
  - target: "$.paths./orders.get.security"
    update:
      - ApiKeyAuth: []
      - BearerAuth: []
    description: "Allow API key or Bearer token for listing orders"
  
  - target: "$.paths./orders.post.security"
    update:
      - ApiKeyAuth: []
      - BearerAuth: []
    description: "Allow API key or Bearer token for creating orders"
  
  # Admin endpoints: OAuth2 with admin scope OR Basic auth
  - target: "$.paths./admin/products.post.security"
    update:
      - OAuth2: ["admin"]
      - BasicAuth: []
    description: "Require OAuth2 admin scope or Basic auth for creating products"
  
  - target: "$.paths./admin/orders/{id}/status.put.security"
    update:
      - OAuth2: ["admin"]
      - BasicAuth: []
    description: "Require OAuth2 admin scope or Basic auth for updating orders"
  
  # Add comprehensive error responses
  - target: "$.paths./orders.get.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to get orders"
  
  - target: "$.paths./orders.post.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to create order"
  
  - target: "$.paths./admin/products.post.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to create product"
  
  - target: "$.paths./admin/products.post.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to create product"
  
  - target: "$.paths./admin/orders/{id}/status.put.responses.401"
    update:
      $ref: "#/components/responses/UnauthorizedError"
    description: "Add 401 response to update order status"
  
  - target: "$.paths./admin/orders/{id}/status.put.responses.403"
    update:
      $ref: "#/components/responses/ForbiddenError"
    description: "Add 403 response to update order status"
  
  # Add security documentation to API info
  - target: "$.info.description"
    update: |
      API for managing products and orders
      
      ## Authentication
      
      This API supports multiple authentication methods:
      
      ### For User Endpoints (/orders)
      - **API Key**: Include `X-API-Key` header with your API key
      - **Bearer Token**: Include `Authorization: Bearer <token>` header with JWT token
      
      ### For Admin Endpoints (/admin/*)
      - **OAuth2**: Use OAuth2 flow with `admin` scope
      - **Basic Auth**: Use HTTP Basic authentication (admin tools only)
      
      ### Public Endpoints
      - Product listing and details are publicly accessible
    description: "Add authentication documentation to API description"
```

## Bundle Configuration

**bundle.yml**
```yaml
name: "Authentication Setup Bundle"
version: "1.0.0"
description: "Demonstrates different authentication setups"

input: "base/openapi.yaml"

environments:
  api-key:
    description: "Simple API key authentication"
    variables:
      AUTH_TYPE: "api-key"
    overlays:
      - "overlays/security-schemes.yaml"
      - "overlays/api-key-auth.yaml"
  
  oauth2:
    description: "OAuth2 with scope-based access"
    variables:
      AUTH_TYPE: "oauth2"
      OAUTH_AUTH_URL: "{{ OAUTH_BASE_URL | default('https://auth.example.com') }}/oauth/authorize"
      OAUTH_TOKEN_URL: "{{ OAUTH_BASE_URL | default('https://auth.example.com') }}/oauth/token"
    overlays:
      - "overlays/security-schemes.yaml"
      - "overlays/oauth2-auth.yaml"
  
  mixed:
    description: "Mixed authentication methods"
    variables:
      AUTH_TYPE: "mixed"
      OAUTH_AUTH_URL: "{{ OAUTH_BASE_URL | default('https://auth.example.com') }}/oauth/authorize"
      OAUTH_TOKEN_URL: "{{ OAUTH_BASE_URL | default('https://auth.example.com') }}/oauth/token"
    overlays:
      - "overlays/security-schemes.yaml"
      - "overlays/mixed-auth.yaml"

# Global variables
variables:
  API_VERSION: "1.0.0"
  SUPPORT_EMAIL: "support@example.com"
```

## Environment Variables

**.env.example**
```bash
# OAuth2 Configuration
OAUTH_BASE_URL=https://auth.example.com
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret

# API Configuration
API_BASE_URL=https://api.example.com
SUPPORT_EMAIL=support@example.com

# Environment
ENVIRONMENT=development
DEBUG_MODE=true
```

## Usage

### Generate API Key Version

```bash
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment api-key \
  --output openapi-apikey.yaml
```

### Generate OAuth2 Version

```bash
# With default OAuth URLs
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment oauth2 \
  --output openapi-oauth2.yaml

# With custom OAuth provider
OAUTH_BASE_URL=https://custom-auth.example.com \
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment oauth2 \
  --output openapi-oauth2-custom.yaml
```

### Generate Mixed Authentication Version

```bash
oas-patcher bundle apply \
  --bundle bundle.yml \
  --environment mixed \
  --output openapi-mixed.yaml
```

## Authentication Patterns

### 1. Progressive Authentication

Start with API keys, upgrade to OAuth2:

```yaml
# Stage 1: API key only
overlays: ["security-schemes.yaml", "api-key-auth.yaml"]

# Stage 2: Add OAuth2 as alternative
overlays: ["security-schemes.yaml", "mixed-auth.yaml"]

# Stage 3: OAuth2 only (deprecated API keys)
overlays: ["security-schemes.yaml", "oauth2-auth.yaml"]
```

### 2. Endpoint-Specific Security

Different auth for different endpoint groups:

```yaml
actions:
  # Public endpoints - no auth
  - target: "$.paths./products"
    # No security property
  
  # User endpoints - API key or JWT
  - target: "$.paths./orders.get.security"
    update:
      - ApiKeyAuth: []
      - BearerAuth: []
  
  # Admin endpoints - OAuth2 admin scope only
  - target: "$.paths./admin/products.post.security"
    update:
      - OAuth2: ["admin"]
```

### 3. Environment-Specific Auth

Different auth schemes per environment:

```yaml
environments:
  development:
    # Relaxed auth for development
    overlays: ["security-schemes.yaml", "api-key-auth.yaml"]
  
  production:
    # Strict OAuth2 for production
    overlays: ["security-schemes.yaml", "oauth2-auth.yaml"]
```

## Security Best Practices

### 1. Comprehensive Error Responses

```yaml
# Always add proper error responses
- target: "$.paths./protected-endpoint.get.responses.401"
  update:
    $ref: "#/components/responses/UnauthorizedError"

- target: "$.paths./protected-endpoint.get.responses.403"
  update:
    $ref: "#/components/responses/ForbiddenError"
```

### 2. Scope Documentation

```yaml
# Document OAuth2 scopes clearly
- target: "$.components.securitySchemes.OAuth2.flows.authorizationCode.scopes"
  update:
    read: "Read access to user's own data"
    write: "Create and modify user's own data"
    admin: "Full access to all data and admin functions"
```

### 3. Security Headers

```yaml
# Add security-related headers
- target: "$.paths./secure-endpoint.get.responses.200.headers"
  update:
    X-RateLimit-Remaining:
      schema:
        type: "integer"
      description: "Number of requests remaining"
    X-RateLimit-Reset:
      schema:
        type: "integer"
      description: "Time when rate limit resets"
```

## Testing Authentication

### Test Scripts

Create test scripts for each auth method:

```bash
#!/bin/bash
# test-api-key.sh

API_KEY="your-api-key"
BASE_URL="https://api.example.com"

# Test public endpoint (should work)
curl -v "$BASE_URL/products"

# Test protected endpoint without auth (should fail)
curl -v "$BASE_URL/orders"

# Test protected endpoint with auth (should work)
curl -v -H "X-API-Key: $API_KEY" "$BASE_URL/orders"
```

```bash
#!/bin/bash
# test-oauth2.sh

ACCESS_TOKEN="your-access-token"
BASE_URL="https://api.example.com"

# Test with Bearer token
curl -v -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE_URL/orders"

# Test admin endpoint with insufficient scope (should fail)
curl -v -H "Authorization: Bearer $ACCESS_TOKEN" \
  -X POST "$BASE_URL/admin/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Product","price":10.00}'
```

## Troubleshooting

### Common Issues

1. **Missing Security Schemes**
   ```
   Error: Security scheme 'ApiKeyAuth' not found
   ```
   - Ensure security-schemes.yaml is applied first
   - Check scheme names match exactly

2. **Invalid OAuth2 URLs**
   ```
   Error: Invalid URL format
   ```
   - Validate OAuth2 URLs in environment variables
   - Ensure URLs are properly formatted

3. **Conflicting Security Requirements**
   ```
   Warning: Multiple security schemes on same endpoint
   ```
   - Use arrays for alternative auth methods
   - Use separate objects for required combinations

### Validation

```bash
# Validate the final specification
oas-patcher validate openapi-with-auth.yaml

# Check security coverage
oas-patcher analyze security openapi-with-auth.yaml

# Test against security best practices
spectral lint openapi-with-auth.yaml
```
