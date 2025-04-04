# OpenAPI Specification Patcher

The OpenAPI Specification Patcher (oas-patch) is a command-line utility that allows you to programmatically modify or update OpenAPI specifications using [overlay documents](https://github.com/OAI/Overlay-Specification) . It supports both YAML and JSON formats and provides powerful JSONPath-based targeting for updates and removals.

## Features
- **JSONPath Support**: Use JSONPath expressions to target specific parts of your OpenAPI document.
- **Flexible Updates**: Apply updates or remove elements from your OpenAPI specification.
- **YAML and JSON Support**: Works seamlessly with both YAML and JSON OpenAPI documents.
- **Sanitization**: Optionally remove special characters from your OpenAPI document.

## Prerequisites
- Python 3.7 or higher
- `pip` for managing Python packages

## Installation

## Install from Pypi
```bash
pip install oas-patch
```

### Install from Source for development
Clone the repository and install the tool locally:
```bash
git clone https://github.com/mcroissant/oas_patcher
pip install -e .
```

## Usage
The tool provides a simple CLI for applying overlays to OpenAPI documents.


### Example Usage
Apply an overlay to an OpenAPI document and save the result:
```bash
oas-patch overlay openapi.yaml overlay.yaml --output modified_openapi.yaml
```

Apply an overlay and print the result to the console:
```bash
oas-patch overlay openapi.json overlay.json
```

Sanitize the OpenAPI document while applying the overlay:
```bash
oas-patch overlay openapi.yaml overlay.yaml --sanitize
```

## Overlay examples
You can find varios overlay examples in the tests/samples folder.
The jsonpath mapping is based on [jsonpath-ng](https://github.com/h2non/jsonpath-ng/tree/master) with the extensions included.

```Yaml
overlay: 1.0.0
info:
  title: Update petstore API
  version: 1.0.0
actions:
  - target: $.info
    update:
      title: OAS Patched Petstore API
  - target: $.info.contact
    remove: true
  - target: $.info.license
    update:
      name: MIT
  - target: $.tags[?@.name == 'pet']
    update:
      description: This is the new description for the pet tag
  - target: $.tags[?@.name == 'store']
    remove: true
  - target: $.tags
    update:
      - name: newTag
        description: This is a new tag
  - target: $.components
    update:
      securitySchemes: 
        ApiAuth:
          type: apiKey
          in: header
          name: X-Api-Key 
        BearerAuth:
          type: http
          scheme: bearer    
  - target: $.servers.*.url
    update: 
      https://myapi.com/v1
  - target: $.paths["/pet/findByStatus"].get.security
    update: 
      BearerAuth: []
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a clear description of your changes.

### Running Tests
To run the tests, install the development dependencies and execute the test suite:
```bash
pip install -r requirements-dev.txt
pytest
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
This tool was inspired by the need to programmatically manage OpenAPI specifications in a flexible and reusable way. Special thanks to the open-source community for their contributions to JSONPath and YAML parsing libraries.