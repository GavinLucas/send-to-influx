"""Unit tests for toinflux.general (get_class)."""

from unittest.mock import patch
import pytest
from toinflux.general import get_class


class TestGetClass:
    """Tests for get_class function."""

    def test_get_class_returns_hue_for_lowercase(self, sample_settings):
        """get_class('hue') returns Hue instance with source 'hue'."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            with patch("toinflux.general.Hue") as mock_hue:
                result = get_class("hue")
                mock_hue.assert_called_once_with("hue")
                assert result is mock_hue.return_value

    def test_get_class_returns_hue_for_uppercase(self, sample_settings):
        """get_class('Hue') uses capitalised class name and lower source."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            with patch("toinflux.general.Hue") as mock_hue:
                result = get_class("Hue")
                mock_hue.assert_called_once_with("hue")
                assert result is mock_hue.return_value

    def test_get_class_returns_zappi_for_lowercase(self, sample_settings):
        """get_class('zappi') returns Zappi instance."""
        with patch("toinflux.influx.Settings") as mock_settings:
            mock_settings.return_value.toinflux = sample_settings
            with patch("toinflux.general.Zappi") as mock_zappi:
                result = get_class("zappi")
                mock_zappi.assert_called_once_with("zappi")
                assert result is mock_zappi.return_value

    def test_get_class_unknown_source_exits(self):
        """get_class with unknown source exits with 1."""
        with pytest.raises(SystemExit):
            get_class("nosuchsource")
