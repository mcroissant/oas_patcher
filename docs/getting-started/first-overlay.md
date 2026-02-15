# Your First Overlay

This tutorial will guide you through creating your first overlay step by step. We'll start simple and gradually build up complexity using multiple small overlays.

## What You'll Learn


- Basic overlay structure and syntax
- How to target specific parts of an OpenAPI spec
- Using multiple overlays together
- When you might need bundle management (coming next!)

## Step 1: Your Starting API

Let's start with a simple bookstore API (`bookstore.yaml`):

```yaml
openapi: 3.0.3
info:
  title: Bookstore API
  version: 1.0.0
paths:
  /books:
    get:
      summary: List books
      responses:
        '200':
          description: Success
```

This API works, but it's missing some important details. Let's improve it step by step using overlays.

## Step 2: Your First Simple Overlay

Let's create our first overlay to add a server URL. Create `01-add-servers.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Add Server
  version: 1.0.0
actions:
  - target: "$"
    update:
        servers:
          - url: "https://api.bookstore.com"
            description: "Production server"
```

### Breaking It Down

- **overlay: 1.0.0** - The overlay format version (use 1.1.0 for copy action support)
- **info** - Metadata about this overlay
- **actions** - The changes to make
- **target: "$"** - Where to make the change (JSONPath), one specificity here is that the path you want to update needs to exist so $.servers wouldn't work
- **update** - What to put there

### Apply the Overlay

```bash
oas-patch overlay bookstore.yaml 01-add-servers.yaml --output bookstore-with-server.yaml
```

Now your API has a server! Check the result:

```yaml
openapi: 3.0.3
info:
  title: Bookstore API
  version: 1.0.0
paths:
  /books:
    get:
      summary: List books
      responses:
        '200':
          description: Success
servers:
- url: https://api.bookstore.com
  description: Production server
```

## Step 3: Add Better Documentation

Create a second overlay `02-improve-info.yaml`:

```yaml
overlay: 1.0.0
info:
  title: Improve Documentation
  version: 1.0.0
actions:
  - target: "$.info"
    update: 
      description: "A simple API for managing books in our bookstore"
  - target: "$.info"
    update:
      contact:
        name: "API Support"
        email: "support@bookstore.com"
```

Apply this to your previous result:

```bash
oas-patch overlay bookstore-with-server.yaml 02-improve-info.yaml --output api-documented.yaml
```

## Step 4: Add Security

Create `03-add-security.yaml` to add API key authentication:

```yaml
overlay: 1.0.0
info:
  title: Add API Key Security
  version: 1.0.0
actions:
  # Add security scheme definition
  - target: "$"
    update:
      components:
        securitySchemes:
            ApiKeyAuth:
              type: "apiKey"
              in: "header"
              name: "X-API-Key"

  # Apply security to the books endpoint
  - target: "$.paths.['/books'].get"
    update:
      security:
        - ApiKeyAuth: []
```

Apply it:

```bash
oas-patch overlay api-documented.yaml 03-add-security.yaml --output api-complete.yaml
```

## Step 5: Using Copy Action (Overlay 1.1)

If you're using Overlay 1.1, you can use the powerful `copy` action to duplicate schemas. This is especially useful when you need schema variations:

Create `04-add-audiobook-schema.yaml`:

```yaml
overlay: 1.1.0
info:
  title: Add Audiobook Schema via Copy
  version: 1.0.0
  description: Demonstrates the copy action feature
actions:
  # First, ensure we have a Book schema
  - target: "$.components.schemas"
    update:
      Book:
        type: object
        properties:
          id:
            type: integer
          title:
            type: string
          author:
            type: string
  
  # Now copy Book to create Audiobook (automatically created)
  - target: "$.components.schemas.Audiobook"
    copy: "$.components.schemas.Book"
    description: "Copy Book schema to Audiobook"
  
  # Customize the Audiobook schema
  - target: "$.components.schemas.Audiobook.properties"
    update:
      narrator:
        type: string
      duration:
        type: integer
        description: "Duration in minutes"
```

The copy action automatically creates the target if it doesn't exist, making it much simpler than manually duplicating schemas!

## Step 6: The Problem with Multiple Commands

You might have noticed we're running multiple commands and managing intermediate files:

1. `api.yaml` → `api-with-server.yaml` (add server)
2. `api-with-server.yaml` → `api-documented.yaml` (improve docs)  
3. `api-documented.yaml` → `api-complete.yaml` (add endpoint)

This gets messy quickly! What if you want to:
- Apply overlays in a different order?
- Skip certain overlays for different environments?
- Share your configuration with teammates?

## What's Next?

You've learned the basics of overlays! But as your API grows, you'll want:

- **Different configurations for different environments** (dev, staging, prod)
- **Easy way to manage multiple overlays** as a group
- **Variable substitution** for environment-specific values
- **Reusable configurations** you can share with your team

This is where **bundles** come in! In the next section, we'll learn how bundles solve these problems and make overlay management much easier.

## Summary

In this tutorial, you learned:

✅ **Basic overlay structure** - Every overlay needs `overlay`, `info`, and `actions`  
✅ **JSONPath targeting** - Use `$.path.to.property` to target specific locations  
✅ **Update operations** - Replace or add content with `update`  
✅ **Copy action (1.1)** - Duplicate schemas and components with `copy`  
✅ **Multiple overlays** - Apply several overlays to build up changes gradually  


### Next Steps

Ready to learn about bundles? Continue to **[Bundle Management](../core-concepts/bundles.md)** to see how to organize and manage your overlays more effectively!



## Key Takeaways

### Best Practices You Applied

1. **Incremental Changes**: Built the overlay step by step
2. **Proper Targeting**: Used specific JSONPath expressions
3. **Reusable Components**: Created schemas that can be referenced

### Common Patterns

- **Root Updates**: Use `"$"` to add new top-level sections
- **Object Updates**: Use `"$.path.to.object"` to modify specific objects

## Next Steps

Now that you've created your first overlay:

1. **Practice**: Try creating overlays for different scenarios
2. **Learn Bundles**: Organize multiple overlays with [Bundle Management](../core-concepts/bundles.md)
3. **Add Templates**: Use dynamic content with [Template Engine](../core-concepts/templates.md)
