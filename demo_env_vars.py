#!/usr/bin/env python3
"""
Demonstration of environment variable resolution in OAS Patcher for CI/CD pipelines.

This script shows how environment variables can be used in bundle configurations
and overlays to dynamically configure OpenAPI documents based on deployment context.
"""

import os
import sys
import yaml
from pathlib import Path

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from oas_patch.bundle_manager import BundleManager
from oas_patch.template_engine import TemplateEngine
from oas_patch.file_utils import load_file
from oas_patch.overlay import apply_overlay


def simulate_ci_environment():
    """Simulate a CI/CD environment by setting environment variables."""
    print("🔧 Setting up CI/CD environment variables...")
    
    # Simulate typical CI/CD environment variables
    os.environ.update({
        'APP_NAME': 'MyService API',
        'API_VERSION': '2.1.0',
        'API_BASE_URL': 'https://api.myservice.com',
        'DEPLOY_ENVIRONMENT': 'production',
        'BUILD_TIMESTAMP': '2025-07-11T10:30:00Z',
        'CI_BUILD_NUMBER': '456',
        'GIT_COMMIT': 'a1b2c3d4e5f6',
        'CI_PIPELINE_URL': 'https://gitlab.example.com/pipelines/123',
        'CI_RUNNER_DESCRIPTION': 'gitlab-ci-runner-01'
    })
    
    print("✅ Environment variables set:")
    for key, value in os.environ.items():
        if key.startswith(('APP_', 'API_', 'DEPLOY_', 'BUILD_', 'CI_', 'GIT_')):
            print(f"   {key}={value}")
    print()


def demonstrate_env_var_resolution():
    """Demonstrate various ways to use environment variables in templates."""
    print("🎯 Demonstrating environment variable resolution patterns:")
    print()
    
    template_engine = TemplateEngine()
    
    # Example 1: Using env() function with defaults
    print("1. Using env() function with defaults:")
    content1 = "Build: {{ env('CI_BUILD_NUMBER', 'local') }}"
    result1 = template_engine.process_template_content(content1, {})
    print(f"   Template: {content1}")
    print(f"   Result:   {result1}")
    print()
    
    # Example 2: Using ENV namespace
    print("2. Using ENV namespace:")
    content2 = "Commit: {{ ENV.GIT_COMMIT }}"
    result2 = template_engine.process_template_content(content2, {})
    print(f"   Template: {content2}")
    print(f"   Result:   {result2}")
    print()
    
    # Example 3: Using ${VAR} syntax in variables
    print("3. Using ${VAR} syntax in variables:")
    variables = {
        'app_name': '${APP_NAME}',
        'version': '${API_VERSION:1.0.0}',
        'missing_var': '${MISSING_VAR:default_value}'
    }
    content3 = "App: {{ app_name }} v{{ version }}, Missing: {{ missing_var }}"
    result3 = template_engine.process_template_content(content3, variables)
    print(f"   Variables: {variables}")
    print(f"   Template:  {content3}")
    print(f"   Result:    {result3}")
    print()
    
    # Example 4: Conditional logic with environment variables
    print("4. Conditional logic with environment variables:")
    content4 = """Environment: {{ ENV.DEPLOY_ENVIRONMENT }}
{%- if ENV.DEPLOY_ENVIRONMENT == 'production' %}
Security Level: High
{%- else %}
Security Level: Standard
{%- endif %}"""
    result4 = template_engine.process_template_content(content4, {})
    print(f"   Template: {content4}")
    print(f"   Result:   {result4}")
    print()


def demonstrate_ci_bundle():
    """Demonstrate the CI bundle with environment variable resolution."""
    print("🚀 Demonstrating CI/CD bundle processing:")
    print()
    
    # Create the CI bundle if it doesn't exist
    ci_bundle_dir = Path("tests/bundle/samples/ci_bundle")
    if not ci_bundle_dir.exists():
        print("❌ CI bundle not found. Please run this script from the project root.")
        return
    
    bundle_manager = BundleManager("tests/bundle/samples")
    template_engine = TemplateEngine()
    
    try:
        # Load the CI bundle
        print("📦 Loading CI bundle configuration...")
        bundle_config = bundle_manager.load_bundle("ci_bundle")
        print(f"   Bundle: {bundle_config.name}")
        print(f"   Variables: {bundle_config.variables}")
        print()
        
        # Get CI environment overlays
        print("📄 Getting overlays for CI environment...")
        overlays = bundle_manager.get_overlays_for_environment("ci_bundle", "ci")
        print(f"   Found {len(overlays)} overlays:")
        for overlay in overlays:
            print(f"   - {overlay.path} (env: {overlay.environment})")
        print()
        
        # Load original OpenAPI document
        original_openapi = load_file("tests/bundle/samples/ci_bundle/openapi.yaml")
        print("📋 Original OpenAPI info:")
        print(f"   Title: {original_openapi['info']['title']}")
        print(f"   Version: {original_openapi['info']['version']}")
        print()
        
        # Apply overlays with environment variable resolution
        print("🔄 Applying overlays with environment variable resolution...")
        result_openapi = original_openapi.copy()
        variables = dict(bundle_config.variables) if bundle_config.variables else {}
        
        for i, overlay_config in enumerate(overlays, 1):
            print(f"   Processing overlay {i}: {overlay_config.path}")
            
            # Load overlay file
            overlay_path = bundle_manager._resolve_overlay_path("ci_bundle", overlay_config.path)
            overlay_data = load_file(str(overlay_path))
            
            # Merge overlay variables
            overlay_variables = dict(variables)
            if overlay_config.variables:
                overlay_variables.update(overlay_config.variables)
            
            # Process template with environment variable resolution
            processed_overlay = template_engine.process_overlay_data(overlay_data, overlay_variables)
            
            # Apply overlay
            result_openapi = apply_overlay(result_openapi, processed_overlay)
            
            print(f"      ✅ Applied {overlay_config.path}")
        
        print()
        
        # Show results
        print("🎉 Final processed OpenAPI document:")
        print(f"   Title: {result_openapi['info']['title']}")
        print(f"   Version: {result_openapi['info']['version']}")
        print(f"   Description: {result_openapi['info']['description']}")
        
        if 'servers' in result_openapi:
            print(f"   Server URL: {result_openapi['servers'][0]['url']}")
            print(f"   Server Description: {result_openapi['servers'][0]['description']}")
        
        if 'x-build-info' in result_openapi['info']:
            build_info = result_openapi['info']['x-build-info']
            print(f"   Build Info:")
            print(f"     - Build Number: {build_info['build_number']}")
            print(f"     - Timestamp: {build_info['timestamp']}")
            print(f"     - Environment: {build_info['environment']}")
            print(f"     - Commit SHA: {build_info['commit_sha']}")
            print(f"     - Pipeline URL: {build_info['pipeline_url']}")
        
        if 'x-deployment' in result_openapi['info']:
            deploy_info = result_openapi['info']['x-deployment']
            print(f"   Deployment Info:")
            print(f"     - Deployed by: {deploy_info['deployed_by']}")
            print(f"     - Deploy time: {deploy_info['deploy_time']}")
        
        print()
        
        # Save the result for inspection
        output_file = "ci_bundle_output.yaml"
        with open(output_file, 'w') as f:
            yaml.dump(result_openapi, f, default_flow_style=False, sort_keys=False)
        print(f"💾 Full result saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error processing CI bundle: {e}")


def main():
    """Main demonstration function."""
    print("=" * 80)
    print("🌟 OAS Patcher Environment Variable Support Demo")
    print("=" * 80)
    print()
    
    # Simulate CI environment
    simulate_ci_environment()
    
    # Demonstrate environment variable resolution patterns
    demonstrate_env_var_resolution()
    
    # Demonstrate CI bundle processing
    demonstrate_ci_bundle()
    
    print("=" * 80)
    print("✨ Demo completed! Environment variables provide flexible configuration")
    print("   for CI/CD pipelines, allowing the same bundle to work across different")
    print("   deployment environments with context-specific values.")
    print("=" * 80)


if __name__ == "__main__":
    main()
