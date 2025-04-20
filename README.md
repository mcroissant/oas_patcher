# OAS Patcher

A command-line tool for working with OpenAPI Specification (OAS) Overlays, allowing you to patch and modify OpenAPI documents.

## Features

- Apply OpenAPI Overlays to existing OpenAPI documents
- Generate overlay files by comparing two OpenAPI documents
- Validate OpenAPI Overlay documents against the specification
- Support for both YAML and JSON formats
- Sanitize special characters in OpenAPI documents

## Installation

```bash
pip install oas-patcher
```

## Usage

### Apply an Overlay

Apply changes from an overlay file to an OpenAPI document:

```bash
oas-patcher overlay openapi.yaml overlay.yaml -o modified.yaml
```

Options:
- `-o, --output`: Path to save the modified OpenAPI document (optional, defaults to stdout)
- `--sanitize`: Remove special characters from the OpenAPI document

### Generate an Overlay (Diff)

Create an overlay file by comparing two OpenAPI documents:

```bash
oas-patcher diff original.yaml modified.yaml -o overlay.yaml
```

Options:
- `-o, --output`: Path to save the generated overlay file (optional, defaults to stdout)

### Validate an Overlay

Validate an OpenAPI Overlay document against the specification:

```bash
oas-patcher validate overlay.yaml --format yaml
```

Options:
- `--format`: Output format for validation results (choices: sh, log, yaml; default: sh)

## Examples

### Apply an Overlay and Save to File

```bash
oas-patcher overlay api.yaml changes.yaml -o updated-api.yaml
```

### Generate Overlay from Two API Versions

```bash
oas-patcher diff api-v1.yaml api-v2.yaml -o version-changes.yaml
```

### Validate an Overlay with YAML Output

```bash
oas-patcher validate my-overlay.yaml --format yaml
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.