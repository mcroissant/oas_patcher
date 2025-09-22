# Installation

This guide covers different ways to install OAS Patcher on your system.

## Prerequisites

- **Python 3.8 or higher** - Check your version with `python --version`
- **pip** - Python package installer (usually comes with Python)

## Install from PyPI (Recommended)

The easiest way to install OAS Patcher is using pip:

```bash
pip install oas-patch
```

### Verify Installation

After installation, verify it's working:

```bash
oas-patch --version
```

You should see output similar to:
```
oas-patch, version 1.0.0
```

## Install from Source

If you want the latest development version or want to contribute:

### 1. Clone the Repository

```bash
git clone https://github.com/mcroissant/oas_patcher.git
cd oas-patcher
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install in Development Mode

```bash
pip install -e .
```

This installs OAS Patcher in "editable" mode, so changes to the source code are immediately available.

### 4. Install Development Dependencies (Optional)

If you plan to contribute or run tests:

```bash
pip install -r requirements-dev.txt
```

## Next Steps

Now that OAS Patcher is installed:

1. 📚 [Quick Start Guide](quick-start.md) - Get up and running in 5 minutes
2. 🎯 [Your First Overlay](first-overlay.md) - Create your first overlay
3. 📖 [Core Concepts](../core-concepts/overlays.md) - Understand the fundamentals

---
