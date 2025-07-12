# OAS Patcher Documentation

Welcome to the comprehensive documentation for **OAS Patcher** - a powerful tool for applying overlays to OpenAPI specifications using the standardized OpenAPI Overlay format.

## What is OAS Patcher?

OAS Patcher allows you to modify and enhance OpenAPI specifications without directly editing the source files. Using the [OpenAPI Overlay specification](https://spec.openapis.org/overlay/v1.0.0), you can:

- **Add or modify** any part of an OpenAPI specification
- **Manage multiple environments** with different configurations
- **Use templates and variables** for dynamic content generation
- **Organize changes** into reusable, shareable overlays
- **Automate API documentation** in CI/CD pipelines

## Key Features

!!! tip "Why Use OAS Patcher?"
    
    - ✅ **Standards-based** - Uses the official OpenAPI Overlay specification
    - ✅ **Environment-aware** - Different configurations for dev, staging, production
    - ✅ **Template support** - Jinja2 templating with environment variables
    - ✅ **Bundle management** - Organize and apply multiple overlays together
    - ✅ **CI/CD ready** - Perfect for automated documentation workflows
    - ✅ **Validation built-in** - Ensures your modifications create valid OpenAPI specs

## Quick Example

Transform this basic API:

```yaml title="api.yaml"
openapi: 3.0.3
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
```

With this simple overlay:

```yaml title="add-server.yaml"
overlay: 1.0.0
info:
  title: Add Production Server
  version: 1.0.0
actions:
  - target: "$.servers"
    update:
      - url: "https://api.example.com"
        description: "Production server"
```

Using one command:

```bash
oas-patcher apply --input api.yaml --overlay add-server.yaml --output result.yaml
```

## The Power of Bundles

While single overlays are useful, **bundles** unlock the true potential of OAS Patcher. A bundle is a collection of overlays that work together to transform your API specification in coordinated ways.

### Why Bundles Matter

- **🎯 Coordinated Changes** - Multiple overlays work together seamlessly
- **🔄 Reusability** - Save and share complete API transformation recipes  
- **🏗️ Environment Management** - Different bundles for dev, staging, production
- **⚡ Efficiency** - Apply complex transformations with a single command
- **🔐 Consistency** - Ensure the same changes are applied every time

### Real-World Bundle Examples

```yaml title="production-ready.yaml"
    name: "production-api-bundle"
    description: "Production environment configuration for the API"
    version: "1.2.0"

    # Global variables available to all overlays
    variables:
    api_version: "v2"
    company_name: "Acme Corp"
    support_email: "support@acme.com"

    # Overlay definitions
    overlays:
    - path: "overlays/base.yaml"
        description: "Base configuration updates"
        
    - path: "overlays/security.yaml"
        description: "Security and authentication server details"
        environment: ["production", "staging"]
        
    - path: "overlays/add-x-extensions.yaml"
        description: "Adding rate-limit extensions"
        environment: ["production"]
        variables:
            monitoring_endpoint: "https://metrics.acme.com"
```

Think of bundles as **recipes** for your API transformations - they capture the complete process of taking a base API specification and preparing it for specific environments or use cases.

## Getting Started

Ready to get started? Follow our step-by-step guides:

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick Start__

    ---

    Get up and running with OAS Patcher in minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quick-start.md)

-   :material-school:{ .lg .middle } __First Overlay__

    ---

    Learn the basics by creating your first overlay

    [:octicons-arrow-right-24: Your First Overlay](getting-started/first-overlay.md)

-   :material-book-open:{ .lg .middle } __Core Concepts__

    ---

    Understand overlays, bundles, and templates

    [:octicons-arrow-right-24: Core Concepts](core-concepts/overlays.md)

-   :material-rocket-launch:{ .lg .middle } __Examples__

    ---

    Real-world examples and use cases

    [:octicons-arrow-right-24: Examples](examples/README.md)

</div>

## Use Cases

OAS Patcher is perfect for:

### API Development Teams
- **Version management** - Maintain different API versions from a single source
- **Environment configuration** - Different server URLs, security schemes per environment
- **Documentation enhancement** - Add examples, descriptions, and metadata

### DevOps Engineers  
- **CI/CD integration** - Automate API spec generation and deployment
- **Configuration management** - Manage API configurations across environments
- **Quality assurance** - Validate and enhance API specifications

### API Architects
- **Standards enforcement** - Apply consistent patterns across APIs
- **Security enhancement** - Add authentication and authorization schemes
- **Documentation consistency** - Ensure all APIs follow documentation standards

## Community and Support

- **GitHub Repository**: [oas-patcher](https://github.com/example/oas-patcher)
- **Issue Tracker**: [Report bugs and request features](https://github.com/example/oas-patcher/issues)
- **Discussions**: [Ask questions and share tips](https://github.com/example/oas-patcher/discussions)
- **PyPI Package**: [pip install oas-patcher](https://pypi.org/project/oas-patcher/)

## License

OAS Patcher is open source software licensed under the [MIT License](https://opensource.org/licenses/MIT).
