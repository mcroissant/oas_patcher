import pytest
from unittest.mock import mock_open, patch
from src.oas_patch.file_utils import (
    load_yaml, load_json, load_file,
    save_yaml, save_json, save_file,
    sanitize_content
)


def test_load_yaml_valid():
    """Test loading a valid YAML file."""
    yaml_content = "key: value"
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        result = load_yaml("test.yaml")
    assert result == {"key": "value"}


def test_load_yaml_invalid():
    """Test loading an invalid YAML file."""
    invalid_yaml = "key: value: another"
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        with pytest.raises(ValueError, match="Invalid YAML format"):
            load_yaml("test.yaml")


def test_load_yaml_file_not_found():
    """Test loading a non-existent YAML file."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_yaml("missing.yaml")


def test_load_json_valid():
    """Test loading a valid JSON file."""
    json_content = '{"key": "value"}'
    with patch("builtins.open", mock_open(read_data=json_content)):
        result = load_json("test.json")
    assert result == {"key": "value"}


def test_load_json_invalid():
    """Test loading an invalid JSON file."""
    invalid_json = '{"key": "value"'
    with patch("builtins.open", mock_open(read_data=invalid_json)):
        with pytest.raises(ValueError, match="Invalid JSON format"):
            load_json("test.json")


def test_load_json_file_not_found():
    """Test loading a non-existent JSON file."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json("missing.json")


def test_load_file_yaml():
    """Test loading a YAML file using load_file."""
    yaml_content = "key: value"
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        result = load_file("test.yaml")
    assert result == {"key": "value"}


def test_load_file_json():
    """Test loading a JSON file using load_file."""
    json_content = '{"key": "value"}'
    with patch("builtins.open", mock_open(read_data=json_content)):
        result = load_file("test.json")
    assert result == {"key": "value"}


def test_load_file_unsupported_format():
    """Test loading a file with an unsupported format."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file("test.txt")


def test_save_yaml():
    """Test saving data to a YAML file."""
    data = {"key": "value"}
    with patch("builtins.open", mock_open()) as mocked_file:
        save_yaml(data, "test.yaml")
        mocked_file.assert_called_once_with("test.yaml", "w", encoding="utf-8")
        # Combine all write calls into a single string and verify the content
        written_content = "".join(call.args[0] for call in mocked_file().write.call_args_list)
        assert written_content == "key: value\n"


def test_save_json():
    """Test saving data to a JSON file."""
    data = {"key": "value"}
    with patch("builtins.open", mock_open()) as mocked_file:
        save_json(data, "test.json")
        mocked_file.assert_called_once_with("test.json", "w", encoding="utf-8")
        # Combine all write calls into a single string and verify the content
        written_content = "".join(call.args[0] for call in mocked_file().write.call_args_list)
        assert written_content == '{\n  "key": "value"\n}'


def test_save_file_yaml():
    """Test saving data to a YAML file using save_file."""
    data = {"key": "value"}
    with patch("builtins.open", mock_open()) as mocked_file:
        save_file(data, "test.yaml")
        mocked_file.assert_called_once_with("test.yaml", "w", encoding="utf-8")
        # Combine all write calls into a single string and verify the content
        written_content = "".join(call.args[0] for call in mocked_file().write.call_args_list)
        assert written_content == "key: value\n"


def test_save_file_json():
    """Test saving data to a JSON file using save_file."""
    data = {"key": "value"}
    with patch("builtins.open", mock_open()) as mocked_file:
        save_file(data, "test.json")
        mocked_file.assert_called_once_with("test.json", "w", encoding="utf-8")
        # Combine all write calls into a single string and verify the content
        written_content = "".join(call.args[0] for call in mocked_file().write.call_args_list)
        assert written_content == '{\n  "key": "value"\n}'


def test_save_file_unsupported_format():
    """Test saving data to an unsupported file format."""
    data = {"key": "value"}
    with pytest.raises(ValueError, match="Unsupported file format"):
        save_file(data, "test.txt")


def test_sanitize_content():
    """Test removing non-printable characters from a string."""
    content = "Valid\x00 content\x1F with invalid\x7F characters"
    sanitized = sanitize_content(content)
    assert sanitized == "Valid content with invalid characters"
