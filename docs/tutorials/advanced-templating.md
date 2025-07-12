# Advanced Templating

This tutorial explores the powerful templating capabilities of OAS Patcher's template engine. You'll learn advanced Jinja2 patterns, custom functions, dynamic content generation, and sophisticated template organization strategies.

## Prerequisites

- Completed previous tutorials, especially [Multi-Environment Setup](multi-environment.md)
- Understanding of [Template Engine](../core-concepts/templates.md) concepts
- Basic knowledge of Jinja2 templating syntax
- Familiarity with JSON/YAML structures

## Tutorial Overview

In this tutorial, we'll:
1. Master advanced Jinja2 templating patterns
2. Create dynamic schema generation
3. Implement template inheritance and includes
4. Build conditional API configurations
5. Handle complex data transformations
6. Debug and troubleshoot templates
7. Optimize template performance

## Step 1: Advanced Template Patterns

### Dynamic Schema Generation

Create templates that generate schemas based on configuration:

```yaml
# overlays/dynamic-schemas.yaml
overlay: 1.0.0
info:
  title: Dynamic Schema Generation
  version: 1.0.0
actions:
  # Generate schemas for different entity types
  {% for entity in entities %}
  - target: "$.components.schemas.{{ entity.name }}"
    update:
      type: object
      description: "{{ entity.description }}"
      required:
        {% for field in entity.fields if field.required %}
        - "{{ field.name }}"
        {% endfor %}
      properties:
        {% for field in entity.fields %}
        {{ field.name }}:
          type: "{{ field.type }}"
          {% if field.description %}
          description: "{{ field.description }}"
          {% endif %}
          {% if field.format %}
          format: "{{ field.format }}"
          {% endif %}
          {% if field.enum %}
          enum: {{ field.enum | to_json }}
          {% endif %}
          {% if field.validation %}
          {% for key, value in field.validation.items() %}
          {{ key }}: {{ value }}
          {% endfor %}
          {% endif %}
        {% endfor %}
      {% if entity.example %}
      example: {{ entity.example | to_json }}
      {% endif %}
  {% endfor %}
```

Bundle configuration with entity definitions:

```yaml
# In bundle.yaml
variables:
  entities:
    - name: "User"
      description: "User account information"
      fields:
        - name: "id"
          type: "integer"
          description: "Unique user identifier"
          required: true
          validation:
            minimum: 1
        - name: "username"
          type: "string"
          description: "User login name"
          required: true
          validation:
            minLength: 3
            maxLength: 50
            pattern: "^[a-zA-Z0-9_]+$"
        - name: "email"
          type: "string"
          format: "email"
          description: "User email address"
          required: true
        - name: "role"
          type: "string"
          description: "User role"
          required: true
          enum: ["admin", "user", "guest"]
        - name: "created_at"
          type: "string"
          format: "date-time"
          description: "Account creation timestamp"
      example:
        id: 1
        username: "johndoe"
        email: "john@example.com"
        role: "user"
        created_at: "2024-01-15T10:30:00Z"
        
    - name: "Product"
      description: "Product catalog item"
      fields:
        - name: "id"
          type: "integer"
          description: "Product identifier"
          required: true
        - name: "name"
          type: "string"
          description: "Product name"
          required: true
          validation:
            minLength: 1
            maxLength: 100
        - name: "price"
          type: "number"
          format: "decimal"
          description: "Product price"
          required: true
          validation:
            minimum: 0
        - name: "category"
          type: "string"
          description: "Product category"
          enum: ["electronics", "clothing", "books", "home"]
        - name: "in_stock"
          type: "boolean"
          description: "Whether product is in stock"
      example:
        id: 101
        name: "Wireless Headphones"
        price: 99.99
        category: "electronics"
        in_stock: true
```

### Dynamic Endpoint Generation

Create endpoints based on entity configuration:

```yaml
# overlays/dynamic-endpoints.yaml
overlay: 1.0.0
info:
  title: Dynamic Endpoint Generation
actions:
  {% for entity in entities %}
  {% set entity_lower = entity.name | lower %}
  {% set entity_plural = entity.plural | default(entity_lower + 's') %}
  
  # List {{ entity.name }} endpoint
  - target: "$.paths./{{ entity_plural }}"
    update:
      get:
        tags: ["{{ entity_lower }}"]
        summary: "List {{ entity.name }} items"
        description: "Retrieve a paginated list of {{ entity.name | lower }} items"
        parameters:
          - name: "page"
            in: "query"
            description: "Page number"
            schema:
              type: "integer"
              minimum: 1
              default: 1
          - name: "limit"
            in: "query"
            description: "Items per page"
            schema:
              type: "integer"
              minimum: 1
              maximum: 100
              default: 20
          {% for field in entity.fields if field.filterable %}
          - name: "{{ field.name }}"
            in: "query"
            description: "Filter by {{ field.description | lower }}"
            schema:
              type: "{{ field.type }}"
              {% if field.enum %}
              enum: {{ field.enum | to_json }}
              {% endif %}
          {% endfor %}
        responses:
          '200':
            description: "List of {{ entity.name | lower }} items"
            content:
              application/json:
                schema:
                  type: "object"
                  properties:
                    data:
                      type: "array"
                      items:
                        $ref: "#/components/schemas/{{ entity.name }}"
                    pagination:
                      $ref: "#/components/schemas/Pagination"
                example:
                  data: [{{ entity.example | to_json }}]
                  pagination:
                    page: 1
                    limit: 20
                    total: 1
                    pages: 1
      post:
        tags: ["{{ entity_lower }}"]
        summary: "Create {{ entity.name }}"
        description: "Create a new {{ entity.name | lower }} item"
        requestBody:
          required: true
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{{ entity.name }}Create"
        responses:
          '201':
            description: "{{ entity.name }} created successfully"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/{{ entity.name }}"
          '400':
            $ref: "#/components/responses/BadRequest"
          '401':
            $ref: "#/components/responses/Unauthorized"
            
  # Individual {{ entity.name }} endpoint
  - target: "$.paths./{{ entity_plural }}/{id}"
    update:
      get:
        tags: ["{{ entity_lower }}"]
        summary: "Get {{ entity.name }} by ID"
        description: "Retrieve a specific {{ entity.name | lower }} by its identifier"
        parameters:
          - name: "id"
            in: "path"
            required: true
            description: "{{ entity.name }} identifier"
            schema:
              type: "{{ entity.id_field.type | default('integer') }}"
        responses:
          '200':
            description: "{{ entity.name }} details"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/{{ entity.name }}"
          '404':
            $ref: "#/components/responses/NotFound"
      put:
        tags: ["{{ entity_lower }}"]
        summary: "Update {{ entity.name }}"
        description: "Update an existing {{ entity.name | lower }}"
        parameters:
          - name: "id"
            in: "path"
            required: true
            schema:
              type: "{{ entity.id_field.type | default('integer') }}"
        requestBody:
          required: true
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{{ entity.name }}Update"
        responses:
          '200':
            description: "{{ entity.name }} updated successfully"
            content:
              application/json:
                schema:
                  $ref: "#/components/schemas/{{ entity.name }}"
          '400':
            $ref: "#/components/responses/BadRequest"
          '404':
            $ref: "#/components/responses/NotFound"
      delete:
        tags: ["{{ entity_lower }}"]
        summary: "Delete {{ entity.name }}"
        description: "Delete a {{ entity.name | lower }}"
        parameters:
          - name: "id"
            in: "path"
            required: true
            schema:
              type: "{{ entity.id_field.type | default('integer') }}"
        responses:
          '204':
            description: "{{ entity.name }} deleted successfully"
          '404':
            $ref: "#/components/responses/NotFound"
  {% endfor %}
```

## Step 2: Template Macros and Functions

### Creating Reusable Macros

```yaml
# overlays/template-macros.yaml
overlay: 1.0.0
info:
  title: Template Macros Example

# Define reusable macros
{% macro generate_pagination_params() %}
- name: "page"
  in: "query"
  description: "Page number for pagination"
  schema:
    type: "integer"
    minimum: 1
    default: 1
- name: "limit"
  in: "query"
  description: "Number of items per page"
  schema:
    type: "integer"
    minimum: 1
    maximum: 100
    default: 20
{% endmacro %}

{% macro generate_error_responses() %}
'400':
  $ref: "#/components/responses/BadRequest"
'401':
  $ref: "#/components/responses/Unauthorized"
'403':
  $ref: "#/components/responses/Forbidden"
'404':
  $ref: "#/components/responses/NotFound"
'500':
  $ref: "#/components/responses/InternalServerError"
{% endmacro %}

{% macro generate_crud_endpoint(entity_name, endpoint_path) %}
get:
  tags: ["{{ entity_name | lower }}"]
  summary: "List {{ entity_name }}"
  parameters:
    {{ generate_pagination_params() | indent(4) }}
  responses:
    '200':
      description: "List of {{ entity_name | lower }} items"
      content:
        application/json:
          schema:
            type: "object"
            properties:
              data:
                type: "array"
                items:
                  $ref: "#/components/schemas/{{ entity_name }}"
              pagination:
                $ref: "#/components/schemas/Pagination"
    {{ generate_error_responses() | indent(4) }}
post:
  tags: ["{{ entity_name | lower }}"]
  summary: "Create {{ entity_name }}"
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: "#/components/schemas/{{ entity_name }}Create"
  responses:
    '201':
      description: "{{ entity_name }} created successfully"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/{{ entity_name }}"
    {{ generate_error_responses() | indent(4) }}
{% endmacro %}

actions:
  {% for entity in api_entities %}
  - target: "$.paths.{{ entity.endpoint }}"
    update:
      {{ generate_crud_endpoint(entity.name, entity.endpoint) | indent(6) }}
  {% endfor %}
```

### Custom Filter Functions

Create custom Jinja2 filters for specific transformations:

```yaml
# overlays/custom-filters.yaml
overlay: 1.0.0
info:
  title: Custom Filters Example
actions:
  # Use custom filters for data transformation
  - target: "$.info.title"
    update: "{{ api_name | title_case }} API"
    
  - target: "$.info.version"
    update: "{{ version | semver_format }}"
    
  # Generate server URLs with custom formatting
  {% for region in regions %}
  - target: "$.servers[{{ loop.index0 }}]"
    update:
      url: "{{ base_url | region_url(region.code) }}"
      description: "{{ region.name }} server"
      x-region: "{{ region.code }}"
  {% endfor %}
  
  # Transform database configuration
  - target: "$.info.x-database"
    update:
      host: "{{ db_config.host | encrypt_sensitive }}"
      port: "{{ db_config.port | int }}"
      ssl_enabled: "{{ db_config.ssl | bool }}"
      connection_string: "{{ db_config | connection_string_format }}"
```

## Step 3: Conditional Template Logic

### Environment-Based Feature Flags

```yaml
# overlays/feature-flags.yaml
overlay: 1.0.0
info:
  title: Feature Flag Configuration
actions:
  {% if features.user_management.enabled %}
  # User management endpoints (only if feature is enabled)
  - target: "$.paths./users"
    update:
      get:
        summary: "List users"
        description: "{{ features.user_management.description }}"
        x-feature-flag: "user_management"
        responses:
          '200':
            description: "List of users"
            
  {% if features.user_management.admin_only and environment == "production" %}
  # Admin-only endpoints in production
  - target: "$.paths./admin/users"
    update:
      get:
        summary: "Admin user management"
        security:
          - AdminAuth: []
        x-admin-only: true
  {% endif %}
  {% endif %}
  
  {% if features.analytics.enabled %}
  # Analytics endpoints
  - target: "$.paths./analytics"
    update:
      get:
        summary: "Get analytics data"
        description: "{{ features.analytics.description }}"
        {% if features.analytics.real_time %}
        x-real-time: true
        {% endif %}
        parameters:
          {% if features.analytics.date_range %}
          - name: "start_date"
            in: "query"
            schema:
              type: "string"
              format: "date"
          - name: "end_date"
            in: "query"
            schema:
              type: "string"
              format: "date"
          {% endif %}
  {% endif %}
  
  # Conditional security based on environment
  {% if environment in ["staging", "production"] %}
  - target: "$.security"
    update:
      - BearerAuth: []
      {% if environment == "production" %}
      - ApiKeyAuth: []
      {% endif %}
  {% endif %}
```

### Complex Conditional Logic

```yaml
# overlays/complex-conditions.yaml
overlay: 1.0.0
info:
  title: Complex Conditional Logic
actions:
  # Multi-condition server configuration
  {% set server_config = [] %}
  
  {% if environment == "development" %}
    {% set _ = server_config.append({
      "url": "http://localhost:" + (dev_port | string),
      "description": "Development server"
    }) %}
  {% elif environment == "staging" %}
    {% for region in staging_regions %}
      {% set _ = server_config.append({
        "url": "https://staging-" + region.code + ".example.com",
        "description": region.name + " staging server"
      }) %}
    {% endfor %}
  {% elif environment == "production" %}
    {% for region in production_regions %}
      {% if region.enabled %}
        {% set server_url = "https://" + region.code + ".example.com" %}
        {% if region.custom_domain %}
          {% set server_url = "https://" + region.custom_domain %}
        {% endif %}
        {% set _ = server_config.append({
          "url": server_url,
          "description": region.name + " production server",
          "x-region": region.code,
          "x-load-balancer": region.load_balancer | default("auto")
        }) %}
      {% endif %}
    {% endfor %}
  {% endif %}
  
  - target: "$.servers"
    update: {{ server_config | to_json }}
    
  # Conditional schema validation based on business rules
  {% for entity in entities %}
  {% if entity.validation_rules %}
  - target: "$.components.schemas.{{ entity.name }}"
    update:
      allOf:
        - $ref: "#/components/schemas/{{ entity.name }}Base"
        {% for rule in entity.validation_rules %}
        {% if rule.condition_met(environment, features) %}
        - type: "object"
          {% if rule.required_fields %}
          required: {{ rule.required_fields | to_json }}
          {% endif %}
          properties:
            {% for field, validation in rule.field_validations.items() %}
            {{ field }}:
              {% for constraint, value in validation.items() %}
              {{ constraint }}: {{ value | to_json }}
              {% endfor %}
            {% endfor %}
        {% endif %}
        {% endfor %}
  {% endif %}
  {% endfor %}
```

## Step 4: Advanced Data Transformations

### Configuration-Driven API Generation

```yaml
# overlays/config-driven-api.yaml
overlay: 1.0.0
info:
  title: Configuration-Driven API
variables:
  # API configuration as data
  api_config:
    endpoints:
      - name: "users"
        methods: ["GET", "POST", "PUT", "DELETE"]
        authentication: "required"
        pagination: true
        search_fields: ["username", "email"]
        sort_fields: ["created_at", "username"]
        
      - name: "products"
        methods: ["GET", "POST", "PUT"]
        authentication: "optional"
        pagination: true
        search_fields: ["name", "category"]
        filters: ["category", "price_range", "in_stock"]
        
    authentication:
      schemes:
        - name: "BearerAuth"
          type: "http"
          scheme: "bearer"
        - name: "ApiKeyAuth"
          type: "apiKey"
          location: "header"
          name: "X-API-Key"

actions:
  # Generate authentication schemes
  {% for scheme in api_config.authentication.schemes %}
  - target: "$.components.securitySchemes.{{ scheme.name }}"
    update:
      type: "{{ scheme.type }}"
      {% if scheme.type == "http" %}
      scheme: "{{ scheme.scheme }}"
      {% elif scheme.type == "apiKey" %}
      in: "{{ scheme.location }}"
      name: "{{ scheme.name }}"
      {% endif %}
  {% endfor %}
  
  # Generate endpoints from configuration
  {% for endpoint in api_config.endpoints %}
  {% set base_path = "/" + endpoint.name %}
  {% set item_path = "/" + endpoint.name + "/{id}" %}
  
  {% if "GET" in endpoint.methods %}
  # List endpoint
  - target: "$.paths.{{ base_path }}.get"
    update:
      summary: "List {{ endpoint.name }}"
      {% if endpoint.authentication == "required" %}
      security:
        {% for scheme in api_config.authentication.schemes %}
        - {{ scheme.name }}: []
        {% endfor %}
      {% endif %}
      parameters:
        {% if endpoint.pagination %}
        - name: "page"
          in: "query"
          schema:
            type: "integer"
            minimum: 1
            default: 1
        - name: "limit"
          in: "query"
          schema:
            type: "integer"
            minimum: 1
            maximum: 100
            default: 20
        {% endif %}
        {% if endpoint.search_fields %}
        - name: "search"
          in: "query"
          description: "Search in fields: {{ endpoint.search_fields | join(', ') }}"
          schema:
            type: "string"
        {% endif %}
        {% if endpoint.sort_fields %}
        - name: "sort"
          in: "query"
          description: "Sort by field"
          schema:
            type: "string"
            enum: {{ endpoint.sort_fields | to_json }}
        - name: "order"
          in: "query"
          schema:
            type: "string"
            enum: ["asc", "desc"]
            default: "asc"
        {% endif %}
        {% if endpoint.filters %}
        {% for filter in endpoint.filters %}
        - name: "{{ filter }}"
          in: "query"
          description: "Filter by {{ filter }}"
          schema:
            type: "string"
        {% endfor %}
        {% endif %}
      responses:
        '200':
          description: "List of {{ endpoint.name }}"
          content:
            application/json:
              schema:
                type: "object"
                properties:
                  data:
                    type: "array"
                    items:
                      $ref: "#/components/schemas/{{ endpoint.name | title }}"
                  {% if endpoint.pagination %}
                  pagination:
                    $ref: "#/components/schemas/Pagination"
                  {% endif %}
  {% endif %}
  
  {% if "POST" in endpoint.methods %}
  # Create endpoint
  - target: "$.paths.{{ base_path }}.post"
    update:
      summary: "Create {{ endpoint.name | title }}"
      {% if endpoint.authentication == "required" %}
      security:
        {% for scheme in api_config.authentication.schemes %}
        - {{ scheme.name }}: []
        {% endfor %}
      {% endif %}
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/{{ endpoint.name | title }}Create"
      responses:
        '201':
          description: "{{ endpoint.name | title }} created"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{{ endpoint.name | title }}"
  {% endif %}
  {% endfor %}
```

### Data Aggregation and Processing

```yaml
# overlays/data-processing.yaml
overlay: 1.0.0
info:
  title: Data Processing and Aggregation
actions:
  # Process and aggregate configuration data
  {% set all_tags = [] %}
  {% set all_schemas = [] %}
  {% set security_requirements = [] %}
  
  {% for service in microservices %}
    {% for tag in service.tags %}
      {% if tag not in all_tags %}
        {% set _ = all_tags.append(tag) %}
      {% endif %}
    {% endfor %}
    
    {% for schema in service.schemas %}
      {% set _ = all_schemas.append({
        "name": service.name + schema.name,
        "definition": schema.definition,
        "service": service.name
      }) %}
    {% endfor %}
    
    {% if service.requires_auth %}
      {% set _ = security_requirements.append(service.auth_scheme) %}
    {% endif %}
  {% endfor %}
  
  # Generate consolidated tags
  - target: "$.tags"
    update:
      {% for tag in all_tags | sort %}
      - name: "{{ tag }}"
        description: "{{ tag | title }} related operations"
      {% endfor %}
  
  # Generate all schemas
  {% for schema in all_schemas %}
  - target: "$.components.schemas.{{ schema.name }}"
    update: {{ schema.definition | to_json }}
  {% endfor %}
  
  # Generate security matrix
  - target: "$.components.x-security-matrix"
    update:
      required_schemes: {{ security_requirements | unique | to_json }}
      service_requirements:
        {% for service in microservices %}
        {{ service.name }}:
          auth_required: {{ service.requires_auth | default(false) }}
          {% if service.requires_auth %}
          scheme: "{{ service.auth_scheme }}"
          {% endif %}
          scopes: {{ service.scopes | default([]) | to_json }}
        {% endfor %}
```

## Step 5: Template Organization and Inheritance

### Template Includes

Create modular templates using includes:

```yaml
# templates/base/common-responses.yaml
# Common response definitions
BadRequest:
  description: "Invalid request parameters"
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/Error"
        
Unauthorized:
  description: "Authentication required"
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/Error"

NotFound:
  description: "Resource not found"
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/Error"
```

```yaml
# templates/base/pagination.yaml  
# Pagination parameter definitions
PaginationParams:
  - name: "page"
    in: "query"
    description: "Page number"
    schema:
      type: "integer"
      minimum: 1
      default: 1
  - name: "limit"
    in: "query"
    description: "Items per page"
    schema:
      type: "integer"
      minimum: 1
      maximum: 100
      default: 20
```

```yaml
# overlays/main-template.yaml
overlay: 1.0.0
info:
  title: Main Template with Includes
actions:
  # Include common responses
  - target: "$.components.responses"
    update:
      {% include 'templates/base/common-responses.yaml' %}
      
  # Generate endpoints with included pagination
  {% for endpoint in endpoints %}
  - target: "$.paths.{{ endpoint.path }}.get"
    update:
      summary: "{{ endpoint.summary }}"
      parameters:
        {% include 'templates/base/pagination.yaml' %}
        {% for param in endpoint.custom_params %}
        - {{ param | to_json }}
        {% endfor %}
      responses:
        '200':
          description: "{{ endpoint.success_description }}"
        '400':
          $ref: "#/components/responses/BadRequest"
        '404':
          $ref: "#/components/responses/NotFound"
  {% endfor %}
```

### Template Inheritance

```yaml
# templates/base/crud-template.yaml
# Base CRUD template
overlay: 1.0.0
info:
  title: "{% block title %}Base CRUD Template{% endblock %}"
actions:
  - target: "$.paths.{{ resource_path }}"
    update:
      get:
        summary: "{% block list_summary %}List items{% endblock %}"
        description: "{% block list_description %}Retrieve a list of items{% endblock %}"
        parameters:
          {% block list_parameters %}
          - name: "page"
            in: "query"
            schema:
              type: "integer"
              default: 1
          {% endblock %}
        responses:
          '200':
            description: "{% block list_response_description %}List of items{% endblock %}"
            content:
              application/json:
                schema:
                  {% block list_response_schema %}
                  type: "array"
                  items:
                    $ref: "#/components/schemas/{{ resource_name }}"
                  {% endblock %}
          {% block list_error_responses %}
          '400':
            $ref: "#/components/responses/BadRequest"
          {% endblock %}
      
      post:
        summary: "{% block create_summary %}Create item{% endblock %}"
        requestBody:
          {% block create_request_body %}
          required: true
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/{{ resource_name }}Create"
          {% endblock %}
        responses:
          {% block create_responses %}
          '201':
            description: "Item created successfully"
          {% endblock %}
```

```yaml
# overlays/user-crud.yaml
# Extends base CRUD template for users
{% extends "templates/base/crud-template.yaml" %}

{% block title %}User Management API{% endblock %}

{% block list_summary %}List users{% endblock %}
{% block list_description %}Retrieve a paginated list of users with optional filtering{% endblock %}

{% block list_parameters %}
{{ super() }}
- name: "role"
  in: "query"
  description: "Filter by user role"
  schema:
    type: "string"
    enum: ["admin", "user", "guest"]
- name: "active"
  in: "query"
  description: "Filter by active status"
  schema:
    type: "boolean"
{% endblock %}

{% block create_summary %}Create new user{% endblock %}

{% block create_responses %}
'201':
  description: "User created successfully"
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/User"
'409':
  description: "User already exists"
  content:
    application/json:
      schema:
        $ref: "#/components/schemas/Error"
{% endblock %}

# Additional user-specific actions
{% block user_specific_actions %}
- target: "$.paths./users/{id}"
  update:
    get:
      summary: "Get user by ID"
      parameters:
        - name: "id"
          in: "path"
          required: true
          schema:
            type: "integer"
      responses:
        '200':
          description: "User details"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/User"
{% endblock %}
```

## Step 6: Template Debugging and Optimization

### Template Debugging Techniques

```yaml
# overlays/debug-template.yaml
overlay: 1.0.0
info:
  title: Template Debugging Example
actions:
  # Debug variable values
  - target: "$.info.x-debug-info"
    update:
      template_variables:
        environment: "{{ environment }}"
        debug_mode: "{{ debug_mode | default('not set') }}"
        all_variables: {{ vars | to_json }}
      
      # Debug loops and conditions
      entity_count: {{ entities | length }}
      first_entity: "{{ entities[0].name if entities else 'no entities' }}"
      
      # Debug filters and functions
      current_time: "{{ now() }}"
      formatted_env: "{{ environment | upper }}"
      
      # Debug complex expressions
      {% set total_endpoints = 0 %}
      {% for entity in entities %}
        {% set total_endpoints = total_endpoints + (entity.methods | length) %}
      {% endfor %}
      total_endpoints: {{ total_endpoints }}
      
  # Conditional debugging output
  {% if debug_mode %}
  - target: "$.info.x-template-debug"
    update:
      jinja_environment:
        filters: {{ jinja_env.filters.keys() | list | to_json }}
        globals: {{ jinja_env.globals.keys() | list | to_json }}
      template_context:
        {% for key, value in vars.items() %}
        {{ key }}: "{{ value | string | truncate(100) }}"
        {% endfor %}
  {% endif %}
```

### Performance Optimization

```yaml
# overlays/optimized-template.yaml
overlay: 1.0.0
info:
  title: Performance Optimized Template
actions:
  # Pre-compute expensive operations
  {% set entity_map = {} %}
  {% for entity in entities %}
    {% set _ = entity_map.update({entity.name: entity}) %}
  {% endfor %}
  
  # Use efficient data structures
  {% set required_schemas = set() %}
  {% for endpoint in endpoints %}
    {% if endpoint.request_schema %}
      {% set _ = required_schemas.add(endpoint.request_schema) %}
    {% endif %}
    {% if endpoint.response_schema %}
      {% set _ = required_schemas.add(endpoint.response_schema) %}
    {% endif %}
  {% endfor %}
  
  # Generate only required schemas
  {% for schema_name in required_schemas %}
  {% set entity = entity_map[schema_name] %}
  - target: "$.components.schemas.{{ schema_name }}"
    update: {{ entity.schema | to_json }}
  {% endfor %}
  
  # Batch similar operations
  {% set server_updates = [] %}
  {% for region in regions %}
    {% set _ = server_updates.append({
      "url": region.url,
      "description": region.name + " server"
    }) %}
  {% endfor %}
  
  - target: "$.servers"
    update: {{ server_updates | to_json }}
    
  # Use template caching for repeated patterns
  {% macro cached_security_scheme(scheme_name, scheme_config) %}
    {% if not _security_cache %}
      {% set _security_cache = {} %}
    {% endif %}
    {% if scheme_name not in _security_cache %}
      {% set _ = _security_cache.update({scheme_name: scheme_config}) %}
    {% endif %}
    {{ _security_cache[scheme_name] | to_json }}
  {% endmacro %}
```

### Error Handling in Templates

```yaml
# overlays/error-handling.yaml
overlay: 1.0.0
info:
  title: Template Error Handling
actions:
  # Graceful degradation
  - target: "$.info.version"
    update: "{{ api_version | default('1.0.0') }}"
    
  # Error checking with meaningful messages
  {% if not entities %}
    {% set _ = error("No entities defined. Please provide entities configuration.") %}
  {% endif %}
  
  {% for entity in entities %}
    {% if not entity.name %}
      {% set _ = error("Entity at index " + loop.index0|string + " is missing name") %}
    {% endif %}
    {% if not entity.fields %}
      {% set _ = error("Entity '" + entity.name + "' has no fields defined") %}
    {% endif %}
  {% endfor %}
  
  # Safe property access
  - target: "$.info.contact"
    update:
      name: "{{ contact.name | default('API Team') }}"
      email: "{{ contact.email | default('api@example.com') }}"
      {% if contact and contact.url %}
      url: "{{ contact.url }}"
      {% endif %}
      
  # Validate environment-specific configuration
  {% if environment == "production" %}
    {% if not prod_config %}
      {% set _ = error("Production configuration is required for production environment") %}
    {% endif %}
    {% if not prod_config.security_enabled %}
      {% set _ = error("Security must be enabled in production") %}
    {% endif %}
  {% endif %}
  
  # Safe iteration with fallbacks
  {% for server in servers | default([]) %}
  - target: "$.servers[{{ loop.index0 }}]"
    update:
      url: "{{ server.url | default('http://localhost:8080') }}"
      description: "{{ server.description | default('Server ' + loop.index|string) }}"
  {% endfor %}
```

## Step 7: Real-World Advanced Examples

### Multi-Tenant API Configuration

```yaml
# overlays/multi-tenant.yaml
overlay: 1.0.0
info:
  title: Multi-Tenant API Configuration
actions:
  # Generate tenant-specific configurations
  {% for tenant in tenants %}
  - target: "$.info.x-tenants.{{ tenant.id }}"
    update:
      name: "{{ tenant.name }}"
      subdomain: "{{ tenant.subdomain }}"
      database: "{{ tenant.database_name }}"
      features: {{ tenant.enabled_features | to_json }}
      rate_limits:
        requests_per_minute: {{ tenant.rate_limit | default(1000) }}
        burst_limit: {{ tenant.burst_limit | default(100) }}
      
  # Generate tenant-specific endpoints if needed
  {% if tenant.custom_endpoints %}
  {% for endpoint in tenant.custom_endpoints %}
  - target: "$.paths./tenants/{{ tenant.id }}{{ endpoint.path }}"
    update:
      {{ endpoint.method | lower }}:
        summary: "{{ endpoint.summary }} ({{ tenant.name }})"
        x-tenant: "{{ tenant.id }}"
        responses:
          '200':
            description: "{{ endpoint.description }}"
  {% endfor %}
  {% endif %}
  {% endfor %}
  
  # Generate tenant-aware security
  - target: "$.components.securitySchemes.TenantAuth"
    update:
      type: "apiKey"
      in: "header"
      name: "X-Tenant-ID"
      description: "Tenant identifier for multi-tenant access"
      
  # Add tenant context to all endpoints
  {% for path, methods in existing_paths.items() %}
  {% for method in methods %}
  - target: "$.paths.{{ path }}.{{ method }}.parameters"
    update:
      {% if method in ['get', 'post', 'put', 'delete'] %}
      - name: "X-Tenant-ID"
        in: "header"
        required: true
        description: "Tenant identifier"
        schema:
          type: "string"
          enum: {{ tenants | map(attribute='id') | list | to_json }}
      {% endif %}
  {% endfor %}
  {% endfor %}
```

### Microservices API Gateway Configuration

```yaml
# overlays/api-gateway.yaml
overlay: 1.0.0
info:
  title: API Gateway Configuration
actions:
  # Generate service discovery information
  - target: "$.info.x-gateway-config"
    update:
      load_balancer: "{{ gateway.load_balancer | default('round_robin') }}"
      circuit_breaker:
        enabled: {{ gateway.circuit_breaker.enabled | default(true) }}
        failure_threshold: {{ gateway.circuit_breaker.failure_threshold | default(5) }}
        timeout: {{ gateway.circuit_breaker.timeout | default(30) }}
      rate_limiting:
        global_limit: {{ gateway.rate_limiting.global | default(10000) }}
        per_service_limit: {{ gateway.rate_limiting.per_service | default(1000) }}
        
  # Generate service routes
  {% for service in microservices %}
  - target: "$.paths.{{ service.base_path }}"
    update:
      x-gateway-service:
        name: "{{ service.name }}"
        upstream: "{{ service.upstream_url }}"
        health_check: "{{ service.health_check_path | default('/health') }}"
        timeout: {{ service.timeout | default(30) }}
        retries: {{ service.retries | default(3) }}
        weight: {{ service.weight | default(100) }}
        
  # Proxy all service endpoints
  {% for endpoint in service.endpoints %}
  - target: "$.paths.{{ service.base_path }}{{ endpoint.path }}"
    update:
      {{ endpoint.method | lower }}:
        summary: "{{ endpoint.summary }}"
        description: "{{ endpoint.description }} (proxied to {{ service.name }})"
        x-proxy-to: "{{ service.upstream_url }}{{ endpoint.path }}"
        x-service-name: "{{ service.name }}"
        
        # Add gateway-specific headers
        parameters:
          {% for param in endpoint.parameters | default([]) %}
          - {{ param | to_json }}
          {% endfor %}
          - name: "X-Service-Name"
            in: "header"
            schema:
              type: "string"
              default: "{{ service.name }}"
          - name: "X-Request-ID"
            in: "header"
            description: "Unique request identifier for tracing"
            schema:
              type: "string"
              format: "uuid"
              
        responses: {{ endpoint.responses | to_json }}
  {% endfor %}
  {% endfor %}
  
  # Generate aggregated health check
  - target: "$.paths./health"
    update:
      get:
        summary: "Gateway health check"
        description: "Aggregate health status of all services"
        responses:
          '200':
            description: "All services healthy"
            content:
              application/json:
                schema:
                  type: "object"
                  properties:
                    status:
                      type: "string"
                      example: "healthy"
                    services:
                      type: "object"
                      properties:
                        {% for service in microservices %}
                        {{ service.name }}:
                          type: "object"
                          properties:
                            status:
                              type: "string"
                              enum: ["healthy", "unhealthy", "unknown"]
                            response_time:
                              type: "number"
                              description: "Response time in milliseconds"
                            last_check:
                              type: "string"
                              format: "date-time"
                        {% endfor %}
```

## Best Practices for Advanced Templating

### 1. Template Organization

```
templates/
├── base/
│   ├── common-responses.yaml
│   ├── pagination.yaml
│   └── security-schemes.yaml
├── crud/
│   ├── base-crud.yaml
│   └── crud-with-search.yaml
├── features/
│   ├── analytics.yaml
│   ├── user-management.yaml
│   └── notifications.yaml
└── environments/
    ├── development.yaml
    ├── staging.yaml
    └── production.yaml
```

### 2. Variable Validation

```yaml
# At the beginning of templates
{% if not environment %}
  {% set _ = error("Environment variable is required") %}
{% endif %}

{% if environment not in ["development", "staging", "production"] %}
  {% set _ = error("Invalid environment: " + environment) %}
{% endif %}
```

### 3. Documentation in Templates

```yaml
{#
  Template: Advanced API Configuration
  Purpose: Generates comprehensive API configuration with dynamic features
  
  Required Variables:
  - environment: Target environment (development|staging|production)
  - api_version: API version string
  - features: Dictionary of feature flags
  
  Optional Variables:
  - debug_mode: Enable debug output (default: false)
  - custom_domains: Array of custom domain configurations
  
  Example Usage:
  oas-patch bundle apply api.yaml my-bundle --environment production
#}
```

### 4. Testing Templates

Create test configurations for template validation:

```bash
#!/bin/bash
# test-templates.sh

# Test with different variable combinations
echo "Testing development environment..."
oas-patch bundle apply base-api.yaml test-bundle \
  --environment development \
  --variable debug_mode=true \
  --variable test_data=true

echo "Testing production environment..."
oas-patch bundle apply base-api.yaml test-bundle \
  --environment production \
  --variable security_enabled=true \
  --variable monitoring_enabled=true

echo "Testing with minimal configuration..."
oas-patch bundle apply base-api.yaml test-bundle \
  --environment development
```

## Next Steps

With advanced templating mastered, you can:

1. Create sophisticated API configurations for complex architectures
2. Build reusable template libraries for your organization
3. Implement dynamic API generation based on business requirements
4. Integrate templates with CI/CD for automated API management

## Summary

In this tutorial, you learned:
- Advanced Jinja2 templating patterns and techniques
- Dynamic schema and endpoint generation
- Template organization with inheritance and includes
- Complex conditional logic and data transformations
- Debugging and optimization strategies
- Real-world examples for multi-tenant and microservices architectures

Advanced templating with OAS Patcher enables sophisticated, maintainable, and scalable API specification management for complex enterprise environments.
