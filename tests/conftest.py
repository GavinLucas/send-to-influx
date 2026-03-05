"""Shared pytest fixtures and settings data for unit tests."""

import pytest


@pytest.fixture
def sample_settings():
    """Minimal valid toinflux settings for testing handlers."""
    return {
        "default_source": "hue",
        "hue": {
            "db": "hue_db",
            "host": "hue.example.com",
            "user": "hue_user",
            "timeout": 5,
            "interval": 300,
            "temperature_units": "C",
        },
        "myenergi": {
            "zappi_url": "https://s18.myenergi.net/cgi-jstatus-Z",
            "dayhour_url": "https://s18.myenergi.net/cgi-jdayhour-Z",
            "apikey": "test_apikey",
            "timeout": 5,
        },
        "zappi": {
            "db": "zappi_db",
            "interval": 300,
            "serial": "12345",
            "fields": ["frq", "vol", "gen"],
        },
        "influx": {
            "url": "https://influx.example.com:8086",
            "user": "influx_user",
            "password": "influx_password",
            "timeout": 5,
        },
    }
