"""Unit tests for toinflux.general (load_settings, get_class)."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
import yaml
from toinflux.general import load_settings, get_class


class TestLoadSettings:
    """Tests for load_settings function."""

    def test_returns_parsed_yaml(self, sample_settings):
        """load_settings returns the parsed YAML dictionary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(sample_settings, f)
            path = f.name
        try:
            result = load_settings(settings_file=path)
            assert result == sample_settings
        finally:
            Path(path).unlink(missing_ok=True)

    def test_returns_correct_values(self, sample_settings):
        """load_settings returns dictionary with expected keys and values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(sample_settings, f)
            path = f.name
        try:
            result = load_settings(settings_file=path)
            assert result["default_source"] == "hue"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_file_not_found_exits(self):
        """load_settings exits with 1 when file is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "missing.yml")
            with pytest.raises(SystemExit):
                load_settings(settings_file=missing)

    def test_invalid_yaml_exits(self):
        """load_settings exits with 1 on YAML error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("invalid: yaml: [[[")
            path = f.name
        try:
            with pytest.raises(SystemExit):
                load_settings(settings_file=path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_empty_yaml_exits(self):
        """load_settings exits with 1 on empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("")
            path = f.name
        try:
            with pytest.raises(SystemExit):
                load_settings(settings_file=path)
        finally:
            Path(path).unlink(missing_ok=True)


class TestGetClass:
    """Tests for get_class function."""

    def test_get_class_returns_hue_for_lowercase(self, sample_settings):
        """get_class('hue') returns Hue instance with source 'hue'."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            with patch("toinflux.philipshue.Hue") as mock_hue:
                result = get_class("hue")
                mock_hue.assert_called_once_with("hue")
                assert result is mock_hue.return_value

    def test_get_class_returns_hue_for_uppercase(self, sample_settings):
        """get_class('Hue') uses capitalised class name and lower source."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            with patch("toinflux.philipshue.Hue") as mock_hue:
                result = get_class("Hue")
                mock_hue.assert_called_once_with("hue")
                assert result is mock_hue.return_value

    def test_get_class_returns_zappi_for_lowercase(self, sample_settings):
        """get_class('zappi') returns Zappi instance."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            with patch("toinflux.myenergi.Zappi") as mock_zappi:
                result = get_class("zappi")
                mock_zappi.assert_called_once_with("zappi")
                assert result is mock_zappi.return_value

    def test_get_class_returns_speedtest_for_lowercase(self, sample_settings):
        """get_class('speedtest') returns Speedtest instance."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            with patch("toinflux.speedtest.Speedtest") as mock_speedtest:
                result = get_class("speedtest")
                mock_speedtest.assert_called_once_with("speedtest")
                assert result is mock_speedtest.return_value

    def test_get_class_unknown_source_exits(self):
        """get_class with unknown source exits with 1."""
        with pytest.raises(SystemExit):
            get_class("nosuchsource")
