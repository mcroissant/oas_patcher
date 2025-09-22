# OAS Patcher

A powerful command-line tool and Python library for working with OpenAPI Specification (OAS) Overlays. Modify and enhance your OpenAPI documents using a declarative overlay approach - no manual editing of large spec files needed!

[![Documentation](https://img.shields.io/badge/docs-online-blue)](https://mcroissant.github.io/oas_patcher/)
[![PyPI version](https://badge.fury.io/py/oas-patch.svg)](https://badge.fury.io/py/oas-patch)

> **Try it now:** [Online Demo](https://vbtn4932y3.execute-api.us-east-1.amazonaws.com/dev/)

## Key Features

🎯 **Overlay System** - Apply targeted modifications to OpenAPI documents  
📦 **Bundle Management** - Organize multiple overlays into reusable bundles  
🌍 **Environment Support** - Different configurations for dev, staging, production  
🔧 **Template Engine** - Use variables and dynamic content with Jinja2  
✅ **Validation** - Comprehensive validation for overlays and configurations  

[View all features in documentation →](https://mcroissant.github.io/oas_patcher/core-concepts/overlays/)

## Quick Start

### Installation

```bash
pip install oas-patch
```

### Basic Usage

1. **Apply an Overlay**
```bash
oas-patch overlay openapi.yaml overlay.yaml -o modified.yaml
```

2. **Generate an Overlay (Diff)**
```bash
oas-patch diff original.yaml modified.yaml -o overlay.yaml
```

3. **Validate an Overlay**
```bash
oas-patch validate overlay.yaml
```

[View full CLI reference →](https://mcroissant.github.io/oas_patcher/cli-reference/overview/)

## Example

```yaml
# overlay.yaml
overlay: 1.0.0
info:
  title: Production Environment Overlay
actions:
  - target: "$"
    update:
      servers:
        - url: https://api.production.com
```

[More examples →](https://mcroissant.github.io/oas_patcher/examples/)

## Documentation

- 📚 [Full Documentation](https://mcroissant.github.io/oas_patcher/)
- 🚀 [Getting Started Guide](https://mcroissant.github.io/oas_patcher/getting-started/quick-start/)
- 💡 [Core Concepts](https://mcroissant.github.io/oas_patcher/core-concepts/overlays/)
- 📖 [API Reference](https://mcroissant.github.io/oas_patcher/api-reference/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
