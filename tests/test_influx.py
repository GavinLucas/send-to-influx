"""Unit tests for toinflux.influx (Settings, DataHandler)."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import requests
import pytest
import yaml
from toinflux.influx import DataHandler, Settings


class TestSettings:
    """Tests for Settings class."""

    def test_init_loads_settings_file(self, sample_settings):
        """Settings loads YAML from settings file and sets toinflux."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(sample_settings, f)
            path = f.name
        try:
            # Pass absolute path so Settings uses it as-is (join with base_dir gives path)
            s = Settings(settings_file=path)
            assert s.toinflux == sample_settings
        finally:
            Path(path).unlink(missing_ok=True)

    def test_init_sets_base_dir_and_settings_file(self, sample_settings):
        """Settings sets base_dir and settings_file from path."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(sample_settings, f)
            path = f.name
        try:
            s = Settings(settings_file=path)
            assert s.base_dir
            assert s.settings_file == path
            assert s.toinflux["default_source"] == "hue"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_load_file_not_found_exits(self):
        """Settings.load exits with 1 when file is missing."""
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "missing.yml")
            with pytest.raises(SystemExit):
                Settings(settings_file=missing)

    def test_load_invalid_yaml_exits(self):
        """Settings.load exits with 1 on YAML error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("invalid: yaml: [[[")
            path = f.name
        try:
            with pytest.raises(SystemExit):
                Settings(settings_file=path)
        finally:
            Path(path).unlink(missing_ok=True)


class TestDataHandler:
    """Tests for DataHandler class."""

    def test_init_sets_source_and_source_settings(self, sample_settings):
        """DataHandler __init__ sets source and source_settings from settings."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            h = DataHandler(source="hue")
            assert h.settings == sample_settings
            assert h.source == "hue"
            assert h.source_settings == sample_settings["hue"]
            assert h.source_settings["db"] == "hue_db"
            assert h.source_settings["interval"] == 300
            assert h.influx_header is None
            assert h.data is None

    def test_init_source_not_in_settings_exits(self, sample_settings):
        """DataHandler __init__ exits when source not in settings."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            with pytest.raises(SystemExit):
                DataHandler(source="unknown_source")

    def test_send_data_uses_instance_data_when_data_is_none(self, sample_settings):
        """send_data uses self.data when data argument is None."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            h = DataHandler(source="hue")
            h.influx_header = "hue,host=test "
            h.data = {"temp": 21.5, "light": 100}
            with patch("toinflux.influx.requests.post") as mock_post:
                mock_post.return_value.raise_for_status = MagicMock()
                h.send_data()
                body = mock_post.call_args[1]["data"]
                assert "temp=21.5" in body
                assert "light=100" in body
                assert body.startswith("hue,host=test ")

    def test_send_data_uses_provided_data(self, sample_settings):
        """send_data uses provided data when given."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            h = DataHandler(source="hue")
            h.influx_header = "hue,host=test "
            h.data = {"old": 1}
            with patch("toinflux.influx.requests.post") as mock_post:
                mock_post.return_value.raise_for_status = MagicMock()
                h.send_data(data={"a": 1, "b": 2})
                body = mock_post.call_args[1]["data"]
                assert "a=1" in body
                assert "b=2" in body
                assert "old=1" not in body

    def test_send_data_builds_correct_url_and_auth(self, sample_settings):
        """send_data posts to correct Influx URL with auth."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            h = DataHandler(source="hue")
            h.influx_header = "hue "
            h.data = {"x": 1}
            with patch("toinflux.influx.requests.post") as mock_post:
                mock_post.return_value.raise_for_status = MagicMock()
                h.send_data()
                url = mock_post.call_args[0][0]
                call_kw = mock_post.call_args[1]
                assert "influx.example.com" in url
                assert call_kw["auth"] == ("influx_user", "influx_password")

    def test_send_data_handles_request_exception(self, sample_settings):
        """send_data does not raise when requests.post raises."""

        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            h = DataHandler(source="hue")
            h.influx_header = "hue "
            h.data = {"x": 1}
            with patch("toinflux.influx.requests.post") as mock_post:
                mock_post.side_effect = requests.exceptions.RequestException("network error")
                # should not raise
                h.send_data()
