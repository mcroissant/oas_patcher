# OAS Patcher

A command-line tool for working with OpenAPI Specification (OAS) Overlays, allowing you to patch and modify OpenAPI documents.

> **NOTE**  try it now :   [Online Demo](http://test-453444549.us-west-2.elb.amazonaws.com:8081/)



## Features

- Apply OpenAPI Overlays to existing OpenAPI documents
- Generate overlay files by comparing two OpenAPI documents
- Validate OpenAPI Overlay documents against the specification

## Installation

```bash
pip install oas-patch
```

## Usage

### Apply an Overlay

Apply changes from an overlay file to an OpenAPI document:

```bash
oas-patch overlay openapi.yaml overlay.yaml -o modified.yaml
```

Options:
- `-o, --output`: Path to save the modified OpenAPI document (optional, defaults to stdout)
- `--sanitize`: Remove special characters from the OpenAPI document

### Generate an Overlay (Diff)

Create an overlay file by comparing two OpenAPI documents:

```bash
oas-patch diff original.yaml modified.yaml -o overlay.yaml
```

Options:
- `-o, --output`: Path to save the generated overlay file (optional, defaults to stdout)

### Validate an Overlay

Validate an OpenAPI Overlay document against the specification:

```bash
oas-patch validate overlay.yaml --format yaml
```

Options:
- `--format`: Output format for validation results (choices: sh, log, yaml; default: sh)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.