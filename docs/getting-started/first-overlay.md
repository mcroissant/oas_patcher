# Your First Overlay

This tutorial will guide you through creating your first overlay from scratch. You'll learn the overlay format, target selection, and best practices.

## What You'll Build

We'll create an overlay that transforms a basic API specification to add:
- Production server configuration
- API versioning
- Security requirements
- Enhanced documentation

## Step 1: Understanding the Source API

Let's start with this OpenAPI specification (`bookstore-api.yaml`):

```yaml
openapi: 3.0.3
info:
  title: Bookstore API
  version: 1.0.0
paths:
  /books:
    get:
      summary: Get all books
      responses:
        '200':
          description: List of books
  /books/{id}:
    get:
      summary: Get book by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Book details
        '404':
          description: Book not found
```

**Issues with this API:**
- No server configuration
- Missing detailed documentation
- No security
- Basic error responses

## Step 2: Plan Your Overlay

Before writing the overlay, let's plan what we want to change:

1. **Add servers** for different environments
2. **Enhance info section** with description, contact, license
3. **Add security scheme** (API key authentication)
4. **Improve error responses** with proper schemas
5. **Add examples** to responses

## Step 3: Create the Overlay Structure

Create `bookstore-enhancement-overlay.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Bookstore API Enhancement Overlay
  version: 1.0.0
  description: Enhances the bookstore API with production-ready features
actions:
  # We'll add actions here step by step
```

## Step 4: Add Server Configuration

Let's add production and staging servers:

```yaml
overlay: 1.0.0
info:
  title: Bookstore API Enhancement Overlay
  version: 1.0.0
  description: Enhances the bookstore API with production-ready features
actions:
  # Add servers (since original has none, we just add them)
  - target: "$"
    update:
      servers:
        - url: https://api.bookstore.com/v1
          description: Production server
        - url: https://staging-api.bookstore.com/v1
          description: Staging server
        - url: http://localhost:3000/v1
          description: Development server
```

### Understanding This Action

- **target: "$"** - Targets the root of the OpenAPI document
- **update:** - Adds or updates the specified content
- **servers:** - Adds a servers array to the root

## Step 5: Enhance API Information

Now let's improve the info section:

```yaml
overlay: 1.0.0
info:
  title: Bookstore API Enhancement Overlay
  version: 1.0.0
  description: Enhances the bookstore API with production-ready features
actions:
  # Add servers
  - target: "$"
    update:
      servers:
        - url: https://api.bookstore.com/v1
          description: Production server
        - url: https://staging-api.bookstore.com/v1
          description: Staging server
        - url: http://localhost:3000/v1
          description: Development server

  # Enhance API information
  - target: "$.info"
    update:
      description: "A comprehensive API for managing bookstore operations including inventory, orders, and customer management."
      version: "2.0.0"
      termsOfService: "https://bookstore.com/terms"
      contact:
        name: "Bookstore API Support"
        url: "https://bookstore.com/support"
        email: "api-support@bookstore.com"
      license:
        name: "MIT"
        url: "https://opensource.org/licenses/MIT"
```

### Understanding This Action

- **target: "$.info"** - Targets the info object specifically
- **update:** - Merges new properties with existing ones
- The original title stays, but other properties are added or updated

## Step 6: Add Security Configuration

Add API key authentication:

```yaml
  # Add security components
  - target: "$"
    update:
      components:
        securitySchemes:
          ApiKeyAuth:
            type: apiKey
            in: header
            name: X-API-Key
            description: "API key for accessing bookstore resources"
        schemas:
          Error:
            type: object
            required:
              - code
              - message
            properties:
              code:
                type: integer
                format: int32
                description: Error code
              message:
                type: string
                description: Error message
              details:
                type: string
                description: Additional error details
```

## Step 7: Apply Security to Endpoints

Now apply security requirements to our endpoints:

```yaml
  # Add security to GET /books
  - target: "$.paths./books.get"
    update:
      security:
        - ApiKeyAuth: []
      description: "Retrieve a paginated list of all books in the bookstore inventory"
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: limit
          in: query
          description: Number of books per page
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100

  # Add security to GET /books/{id}
  - target: "$.paths./books/{id}.get"
    update:
      security:
        - ApiKeyAuth: []
      description: "Retrieve detailed information about a specific book by its unique identifier"
```

## Step 8: Enhance Response Schemas

Let's improve the responses with proper schemas:

```yaml
  # Enhance the GET /books response
  - target: "$.paths./books.get.responses.200"
    update:
      description: "Successfully retrieved list of books"
      content:
        application/json:
          schema:
            type: object
            properties:
              books:
                type: array
                items:
                  $ref: "#/components/schemas/Book"
              pagination:
                type: object
                properties:
                  page:
                    type: integer
                  limit:
                    type: integer
                  total:
                    type: integer
                  totalPages:
                    type: integer
          example:
            books:
              - id: "1"
                title: "The Great Gatsby"
                author: "F. Scott Fitzgerald"
                isbn: "978-0-7432-7356-5"
                price: 12.99
                stock: 15
              - id: "2"
                title: "To Kill a Mockingbird"
                author: "Harper Lee"
                isbn: "978-0-06-112008-4"
                price: 14.99
                stock: 8
            pagination:
              page: 1
              limit: 20
              total: 156
              totalPages: 8

  # Add Book schema to components
  - target: "$.components.schemas"
    update:
      Book:
        type: object
        required:
          - id
          - title
          - author
          - price
        properties:
          id:
            type: string
            description: Unique identifier for the book
          title:
            type: string
            description: Title of the book
          author:
            type: string
            description: Author of the book
          isbn:
            type: string
            description: ISBN number
          price:
            type: number
            format: float
            description: Price in USD
          stock:
            type: integer
            description: Number of copies in stock
          genre:
            type: string
            description: Book genre
          publishedDate:
            type: string
            format: date
            description: Publication date
```

## Step 9: Add Error Responses

Improve error handling:

```yaml
  # Add error responses to GET /books
  - target: "$.paths./books.get.responses"
    update:
      '400':
        description: "Bad request - invalid parameters"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
            example:
              code: 400
              message: "Invalid pagination parameters"
              details: "Page must be greater than 0"
      '401':
        description: "Unauthorized - invalid or missing API key"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
            example:
              code: 401
              message: "Invalid API key"
      '500':
        description: "Internal server error"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"

  # Add error responses to GET /books/{id}
  - target: "$.paths./books/{id}.get.responses"
    update:
      '400':
        description: "Bad request - invalid book ID format"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      '401':
        description: "Unauthorized - invalid or missing API key"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
      '500':
        description: "Internal server error"
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/Error"
```

## Step 10: Complete Overlay File

Here's the complete overlay file:

```yaml
overlay: 1.0.0
info:
  title: Bookstore API Enhancement Overlay
  version: 1.0.0
  description: Enhances the bookstore API with production-ready features
actions:
  # Add servers configuration
  - target: "$"
    update:
      servers:
        - url: https://api.bookstore.com/v1
          description: Production server
        - url: https://staging-api.bookstore.com/v1
          description: Staging server
        - url: http://localhost:3000/v1
          description: Development server

  # Enhance API information
  - target: "$.info"
    update:
      description: "A comprehensive API for managing bookstore operations including inventory, orders, and customer management."
      version: "2.0.0"
      termsOfService: "https://bookstore.com/terms"
      contact:
        name: "Bookstore API Support"
        url: "https://bookstore.com/support"
        email: "api-support@bookstore.com"
      license:
        name: "MIT"
        url: "https://opensource.org/licenses/MIT"

  # Add security components and schemas
  - target: "$"
    update:
      components:
        securitySchemes:
          ApiKeyAuth:
            type: apiKey
            in: header
            name: X-API-Key
            description: "API key for accessing bookstore resources"
        schemas:
          Book:
            type: object
            required:
              - id
              - title
              - author
              - price
            properties:
              id:
                type: string
                description: Unique identifier for the book
              title:
                type: string
                description: Title of the book
              author:
                type: string
                description: Author of the book
              isbn:
                type: string
                description: ISBN number
              price:
                type: number
                format: float
                description: Price in USD
              stock:
                type: integer
                description: Number of copies in stock
              genre:
                type: string
                description: Book genre
              publishedDate:
                type: string
                format: date
                description: Publication date
          Error:
            type: object
            required:
              - code
              - message
            properties:
              code:
                type: integer
                format: int32
                description: Error code
              message:
                type: string
                description: Error message
              details:
                type: string
                description: Additional error details

  # Enhance GET /books endpoint
  - target: "$.paths./books.get"
    update:
      security:
        - ApiKeyAuth: []
      description: "Retrieve a paginated list of all books in the bookstore inventory"
      parameters:
        - name: page
          in: query
          description: Page number for pagination
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: limit
          in: query
          description: Number of books per page
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 100
      responses:
        '200':
          description: "Successfully retrieved list of books"
          content:
            application/json:
              schema:
                type: object
                properties:
                  books:
                    type: array
                    items:
                      $ref: "#/components/schemas/Book"
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                      limit:
                        type: integer
                      total:
                        type: integer
                      totalPages:
                        type: integer
              example:
                books:
                  - id: "1"
                    title: "The Great Gatsby"
                    author: "F. Scott Fitzgerald"
                    isbn: "978-0-7432-7356-5"
                    price: 12.99
                    stock: 15
                pagination:
                  page: 1
                  limit: 20
                  total: 156
                  totalPages: 8
        '400':
          description: "Bad request - invalid parameters"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
        '401':
          description: "Unauthorized - invalid or missing API key"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
        '500':
          description: "Internal server error"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"

  # Enhance GET /books/{id} endpoint
  - target: "$.paths./books/{id}.get"
    update:
      security:
        - ApiKeyAuth: []
      description: "Retrieve detailed information about a specific book by its unique identifier"
      responses:
        '200':
          description: "Successfully retrieved book details"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Book"
              example:
                id: "1"
                title: "The Great Gatsby"
                author: "F. Scott Fitzgerald"
                isbn: "978-0-7432-7356-5"
                price: 12.99
                stock: 15
                genre: "Classic Literature"
                publishedDate: "1925-04-10"
        '400':
          description: "Bad request - invalid book ID format"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
        '401':
          description: "Unauthorized - invalid or missing API key"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
        '404':
          description: "Book not found"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
              example:
                code: 404
                message: "Book not found"
                details: "No book exists with the provided ID"
        '500':
          description: "Internal server error"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Error"
```

## Step 11: Apply and Test

Apply your overlay:

```bash
oas-patch overlay bookstore-api.yaml bookstore-enhancement-overlay.yaml -o enhanced-bookstore-api.yaml
```

Validate the result:

```bash
oas-patch validate enhanced-bookstore-api.yaml --format yaml
```

## What You've Learned

🎯 **Overlay Structure**: How to organize actions in an overlay  
🔍 **Target Selection**: Using JSONPath to target specific parts of the API  
🛡️ **Security Enhancement**: Adding authentication and proper error handling  
📚 **Documentation**: Improving API documentation with descriptions and examples  
🏗️ **Schema Design**: Creating reusable components and schemas  

## Key Takeaways

### Best Practices You Applied

1. **Incremental Changes**: Built the overlay step by step
2. **Proper Targeting**: Used specific JSONPath expressions
3. **Reusable Components**: Created schemas that can be referenced
4. **Complete Documentation**: Added descriptions and examples
5. **Error Handling**: Included comprehensive error responses

### Common Patterns

- **Root Updates**: Use `"$"` to add new top-level sections
- **Object Updates**: Use `"$.path.to.object"` to modify specific objects
- **Component References**: Use `$ref` to reference reusable schemas
- **Security Application**: Apply security at the operation level

## Next Steps

Now that you've created your first overlay:

1. **Practice**: Try creating overlays for different scenarios
2. **Learn Bundles**: Organize multiple overlays with [Bundle Management](../core-concepts/bundles.md)
3. **Add Templates**: Use dynamic content with [Template Engine](../core-concepts/templates.md)
4. **Explore Examples**: Check out [real-world examples](../examples/simple-modifications.md)

## Troubleshooting

**Overlay not applying?**
- Check JSONPath syntax with `oas-patch validate`
- Verify target paths exist in the source document
- Use `--format yaml` for detailed validation output

**Unexpected results?**
- Remember that updates merge with existing content
- Use `remove: true` before adding new content if needed
- Check the order of actions in your overlay

---

**Congratulations!** You've successfully created a comprehensive overlay. Continue with [Bundle Management](../core-concepts/bundles.md) to learn how to organize multiple overlays.
