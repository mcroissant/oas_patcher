# Examples

This section provides practical, real-world examples of using OAS Patcher for common API specification scenarios. Each example includes complete working code and explanations.

## Quick Reference

- **[API Versioning](./api-versioning.md)** - Managing multiple API versions
- **[Authentication Setup](./authentication.md)** - Adding security schemes
- **[Server Configuration](./server-config.md)** - Environment-specific server settings
- **[Response Enhancement](./response-enhancement.md)** - Improving response documentation
- **[Rate Limiting](./rate-limiting.md)** - Adding rate limiting specifications
- **[CORS Configuration](./cors-config.md)** - Cross-origin resource sharing setup
- **[Error Handling](./error-handling.md)** - Standardizing error responses
- **[Webhooks](./webhooks.md)** - Adding webhook specifications
- **[Monitoring Integration](./monitoring.md)** - Adding observability endpoints
- **[Legacy Migration](./legacy-migration.md)** - Modernizing older API specs

## Getting Started

Choose an example that matches your use case:

### Basic Modifications
Start with simple changes like updating titles, descriptions, or server URLs.
→ See [Server Configuration](./server-config.md)

### Security Implementation
Add authentication and authorization to your API.
→ See [Authentication Setup](./authentication.md)

### Multi-Environment Setup
Configure your API for different deployment environments.
→ See [API Versioning](./api-versioning.md)

### Advanced Scenarios
Complex modifications like adding monitoring, webhooks, or legacy migration.
→ See [Monitoring Integration](./monitoring.md)

## Example Structure

Each example follows this structure:

1. **Scenario Description** - What problem we're solving
2. **Input Files** - Starting OpenAPI specification
3. **Overlay Configuration** - The overlay file(s) needed
4. **Command Usage** - How to apply the overlay
5. **Expected Output** - The resulting specification
6. **Variations** - Alternative approaches or extensions
7. **Best Practices** - Tips and recommendations

## Prerequisites

Before running these examples, ensure you have:

- OAS Patcher installed (`pip install oas-patcher`)
- Basic understanding of OpenAPI specifications
- Familiarity with YAML syntax
- Understanding of JSONPath expressions

## File Organization

Examples include these file types:

```
example-name/
├── input.yaml          # Original OpenAPI spec
├── overlay.yaml        # Primary overlay file
├── expected.yaml       # Expected output
├── bundle.yml          # Bundle configuration (if applicable)
├── .env.example        # Environment variables template
└── README.md          # Detailed explanation
```

## Common Patterns

### Simple Value Updates
```yaml
# Update a simple field
- target: "$.info.title"
  update: "My Updated API"
```

### Adding New Sections
```yaml
# Add a new security scheme
- target: "$.components.securitySchemes.bearerAuth"
  update:
    type: http
    scheme: bearer
```

### Environment Variables
```yaml
# Use environment variables
- target: "$.servers[0].url"
  update: "{{ API_BASE_URL }}"
```

### Conditional Logic
```yaml
# Add debug info only in development
- target: "$.info.x-debug"
  update: "{{ 'enabled' if DEBUG_MODE == 'true' else 'disabled' }}"
```

## Tips for Success

1. **Start Small** - Begin with simple overlays and gradually add complexity
2. **Test Incrementally** - Validate each change before adding more
3. **Use Version Control** - Track changes to both specs and overlays
4. **Document Changes** - Include descriptions in your overlay actions
5. **Validate Output** - Always validate the resulting OpenAPI specification

## Contributing Examples

Have a useful example to share? We welcome contributions! Please:

1. Follow the standard example structure
2. Include complete, working files
3. Add clear documentation
4. Test the example thoroughly
5. Submit a pull request

## Support

If you have questions about these examples or need help with a specific use case:

- Check the [Troubleshooting Guide](../troubleshooting/common-issues.md)
- Review the [CLI Reference](../cli-reference/overview.md)
- Open an issue on the project repository
