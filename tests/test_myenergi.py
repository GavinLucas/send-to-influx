"""Unit tests for toinflux.myenergi (MyEnergi, Zappi)."""

from unittest.mock import MagicMock, patch
import pytest
from toinflux.myenergi import MyEnergi, Zappi


class TestMyEnergi:
    """Tests for MyEnergi class."""

    def test_get_data_from_myenergi_returns_json_on_200(self, sample_settings):
        """get_data_from_myenergi returns response JSON when status is 200."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"key": "value"}
            with patch("toinflux.myenergi.requests.get", return_value=mock_resp):
                result = handler.get_data_from_myenergi("https://example.com/api")
                assert result == {"key": "value"}

    def test_get_data_from_myenergi_exits_on_401(self, sample_settings):
        """get_data_from_myenergi exits on 401."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            with patch("toinflux.myenergi.requests.get", return_value=mock_resp):
                with pytest.raises(SystemExit):
                    handler.get_data_from_myenergi("https://example.com")

    def test_get_data_from_myenergi_exits_on_other_error_code(self, sample_settings):
        """get_data_from_myenergi exits on non-200, non-401 status."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            with patch("toinflux.myenergi.requests.get", return_value=mock_resp):
                with pytest.raises(SystemExit):
                    handler.get_data_from_myenergi("https://example.com")

    def test_dayhour_results_aggregates_day(self, sample_settings):
        """dayhour_results sums all hours for the day when hour is None."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            serial = handler.source_settings["serial"]
            response_data = {
                f"U{serial}": [
                    {"hr": 0, "h1d": 3600, "imp": 1000, "exp": 0, "gep": 0},
                    {"hr": 1, "h1d": 3600, "imp": 2000, "exp": 0, "gep": 0},
                ],
            }
            with patch.object(handler, "get_data_from_myenergi", return_value=response_data):
                result = handler.dayhour_results("2025", "01", "15", hour=None)
                assert result["Charge"] == round((3600 + 3600) / 3600 / 1000, 4)
                assert result["Import"] == round((1000 + 2000) / 3600 / 1000, 4)
                assert result["Export"] == 0
                assert result["Genera"] == 0

    def test_dayhour_results_single_hour_when_hour_specified(self, sample_settings):
        """dayhour_results returns single hour when hour is specified."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            serial = handler.source_settings["serial"]
            response_data = {
                f"U{serial}": [
                    {"hr": 0, "h1d": 0, "imp": 0, "exp": 0, "gep": 0},
                    {"hr": 2, "h1d": 7200, "imp": 5000, "exp": 100, "gep": 200},
                ],
            }
            with patch.object(handler, "get_data_from_myenergi", return_value=response_data):
                result = handler.dayhour_results("2025", "01", "15", hour="2")
                assert result["Charge"] == round(7200 / 3600 / 1000, 4)
                assert result["Import"] == round(5000 / 3600 / 1000, 4)
                assert result["Export"] == round(100 / 3600 / 1000, 4)
                assert result["Genera"] == round(200 / 3600 / 1000, 4)

    def test_dayhour_results_empty_when_no_serial_key(self, sample_settings):
        """dayhour_results returns zeroed data when response has no U+serial key."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            handler = MyEnergi(source="zappi")
            with patch.object(handler, "get_data_from_myenergi", return_value={}):
                result = handler.dayhour_results("2025", "01", "15")
                assert result["Charge"] == 0
                assert result["Import"] == 0
                assert result["Export"] == 0
                assert result["Genera"] == 0


class TestZappi:
    """Tests for Zappi class."""

    def test_get_data_sets_influx_header_and_returns_parsed_data(self, sample_settings):
        """get_data sets influx_header and returns parse_zappi_data result."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            with patch.object(Zappi, "parse_zappi_data", return_value={"frq": 50, "Charge": 1.5}) as mock_parse:
                zappi = Zappi(source="zappi")
                result = zappi.get_data()
                mock_parse.assert_called_once()
                assert zappi.influx_header == "myenergi,device=zappi "
                assert result == {"frq": 50, "Charge": 1.5}
                assert zappi.data == result

    def test_parse_zappi_data_merges_zappi_and_day_data(self, sample_settings):
        """parse_zappi_data merges API zappi fields with dayhour data."""
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = sample_settings
            zappi = Zappi(source="zappi")
            myenergi_data = {"zappi": [{"frq": 50, "vol": 240, "gen": 100, "other": "ignored"}]}
            day_data = {"Charge": 1.0, "Import": 2.0, "Export": 0.0, "Genera": 0.5}
            with patch.object(Zappi, "get_data_from_myenergi", return_value=myenergi_data):
                with patch.object(Zappi, "dayhour_results", return_value=day_data):
                    result = zappi.parse_zappi_data()
                    assert result["frq"] == 50
                    assert result["vol"] == 240
                    assert result["gen"] == 100
                    assert result["Charge"] == 1.0
                    assert result["Import"] == 2.0
                    assert "other" not in result

    def test_parse_zappi_data_uses_all_zappi_fields_when_no_fields_setting(self, sample_settings):
        """parse_zappi_data uses full zappi[0] when zappi.fields not in settings."""
        settings = {**sample_settings}
        zappi_cfg = {k: v for k, v in settings["zappi"].items() if k != "fields"}
        settings["zappi"] = zappi_cfg
        with patch("toinflux.influx.load_settings") as mock_load_settings:
            mock_load_settings.return_value = settings
            zappi = Zappi(source="zappi")
            myenergi_data = {"zappi": [{"frq": 50, "vol": 240, "custom": "yes"}]}
            day_data = {"Charge": 0, "Import": 0, "Export": 0, "Genera": 0}
            with patch.object(Zappi, "get_data_from_myenergi", return_value=myenergi_data):
                with patch.object(Zappi, "dayhour_results", return_value=day_data):
                    result = zappi.parse_zappi_data()
                    assert result["frq"] == 50
                    assert result["vol"] == 240
                    assert result["custom"] == "yes"
