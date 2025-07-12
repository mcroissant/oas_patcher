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
git clone https://github.com/your-org/oas-patcher.git
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

## Install with Docker

You can also run OAS Patcher in a Docker container:

### 1. Pull the Image

```bash
docker pull ghcr.io/your-org/oas-patcher:latest
```

### 2. Run with Docker

```bash
# Apply an overlay
docker run --rm -v $(pwd):/workspace ghcr.io/your-org/oas-patcher:latest \
  overlay /workspace/api.yaml /workspace/overlay.yaml -o /workspace/output.yaml

# Or get help
docker run --rm ghcr.io/your-org/oas-patcher:latest --help
```

## Installation Options

### Core Installation

The basic installation includes all core features:

```bash
pip install oas-patch
```

**Includes:**
- Overlay application and generation
- Basic validation
- CLI interface
- Python API

### Full Installation with Enhanced Features

For advanced features like bundle management and template engine:

```bash
pip install "oas-patch[enhanced]"
```

**Additional features:**
- Bundle management
- Template engine with Jinja2
- Environment variable support
- Advanced CLI commands

### Development Installation

For contributors and advanced users:

```bash
pip install "oas-patch[dev]"
```

**Includes:**
- All enhanced features
- Testing frameworks
- Development tools
- Documentation tools

## Platform-Specific Instructions

### Windows

```powershell
# Using pip
pip install oas-patch

# Using pipx (isolated installation)
pipx install oas-patch
```

### macOS

```bash
# Using pip
pip install oas-patch

# Using Homebrew (if available)
brew install oas-patch

# Using pipx
pipx install oas-patch
```

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip
pip3 install oas-patch

# CentOS/RHEL/Fedora
sudo yum install python3-pip  # or dnf
pip3 install oas-patch

# Using pipx
pipx install oas-patch
```

## Virtual Environments

We strongly recommend using virtual environments to avoid dependency conflicts:

### Using venv (Built-in)

```bash
# Create virtual environment
python -m venv oas-patcher-env

# Activate it
# Windows:
oas-patcher-env\Scripts\activate
# macOS/Linux:
source oas-patcher-env/bin/activate

# Install OAS Patcher
pip install oas-patch

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create environment
conda create -n oas-patcher python=3.9

# Activate environment
conda activate oas-patcher

# Install OAS Patcher
pip install oas-patch
```

### Using pipx (Isolated Installation)

pipx installs Python applications in isolated environments:

```bash
# Install pipx first
pip install pipx

# Install OAS Patcher
pipx install oas-patch

# Use directly
oas-patch --help
```

## Troubleshooting Installation

### Common Issues

**"Command not found" error:**
- Make sure Python's Scripts directory is in your PATH
- Try using `python -m oas_patch` instead of `oas-patch`

**Permission errors on Windows:**
- Use `--user` flag: `pip install --user oas-patch`
- Or run command prompt as Administrator

**Permission errors on macOS/Linux:**
- Use `--user` flag: `pip install --user oas-patch`
- Or use `sudo` (not recommended)

**ImportError or ModuleNotFoundError:**
- Make sure you're using the right Python environment
- Check Python version: `python --version`
- Reinstall: `pip uninstall oas-patch && pip install oas-patch`

### Getting Help

If you encounter issues:

1. Check our [Troubleshooting Guide](../troubleshooting/common-issues.md)
2. Search [GitHub Issues](https://github.com/your-org/oas-patcher/issues)
3. Create a new issue with:
   - Your operating system
   - Python version
   - Installation method used
   - Complete error message

## Next Steps

Now that OAS Patcher is installed:

1. 📚 [Quick Start Guide](quick-start.md) - Get up and running in 5 minutes
2. 🎯 [Your First Overlay](first-overlay.md) - Create your first overlay
3. 📖 [Core Concepts](../core-concepts/overlays.md) - Understand the fundamentals

---

**Need help?** Check our [FAQ](../troubleshooting/faq.md) or ask a question in [GitHub Discussions](https://github.com/your-org/oas-patcher/discussions).
