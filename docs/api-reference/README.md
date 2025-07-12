# API Reference

This section provides comprehensive reference documentation for OAS Patcher's Python API, enabling programmatic usage and integration.

## Overview

OAS Patcher provides a Python API for:
- Programmatic overlay application
- Bundle management and processing
- Template engine integration
- Validation and error handling
- Custom tool development

## Quick Start

```python
from oas_patch import apply_overlay, validate_specification

# Apply a simple overlay
result = apply_overlay(
    input_spec="openapi.yaml",
    overlay_file="overlay.yaml"
)

# Validate the result
is_valid, errors = validate_specification(result)
```

## Core Modules

### `oas_patch.overlay`

Main overlay processing functionality.

```python
from oas_patch.overlay import Overlay, OverlayProcessor

# Load and apply overlay
overlay = Overlay.from_file("overlay.yaml")
processor = OverlayProcessor()
result = processor.apply(base_spec, overlay)
```

**Key Classes:**
- `Overlay` - Represents an overlay document
- `OverlayProcessor` - Processes overlay applications
- `Action` - Represents individual overlay actions

### `oas_patch.bundle_manager`

Bundle configuration and processing.

```python
from oas_patch.bundle_manager import BundleManager

# Load and process bundle
bundle_manager = BundleManager("bundle.yml")
result = bundle_manager.apply(environment="production")
```

**Key Classes:**
- `BundleManager` - Manages bundle configurations
- `BundleConfig` - Represents bundle configuration
- `Environment` - Represents environment settings

### `oas_patch.template_engine`

Template processing and variable substitution.

```python
from oas_patch.template_engine import TemplateEngine

# Process templates with variables
engine = TemplateEngine()
result = engine.render(template_content, variables)
```

**Key Classes:**
- `TemplateEngine` - Jinja2-based template processor
- `TemplateContext` - Template execution context
- `TemplateFunction` - Custom template functions

### `oas_patch.validator`

Specification validation and error reporting.

```python
from oas_patch.validator import Validator, ValidationError

# Validate OpenAPI specification
validator = Validator()
try:
    validator.validate(spec_content)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

**Key Classes:**
- `Validator` - OpenAPI specification validator
- `ValidationError` - Validation error exception
- `ValidationResult` - Detailed validation results

## Common Usage Patterns

### 1. Simple Overlay Application

```python
import yaml
from oas_patch.overlay import OverlayProcessor

# Load specifications
with open("openapi.yaml") as f:
    base_spec = yaml.safe_load(f)

with open("overlay.yaml") as f:
    overlay_spec = yaml.safe_load(f)

# Apply overlay
processor = OverlayProcessor()
result = processor.apply(base_spec, overlay_spec)

# Save result
with open("output.yaml", "w") as f:
    yaml.dump(result, f)
```

### 2. Bundle Processing with Environment

```python
from oas_patch.bundle_manager import BundleManager
from oas_patch.environment_manager import EnvironmentManager

# Setup environment
env_manager = EnvironmentManager()
env_manager.load_dotenv(".env.production")

# Process bundle
bundle_manager = BundleManager("bundle.yml")
bundle_manager.set_environment_manager(env_manager)

result = bundle_manager.apply(
    environment="production",
    output_file="openapi-prod.yaml"
)
```

### 3. Custom Template Functions

```python
from oas_patch.template_engine import TemplateEngine

def custom_formatter(value):
    """Custom template function."""
    return value.upper().replace(" ", "_")

# Register custom function
engine = TemplateEngine()
engine.add_function("format_name", custom_formatter)

# Use in template
template = "{{ API_NAME | format_name }}"
result = engine.render(template, {"API_NAME": "My API"})
# Result: "MY_API"
```

### 4. Validation with Custom Rules

```python
from oas_patch.validator import Validator, ValidationRule

class CustomValidationRule(ValidationRule):
    def validate(self, spec):
        # Custom validation logic
        if "x-custom-field" not in spec.get("info", {}):
            raise ValidationError("Missing required x-custom-field")

# Use custom validator
validator = Validator()
validator.add_rule(CustomValidationRule())
validator.validate(spec)
```

### 5. Error Handling

```python
from oas_patch import (
    apply_overlay, 
    OverlayError, 
    ValidationError, 
    TemplateError
)

try:
    result = apply_overlay("input.yaml", "overlay.yaml")
except OverlayError as e:
    print(f"Overlay application failed: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
except TemplateError as e:
    print(f"Template processing failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom Overlay Processor

```python
from oas_patch.overlay import OverlayProcessor, Action

class CustomOverlayProcessor(OverlayProcessor):
    def process_action(self, spec, action):
        """Custom action processing."""
        if action.get("custom_action"):
            return self.handle_custom_action(spec, action)
        return super().process_action(spec, action)
    
    def handle_custom_action(self, spec, action):
        """Handle custom action type."""
        # Custom logic here
        pass

# Use custom processor
processor = CustomOverlayProcessor()
result = processor.apply(base_spec, overlay_spec)
```

### Plugin Architecture

```python
from oas_patch.plugins import Plugin, PluginManager

class MyPlugin(Plugin):
    def initialize(self, config):
        """Plugin initialization."""
        pass
    
    def process_overlay(self, overlay):
        """Process overlay before application."""
        # Custom overlay processing
        return overlay
    
    def post_process(self, result):
        """Post-process result."""
        # Custom result processing
        return result

# Register and use plugin
plugin_manager = PluginManager()
plugin_manager.register(MyPlugin())
plugin_manager.initialize(config)

# Apply with plugins
result = plugin_manager.apply_overlay(base_spec, overlay_spec)
```

### Streaming Processing

```python
from oas_patch.streaming import StreamingProcessor

# Process large specifications in streaming mode
processor = StreamingProcessor()
with open("large-spec.yaml") as input_file:
    with open("output.yaml", "w") as output_file:
        processor.apply_streaming(
            input_file, 
            overlay_spec, 
            output_file
        )
```

## Configuration

### Global Configuration

```python
from oas_patch.config import Config

# Set global configuration
Config.set_defaults({
    "validation": {
        "strict_mode": True,
        "fail_on_warning": False
    },
    "template": {
        "strict_undefined": True,
        "auto_escape": False
    },
    "processing": {
        "max_memory": "1GB",
        "timeout": 300
    }
})
```

### Per-Operation Configuration

```python
from oas_patch.overlay import OverlayProcessor

# Configure processor
processor = OverlayProcessor(
    validation_mode="strict",
    template_config={
        "undefined": "strict",
        "auto_escape": False
    },
    processing_config={
        "timeout": 60,
        "max_iterations": 1000
    }
)
```

## Testing Integration

### Unit Testing

```python
import unittest
from oas_patch.overlay import OverlayProcessor

class TestOverlayApplication(unittest.TestCase):
    def setUp(self):
        self.processor = OverlayProcessor()
        self.base_spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }
    
    def test_simple_overlay(self):
        overlay = {
            "overlay": "1.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "actions": [
                {
                    "target": "$.info.title",
                    "update": "Updated API"
                }
            ]
        }
        
        result = self.processor.apply(self.base_spec, overlay)
        self.assertEqual(result["info"]["title"], "Updated API")
```

### Integration Testing

```python
import tempfile
import os
from oas_patch.bundle_manager import BundleManager

def test_bundle_integration():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        bundle_path = os.path.join(temp_dir, "bundle.yml")
        # ... create bundle configuration
        
        # Test bundle processing
        bundle_manager = BundleManager(bundle_path)
        result = bundle_manager.apply("test")
        
        # Assertions
        assert result is not None
        assert "info" in result
```

### Mock Testing

```python
from unittest.mock import Mock, patch
from oas_patch.template_engine import TemplateEngine

def test_template_with_mock():
    with patch('oas_patch.template_engine.Environment') as mock_env:
        mock_template = Mock()
        mock_template.render.return_value = "mocked result"
        mock_env.return_value.from_string.return_value = mock_template
        
        engine = TemplateEngine()
        result = engine.render("{{ test }}", {"test": "value"})
        
        assert result == "mocked result"
```

## Performance Optimization

### Memory Management

```python
from oas_patch.utils import memory_efficient_processing

# Process large specifications efficiently
with memory_efficient_processing():
    result = apply_overlay("large-spec.yaml", "overlay.yaml")
```

### Caching

```python
from oas_patch.cache import TemplateCache, OverlayCache

# Enable template caching
template_cache = TemplateCache(max_size=100)
engine = TemplateEngine(cache=template_cache)

# Enable overlay caching
overlay_cache = OverlayCache(max_size=50)
processor = OverlayProcessor(cache=overlay_cache)
```

### Parallel Processing

```python
from oas_patch.parallel import ParallelBundleProcessor
import concurrent.futures

# Process multiple environments in parallel
processor = ParallelBundleProcessor()
environments = ["dev", "staging", "production"]

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(processor.apply_environment, env): env 
        for env in environments
    }
    
    for future in concurrent.futures.as_completed(futures):
        env = futures[future]
        result = future.result()
        print(f"Processed {env}: {result}")
```

## Error Handling Reference

### Exception Hierarchy

```
OASPatchError
├── OverlayError
│   ├── InvalidOverlayError
│   ├── TargetNotFoundError
│   └── ActionConflictError
├── ValidationError
│   ├── SchemaValidationError
│   ├── FormatValidationError
│   └── ConstraintValidationError
├── TemplateError
│   ├── TemplateSyntaxError
│   ├── VariableNotFoundError
│   └── FilterError
├── BundleError
│   ├── BundleNotFoundError
│   ├── EnvironmentNotFoundError
│   └── CircularDependencyError
└── FileError
    ├── FileNotFoundError
    ├── PermissionError
    └── FormatError
```

### Error Context

```python
from oas_patch.errors import OverlayError

try:
    apply_overlay("input.yaml", "overlay.yaml")
except OverlayError as e:
    print(f"Error: {e}")
    print(f"Context: {e.context}")
    print(f"Line: {e.line_number}")
    print(f"Column: {e.column_number}")
    print(f"Suggestions: {e.suggestions}")
```

## Extension Points

### Custom Actions

```python
from oas_patch.actions import ActionHandler

class CustomActionHandler(ActionHandler):
    action_type = "custom_merge"
    
    def apply(self, document, action):
        """Apply custom merge action."""
        # Custom implementation
        pass

# Register custom action
from oas_patch.registry import ActionRegistry
ActionRegistry.register(CustomActionHandler)
```

### Custom Validators

```python
from oas_patch.validators import ValidatorPlugin

class BusinessRuleValidator(ValidatorPlugin):
    def validate(self, document):
        """Validate business rules."""
        errors = []
        # Custom validation logic
        return errors

# Register validator
from oas_patch.registry import ValidatorRegistry
ValidatorRegistry.register(BusinessRuleValidator)
```

### Custom Template Functions

```python
from oas_patch.template_functions import TemplateFunction

class DateTimeFunction(TemplateFunction):
    name = "datetime"
    
    def __call__(self, format_string="%Y-%m-%d"):
        """Return current datetime."""
        from datetime import datetime
        return datetime.now().strftime(format_string)

# Register function
from oas_patch.registry import TemplateRegistry
TemplateRegistry.register(DateTimeFunction)
```

## Best Practices

### 1. Resource Management

```python
# Use context managers for proper cleanup
from oas_patch.context import ProcessingContext

with ProcessingContext() as ctx:
    result = ctx.apply_overlay(base_spec, overlay_spec)
    # Automatic cleanup on exit
```

### 2. Error Resilience

```python
from oas_patch.resilience import RetryPolicy, CircuitBreaker

# Configure retry policy
retry_policy = RetryPolicy(
    max_attempts=3,
    backoff_factor=2.0,
    exceptions=[TemplateError, ValidationError]
)

# Apply with resilience
processor = OverlayProcessor(retry_policy=retry_policy)
result = processor.apply(base_spec, overlay_spec)
```

### 3. Monitoring and Logging

```python
import logging
from oas_patch.monitoring import MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("oas_patch")

# Enable metrics collection
metrics = MetricsCollector()
processor = OverlayProcessor(metrics=metrics)

result = processor.apply(base_spec, overlay_spec)

# Access metrics
print(f"Processing time: {metrics.processing_time}")
print(f"Memory usage: {metrics.peak_memory}")
print(f"Actions applied: {metrics.actions_count}")
```

## Migration Guide

### From CLI to API

```python
# CLI command:
# oas-patcher apply --input input.yaml --overlay overlay.yaml --output output.yaml

# Equivalent API usage:
from oas_patch import apply_overlay

result = apply_overlay(
    input_spec="input.yaml",
    overlay_file="overlay.yaml",
    output_file="output.yaml"
)
```

### From Other Tools

```python
# Migration helpers for other overlay tools
from oas_patch.migration import (
    convert_from_swagger_overlay,
    convert_from_redoc_overlay
)

# Convert existing overlay formats
overlay = convert_from_swagger_overlay("old-overlay.json")
result = apply_overlay(base_spec, overlay)
```

## Contributing to the API

### Development Setup

```python
# Development installation
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Type checking
mypy oas_patch/

# Code formatting
black oas_patch/
isort oas_patch/
```

### API Design Guidelines

1. **Consistency** - Follow established patterns
2. **Documentation** - Include comprehensive docstrings
3. **Type Hints** - Use type annotations
4. **Error Handling** - Provide meaningful error messages
5. **Testing** - Include comprehensive test coverage

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## Support and Resources

- **Source Code**: [GitHub Repository](https://github.com/example/oas-patcher)
- **Documentation**: [Full Documentation](https://oas-patcher.readthedocs.io)
- **Examples**: [Example Repository](https://github.com/example/oas-patcher-examples)
- **Community**: [Discussions](https://github.com/example/oas-patcher/discussions)
- **Issues**: [Bug Reports](https://github.com/example/oas-patcher/issues)
