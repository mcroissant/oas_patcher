# OAS Patcher Documentation

Welcome to the comprehensive documentation for **OAS Patcher** - a powerful command-line tool and Python library for working with OpenAPI Specification (OAS) Overlays.

## What is OAS Patcher?

OAS Patcher enables you to modify, enhance, and manage OpenAPI specifications using a declarative overlay approach. Instead of manually editing large OpenAPI files, you can create small, focused overlay files that describe the changes you want to make.

### Key Features

🎯 **Overlay System** - Apply targeted modifications to OpenAPI documents without editing the source  
📦 **Bundle Management** - Organize multiple overlays into reusable bundles  
🌍 **Environment Support** - Apply different configurations for dev, staging, production  
🔧 **Template Engine** - Use variables and dynamic content with Jinja2 templating  
🌐 **Environment Variables** - Integrate with CI/CD pipelines using environment variables  
✅ **Validation** - Comprehensive validation for overlays and configurations  
⚡ **CLI & API** - Use from command line or integrate into Python applications  

## Why Use OAS Patcher?

### Problems It Solves

- **API Evolution**: Modify APIs across different environments without duplicating specification files
- **CI/CD Integration**: Automatically apply environment-specific configurations during deployment
- **Documentation Maintenance**: Keep API documentation in sync across multiple versions
- **Configuration Management**: Centralize API configuration with environment-specific overrides

### Real-World Use Cases

- **Multi-Environment Deployments**: Different server URLs, authentication schemes per environment
- **Security Updates**: Update authentication methods or add new security schemes to keep wour documentation in sync with the changes your api gateway introduces
- **API Versioning**: Add new endpoints or modify existing ones for new API versions
- **Documentation Enhancement**: Add examples, descriptions, or additional metadata
- **Compliance Requirements**: Add regulatory information or compliance metadata

## Quick Example

Here's a simple example of how OAS Patcher works:

**Original OpenAPI** (`api.yaml`):
```yaml
openapi: 3.0.3
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get users
      responses:
        '200':
          description: List of users
```

**Overlay** (`production-overlay.yaml`):
```yaml
overlay: 1.0.0
info:
  title: Production Environment Overlay
  version: 1.0.0
actions:
  - target: "$"
    update:
      servers:
        - url: https://api.production.com
          description: Production server
  - target: "$.info"
    update:
      description: "Production API - Built {{ env('BUILD_TIME', 'unknown') }}"
```

**Apply the overlay**:
```bash
oas-patch overlay api.yaml production-overlay.yaml -o production-api.yaml
```

**Result**: Your API specification now includes production servers and build information!

## Getting Started

Ready to get started? Follow these steps:

1. [**Install OAS Patcher**](getting-started/installation.md) - Get up and running in minutes
2. [**Quick Start Guide**](getting-started/quick-start.md) - Your first overlay in 5 minutes
3. [**Create Your First Overlay**](getting-started/first-overlay.md) - Step-by-step tutorial


## Community and Support

- **GitHub**: [oas-patcher](https://github.com/your-org/oas-patcher) - Report issues and contribute
- **Documentation**: This GitBook - Comprehensive guides and references
- **Examples**: [Example Repository](examples/) - Real-world use cases and templates

## What's Next?

- [Install OAS Patcher](getting-started/installation.md) to get started
- Learn about [Core Concepts](core-concepts/overlays.md) to understand the fundamentals
- Explore [Tutorials](tutorials/basic-overlay.md) for hands-on learning
- Check out [Examples](examples/simple-modifications.md) for real-world scenarios

---

*Let's make API management easier, one overlay at a time!* 🚀
