"""
Thorough integration tests for the full bundle pipeline.

Covers:
- Variable precedence (CLI > overlay-specific > bundle-global)
- Sequential overlay application (each overlay sees the previous result)
- Environment-specific filtering (--env flag)
- No-env filter applies ALL overlays, including env-restricted ones
- Empty-match environment (no overlays match → warning + no output file)
- ${VAR:default} substitution in bundle-level variables
- env() / ENV.VAR / ${} syntax in overlay templates end-to-end
- Undefined Jinja2 variable renders to empty string (no crash)
- CI/CD bundle end-to-end (env vars, build metadata)
- Jinja2 conditionals and standard filters in templates
- --var with '=' in the value (URL-style)
- Bundle without a 'name' field (falls back to bundle filename stem)
- Overlay-specific variables override bundle-global variables
"""

import os
import tempfile
import pytest
from pathlib import Path

import yaml
from click.testing import CliRunner

from oas_patch.oas_patcher_cli import cli
from oas_patch.file_utils import load_file, save_file
from oas_patch.template_engine import TemplateEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(args, env=None):
    runner = CliRunner()
    return runner.invoke(cli, args, env=env)


def make_bundle(tmp: Path, overlays_cfg, bundle_vars=None, name="test-bundle"):
    """Write a minimal bundle.yaml and return its Path."""
    cfg = {"name": name, "overlays": overlays_cfg}
    if bundle_vars:
        cfg["variables"] = bundle_vars
    bundle_file = tmp / "bundle.yaml"
    save_file(cfg, str(bundle_file))
    return bundle_file


def make_overlay(tmp: Path, filename, actions, title="T"):
    ov = {
        "overlay": "1.0.0",
        "info": {"title": title, "version": "1.0.0"},
        "actions": actions,
    }
    p = tmp / filename
    save_file(ov, str(p))
    return p


def make_openapi(tmp: Path):
    doc = {"openapi": "3.0.3", "info": {"title": "Base", "version": "1.0.0"}, "paths": {}}
    p = tmp / "openapi.yaml"
    save_file(doc, str(p))
    return p


# ---------------------------------------------------------------------------
# Variable precedence
# ---------------------------------------------------------------------------


class TestVariablePrecedence:
    """CLI variables must win over overlay-specific AND bundle-global variables."""

    def test_cli_vars_override_bundle_global_vars(self, tmp_path):
        """CLI --var must beat bundle-level variables."""
        make_overlay(
            tmp_path,
            "ov.yaml",
            [{"target": "$.info", "update": {"title": "{{ api_title }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml"}],
            bundle_vars={"api_title": "Bundle Title"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--var", "api_title=CLI Title",
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "CLI Title"

    def test_cli_vars_override_overlay_specific_vars(self, tmp_path):
        """CLI --var must beat overlay-specific variables."""
        make_overlay(
            tmp_path,
            "ov.yaml",
            [{"target": "$.info", "update": {"x-stage": "{{ stage }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml", "variables": {"stage": "overlay-level"}}],
            bundle_vars={"stage": "bundle-level"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--var", "stage=cli-level",
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-stage"] == "cli-level", (
            "CLI variable must override overlay-specific variable: "
            f"got '{doc['info']['x-stage']}'"
        )

    def test_overlay_specific_vars_override_bundle_vars(self, tmp_path):
        """Overlay-specific variables must beat bundle-global variables."""
        make_overlay(
            tmp_path,
            "ov.yaml",
            [{"target": "$.info", "update": {"x-scope": "{{ scope }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml", "variables": {"scope": "overlay-scope"}}],
            bundle_vars={"scope": "bundle-scope"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-scope"] == "overlay-scope"

    def test_var_with_equals_in_value(self, tmp_path):
        """--var key=https://host/path must treat everything after first '=' as the value."""
        make_overlay(
            tmp_path,
            "ov.yaml",
            [{"target": "$.info", "update": {"x-url": "{{ url }}"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--var", "url=https://api.example.com/v1?foo=bar",
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-url"] == "https://api.example.com/v1?foo=bar"

    def test_multiple_overlay_vars_independent(self, tmp_path):
        """Each overlay gets its own variable scope; earlier overlay's vars don't leak."""
        make_overlay(
            tmp_path,
            "ov1.yaml",
            [{"target": "$.info", "update": {"x-step": "{{ step }}"}}],
        )
        make_overlay(
            tmp_path,
            "ov2.yaml",
            [{"target": "$.info", "update": {"x-step2": "{{ step }}"}}],
        )
        make_bundle(
            tmp_path,
            [
                {"path": "ov1.yaml", "variables": {"step": "first"}},
                {"path": "ov2.yaml", "variables": {"step": "second"}},
            ],
            bundle_vars={"step": "global"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        # Each overlay used its own step variable, not the other's
        assert doc["info"]["x-step"] == "first"
        assert doc["info"]["x-step2"] == "second"


# ---------------------------------------------------------------------------
# Sequential overlay application
# ---------------------------------------------------------------------------


class TestSequentialOverlays:
    """Each overlay must see the output of all previous overlays."""

    def test_overlay_result_feeds_next_overlay(self, tmp_path):
        """The output of overlay N is the input of overlay N+1."""
        # Overlay 1: set title and add x-step1
        make_overlay(
            tmp_path,
            "ov1.yaml",
            [{"target": "$.info", "update": {"title": "After Step 1", "x-step1": True}}],
        )
        # Overlay 2: add x-step2 (x-step1 must already be there)
        make_overlay(
            tmp_path,
            "ov2.yaml",
            [{"target": "$.info", "update": {"x-step2": True}}],
        )
        # Overlay 3: change title one more time
        make_overlay(
            tmp_path,
            "ov3.yaml",
            [{"target": "$.info", "update": {"title": "Final Title"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov1.yaml"}, {"path": "ov2.yaml"}, {"path": "ov3.yaml"}],
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        info = doc["info"]
        assert info["title"] == "Final Title"
        assert info["x-step1"] is True
        assert info["x-step2"] is True

    def test_overlay_order_matters(self, tmp_path):
        """Last overlay wins for the same target key."""
        make_overlay(
            tmp_path, "ov1.yaml",
            [{"target": "$.info", "update": {"title": "First"}}],
        )
        make_overlay(
            tmp_path, "ov2.yaml",
            [{"target": "$.info", "update": {"title": "Second"}}],
        )
        make_bundle(tmp_path, [{"path": "ov1.yaml"}, {"path": "ov2.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "Second"

    def test_remove_in_earlier_overlay_visible_to_later(self, tmp_path):
        """A key removed in overlay N must be absent when overlay N+1 runs."""
        make_overlay(
            tmp_path, "ov1.yaml",
            [{"target": "$.info.description", "remove": True}],
        )
        make_overlay(
            tmp_path, "ov2.yaml",
            [{"target": "$.info", "update": {"x-had-desc": False}}],
        )
        make_bundle(tmp_path, [{"path": "ov1.yaml"}, {"path": "ov2.yaml"}])

        doc = {
            "openapi": "3.0.3",
            "info": {"title": "Base", "version": "1.0.0", "description": "Remove me"},
            "paths": {},
        }
        save_file(doc, str(tmp_path / "openapi.yaml"))

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        result = load_file(str(tmp_path / "out.yaml"))
        assert "description" not in result["info"]
        assert result["info"]["x-had-desc"] is False


# ---------------------------------------------------------------------------
# Environment filtering
# ---------------------------------------------------------------------------


class TestEnvironmentFiltering:
    def test_env_filter_restricts_overlays(self, tmp_path):
        """Only overlays matching --env are applied; others are skipped."""
        make_overlay(tmp_path, "base.yaml",
                     [{"target": "$.info", "update": {"x-base": True}}])
        make_overlay(tmp_path, "prod.yaml",
                     [{"target": "$.info", "update": {"x-prod": True}}])
        make_overlay(tmp_path, "dev.yaml",
                     [{"target": "$.info", "update": {"x-dev": True}}])
        make_bundle(
            tmp_path,
            [
                {"path": "base.yaml"},  # always applied
                {"path": "prod.yaml", "environment": ["prod", "production"]},
                {"path": "dev.yaml", "environment": ["dev"]},
            ],
        )
        make_openapi(tmp_path)

        # Run with --env prod: base + prod only
        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--env", "prod",
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"].get("x-base") is True
        assert doc["info"].get("x-prod") is True
        assert "x-dev" not in doc["info"]

    def test_env_filter_multiple_names_in_list(self, tmp_path):
        """An overlay with environment: [prod, production] matches both names."""
        make_overlay(tmp_path, "ov.yaml",
                     [{"target": "$.info", "update": {"x-env": "{{ env_name }}"}}])
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml", "environment": ["prod", "production"]}],
            bundle_vars={"env_name": "prod"},
        )
        make_openapi(tmp_path)

        for env_name in ("prod", "production"):
            r = run(
                [
                    "bundle", "apply",
                    str(tmp_path / "openapi.yaml"),
                    str(tmp_path / "bundle.yaml"),
                    "--env", env_name,
                    "--output", str(tmp_path / "out.yaml"),
                ]
            )
            assert r.exit_code == 0, r.output
            doc = load_file(str(tmp_path / "out.yaml"))
            assert "x-env" in doc["info"]

    def test_no_env_flag_applies_all_overlays(self, tmp_path):
        """Without --env, ALL overlays (including env-restricted ones) are applied."""
        make_overlay(tmp_path, "common.yaml",
                     [{"target": "$.info", "update": {"x-common": True}}])
        make_overlay(tmp_path, "prod.yaml",
                     [{"target": "$.info", "update": {"x-prod": True}}])
        make_overlay(tmp_path, "dev.yaml",
                     [{"target": "$.info", "update": {"x-dev": True}}])
        make_bundle(
            tmp_path,
            [
                {"path": "common.yaml"},
                {"path": "prod.yaml", "environment": ["prod"]},
                {"path": "dev.yaml", "environment": ["dev"]},
            ],
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"].get("x-common") is True
        assert doc["info"].get("x-prod") is True
        assert doc["info"].get("x-dev") is True

    def test_no_matching_overlays_exits_cleanly(self, tmp_path):
        """When no overlays match the requested env, command exits 0 with a warning."""
        make_overlay(tmp_path, "prod.yaml",
                     [{"target": "$.info", "update": {"x-prod": True}}])
        make_bundle(
            tmp_path,
            [{"path": "prod.yaml", "environment": ["prod"]}],
        )
        make_openapi(tmp_path)
        out = tmp_path / "out.yaml"

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--env", "dev",   # no overlay matches this
                "--output", str(out),
            ]
        )
        assert r.exit_code == 0, r.output
        assert not out.exists(), "No output file should be created when no overlays match"
        assert "No overlays" in r.output


# ---------------------------------------------------------------------------
# Template / variable injection
# ---------------------------------------------------------------------------


class TestTemplateInjection:
    """End-to-end template rendering tests through the full bundle pipeline."""

    def test_dollar_brace_default_without_env_var(self, tmp_path, monkeypatch):
        """${VAR:default} in bundle variables falls back to default when unset."""
        monkeypatch.delenv("BUNDLE_TEST_TITLE", raising=False)
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "{{ api_title }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml"}],
            bundle_vars={"api_title": "${BUNDLE_TEST_TITLE:Default Title}"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "Default Title"

    def test_dollar_brace_resolved_from_env_var(self, tmp_path, monkeypatch):
        """${VAR:default} in bundle variables uses env var when set."""
        monkeypatch.setenv("BUNDLE_TEST_TITLE", "Env-Injected Title")
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "{{ api_title }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml"}],
            bundle_vars={"api_title": "${BUNDLE_TEST_TITLE:Default Title}"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "Env-Injected Title"

    def test_cli_var_overrides_dollar_brace_bundle_var(self, tmp_path, monkeypatch):
        """--var must beat ${VAR:default} resolved bundle variable."""
        monkeypatch.setenv("BUNDLE_TEST_TITLE", "Env Title")
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "{{ api_title }}"}}],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml"}],
            bundle_vars={"api_title": "${BUNDLE_TEST_TITLE:Default Title}"},
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--var", "api_title=CLI Title",
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "CLI Title"

    def test_env_function_default_when_unset(self, tmp_path, monkeypatch):
        """{{ env('VAR', 'default') }} returns default when VAR is not in os.environ."""
        monkeypatch.delenv("BUNDLE_COMMIT", raising=False)
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {
                "x-commit": "{{ env('BUNDLE_COMMIT', 'none') }}"
            }}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-commit"] == "none"

    def test_env_function_reads_real_env_var(self, tmp_path, monkeypatch):
        """{{ env('VAR') }} reads from os.environ when the variable is set."""
        monkeypatch.setenv("BUNDLE_COMMIT", "deadbeef")
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {
                "x-commit": "{{ env('BUNDLE_COMMIT', 'none') }}"
            }}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-commit"] == "deadbeef"

    def test_ENV_namespace_access(self, tmp_path, monkeypatch):
        """{{ ENV.VAR_NAME }} resolves from the ENV namespace injected by TemplateEngine."""
        monkeypatch.setenv("BUNDLE_REGION", "us-east-1")
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {
                "x-region": "{{ ENV.BUNDLE_REGION }}"
            }}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-region"] == "us-east-1"

    def test_undefined_variable_renders_to_empty_string(self, tmp_path):
        """Jinja2 renders an undefined variable to '' (does not crash or skip the overlay)."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"x-val": "{{ totally_undefined_var }}"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        # Overlay was applied; x-val is empty string
        assert doc["info"]["x-val"] == ""

    def test_jinja2_conditional_in_template(self, tmp_path):
        """{% if %} block in an overlay string value is rendered correctly."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {
                "x-mode": "{% if debug %}debug{% else %}release{% endif %}"
            }}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}], bundle_vars={"debug": True})
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-mode"] == "debug"

    def test_jinja2_conditional_false_branch(self, tmp_path):
        """{% if %} false branch is rendered when condition is false."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {
                "x-mode": "{% if debug %}debug{% else %}release{% endif %}"
            }}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}], bundle_vars={"debug": False})
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-mode"] == "release"

    def test_standard_jinja2_filter_upper(self, tmp_path):
        """Standard Jinja2 filters like |upper are available in templates."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "{{ name | upper }}"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}], bundle_vars={"name": "my api"})
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "MY API"

    def test_template_in_nested_structure(self, tmp_path):
        """Templates are resolved inside nested dicts and lists."""
        make_overlay(
            tmp_path, "ov.yaml",
            [
                {
                    "target": "$",
                    "update": {
                        "servers": [
                            {
                                "url": "{{ base_url }}/{{ version }}",
                                "description": "{{ environment }} server",
                            }
                        ]
                    },
                }
            ],
        )
        make_bundle(
            tmp_path,
            [{"path": "ov.yaml"}],
            bundle_vars={
                "base_url": "https://api.example.com",
                "version": "v2",
                "environment": "Production",
            },
        )
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        servers = doc["servers"]
        assert servers[0]["url"] == "https://api.example.com/v2"
        assert servers[0]["description"] == "Production server"


# ---------------------------------------------------------------------------
# CI/CD bundle (uses the existing ci_bundle sample)
# ---------------------------------------------------------------------------


class TestCIBundle:
    """End-to-end test for the CI/CD bundle sample."""

    @pytest.fixture
    def ci_bundle_dir(self):
        return Path(__file__).parent / "samples" / "ci_bundle"

    def test_ci_bundle_applies_with_env_vars(self, tmp_path, ci_bundle_dir, monkeypatch):
        """ci_bundle resolves ${VAR:default}, env(), and ENV.VAR from the environment."""
        monkeypatch.setenv("GIT_COMMIT", "abc123def456")
        monkeypatch.setenv("CI_BUILD_NUMBER", "99")
        monkeypatch.setenv("BUILD_TIMESTAMP", "2025-01-01T12:00:00Z")
        monkeypatch.setenv("DEPLOY_ENVIRONMENT", "staging")
        monkeypatch.setenv("CI_PIPELINE_URL", "https://ci.example.com/99")

        out = tmp_path / "out.yaml"
        r = run(
            [
                "bundle", "apply",
                str(ci_bundle_dir / "openapi.yaml"),
                str(ci_bundle_dir / "bundle.yaml"),
                "--env", "ci",
                "--output", str(out),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(out))
        build_info = doc["info"]["x-build-info"]
        # build_number comes from overlay-specific variable ${CI_BUILD_NUMBER:0}
        assert build_info["build_number"] == "99"
        # commit_sha comes from env('GIT_COMMIT', 'unknown') in the overlay template
        assert build_info["commit_sha"] == "abc123def456"
        # environment comes from DEPLOY_ENVIRONMENT via ${} in bundle vars
        assert build_info["environment"] == "staging"
        # deploy_time uses ENV.BUILD_TIMESTAMP
        assert doc["info"]["x-deployment"]["deploy_time"] == "2025-01-01T12:00:00Z"

    def test_ci_bundle_defaults_when_env_vars_absent(self, tmp_path, ci_bundle_dir, monkeypatch):
        """ci_bundle uses defaults when CI env vars are not set."""
        for var in [
            "GIT_COMMIT", "CI_BUILD_NUMBER", "BUILD_TIMESTAMP",
            "DEPLOY_ENVIRONMENT", "CI_PIPELINE_URL", "APP_NAME",
            "API_VERSION", "API_BASE_URL", "CI_RUNNER_DESCRIPTION",
        ]:
            monkeypatch.delenv(var, raising=False)

        out = tmp_path / "out.yaml"
        r = run(
            [
                "bundle", "apply",
                str(ci_bundle_dir / "openapi.yaml"),
                str(ci_bundle_dir / "bundle.yaml"),
                "--env", "ci",
                "--output", str(out),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(out))
        build_info = doc["info"]["x-build-info"]
        # Should fall back to defaults defined with :
        assert build_info["build_number"] == "0"
        assert build_info["commit_sha"] == "unknown"


# ---------------------------------------------------------------------------
# Bundle metadata / structure edge cases
# ---------------------------------------------------------------------------


class TestBundleStructure:
    def test_bundle_without_name_field(self, tmp_path):
        """Bundle without 'name' field must use the bundle file's stem as name."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"x-ok": True}}],
        )
        # Deliberately omit 'name' from bundle config
        cfg = {"overlays": [{"path": "ov.yaml"}]}
        bundle_file = tmp_path / "my-bundle.yaml"
        save_file(cfg, str(bundle_file))
        make_openapi(tmp_path)

        # The command should succeed (name is optional)
        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(bundle_file),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["x-ok"] is True

    def test_empty_bundle_variables(self, tmp_path):
        """Bundle with no variables section must still apply overlays."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "Static Title"}}],
        )
        cfg = {"name": "no-vars", "overlays": [{"path": "ov.yaml"}]}
        save_file(cfg, str(tmp_path / "bundle.yaml"))
        make_openapi(tmp_path)

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(tmp_path / "out.yaml"),
            ]
        )
        assert r.exit_code == 0, r.output
        doc = load_file(str(tmp_path / "out.yaml"))
        assert doc["info"]["title"] == "Static Title"

    def test_bundle_validation_passes_for_valid_bundle(self, tmp_path):
        """bundle validate exits 0 for a well-formed bundle."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "OK"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])

        r = run(["bundle", "validate", str(tmp_path / "bundle.yaml")])
        assert r.exit_code == 0, r.output

    def test_bundle_validation_fails_for_missing_overlay_file(self, tmp_path):
        """bundle validate exits 1 when an overlay file does not exist."""
        make_bundle(tmp_path, [{"path": "nonexistent.yaml"}])

        r = run(["bundle", "validate", str(tmp_path / "bundle.yaml")])
        assert r.exit_code == 1
        assert "not found" in r.output


# ---------------------------------------------------------------------------
# Dry-run and output format
# ---------------------------------------------------------------------------


class TestDryRunAndFormats:
    def test_dry_run_no_file_created(self, tmp_path):
        """--dry-run must print the result but NOT write any file."""
        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "DryRun Result"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)
        out = tmp_path / "should-not-exist.yaml"

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(out),
                "--dry-run",
            ]
        )
        assert r.exit_code == 0, r.output
        assert not out.exists()
        assert "DryRun Result" in r.output

    def test_json_output_format(self, tmp_path):
        """--format json writes a valid JSON file."""
        import json

        make_overlay(
            tmp_path, "ov.yaml",
            [{"target": "$.info", "update": {"title": "JSON API"}}],
        )
        make_bundle(tmp_path, [{"path": "ov.yaml"}])
        make_openapi(tmp_path)
        out = tmp_path / "out.json"

        r = run(
            [
                "bundle", "apply",
                str(tmp_path / "openapi.yaml"),
                str(tmp_path / "bundle.yaml"),
                "--output", str(out),
                "--format", "json",
            ]
        )
        assert r.exit_code == 0, r.output
        assert out.exists()
        with open(out) as f:
            data = json.load(f)
        assert data["info"]["title"] == "JSON API"


# ---------------------------------------------------------------------------
# TemplateEngine unit-level tests not covered elsewhere
# ---------------------------------------------------------------------------


class TestTemplateEngineUnit:
    def setup_method(self):
        self.engine = TemplateEngine()

    def test_enable_env_vars_false_no_ENV_namespace(self, monkeypatch):
        """When enable_env_vars=False, ENV namespace must NOT be injected."""
        monkeypatch.setenv("SOME_VAR", "injected")
        engine = TemplateEngine(enable_env_vars=False)
        # With env vars disabled, the ENV namespace isn't injected,
        # so ENV.SOME_VAR renders to '' (undefined)
        result = engine.process_template_content(
            "{{ ENV.SOME_VAR if ENV is defined else 'disabled' }}", {}
        )
        assert result == "disabled"

    def test_env_function_not_available_when_disabled(self, monkeypatch):
        """env() function must still work regardless of enable_env_vars flag
        (it is always registered as a global)."""
        # The env() global IS always registered; enable_env_vars only affects
        # the ENV namespace and ${} var resolution.
        monkeypatch.setenv("MY_TEST_VAR", "hello")
        engine = TemplateEngine(enable_env_vars=True)
        result = engine.process_template_content("{{ env('MY_TEST_VAR', 'x') }}", {})
        assert result == "hello"

    def test_process_overlay_data_does_not_mutate_input(self):
        """process_overlay_data must not mutate the original overlay dict."""
        original = {"actions": [{"target": "$.info", "update": {"title": "{{ name }}"}}]}
        import copy
        snapshot = copy.deepcopy(original)

        self.engine.process_overlay_data(original, {"name": "Processed"})
        assert original == snapshot

    def test_to_yaml_filter_roundtrips(self):
        """to_yaml filter produces YAML that parses back to the original object."""
        obj = {"key": "value", "num": 42, "nested": {"x": [1, 2, 3]}}
        yaml_str = self.engine._to_yaml_filter(obj)
        assert yaml.safe_load(yaml_str) == obj

    def test_dollar_brace_no_default_returns_empty_when_unset(self, monkeypatch):
        """${VAR} with no default returns empty string when VAR is not set."""
        monkeypatch.delenv("UNSET_XYZ_TEST", raising=False)
        result = self.engine._resolve_env_vars_in_value("${UNSET_XYZ_TEST}")
        assert result == ""

    def test_dollar_brace_with_default_returns_default(self, monkeypatch):
        """${VAR:fallback} returns fallback when VAR is not set."""
        monkeypatch.delenv("UNSET_XYZ_TEST", raising=False)
        result = self.engine._resolve_env_vars_in_value("${UNSET_XYZ_TEST:fallback}")
        assert result == "fallback"

    def test_dollar_brace_returns_env_value_when_set(self, monkeypatch):
        """${VAR:fallback} returns env value when VAR is set."""
        monkeypatch.setenv("UNSET_XYZ_TEST", "real-value")
        result = self.engine._resolve_env_vars_in_value("${UNSET_XYZ_TEST:fallback}")
        assert result == "real-value"

    def test_multiple_dollar_brace_in_single_string(self, monkeypatch):
        """Multiple ${} substitutions in a single string all resolve."""
        monkeypatch.setenv("A_VAR", "alpha")
        monkeypatch.setenv("B_VAR", "beta")
        result = self.engine._resolve_env_vars_in_value("${A_VAR}-${B_VAR}")
        assert result == "alpha-beta"

    def test_extract_variables_from_complex_template(self):
        """extract_template_variables finds all undeclared variables."""
        content = "{{ title }} - {{ version }} by {{ owner }}"
        variables = self.engine.extract_template_variables(content)
        assert "title" in variables
        assert "version" in variables
        assert "owner" in variables

    def test_validate_template_with_syntax_error(self):
        """validate_template marks invalid templates with valid=False."""
        result = self.engine.validate_template("{{ unclosed }")
        assert result["valid"] is False
        assert result["errors"]
