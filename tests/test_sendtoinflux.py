"""Unit tests for sendtoinflux (signal_handler, main)."""

from unittest.mock import MagicMock, patch
import pytest
import sendtoinflux


class TestSignalHandler:
    """Tests for signal_handler."""

    def test_signal_handler_exits_with_zero(self):
        """signal_handler prints message and exits with 0."""
        with patch("sendtoinflux.sys.exit") as mock_exit:
            sendtoinflux.signal_handler(2, None)
            mock_exit.assert_called_once_with(0)

    def test_signal_handler_accepts_frame(self):
        """signal_handler accepts frame argument (no crash)."""
        with patch("sendtoinflux.sys.exit"):
            sendtoinflux.signal_handler(2, object())


class TestMain:
    """Tests for main."""

    def test_main_dump_mode_prints_json_and_exits(self):
        """main with -d/--dump gets data, prints JSON, and exits 0."""
        mock_handler = MagicMock()
        mock_handler.get_data.return_value = {"temp": 21}
        with patch("sendtoinflux.signal.signal"):
            with patch("sendtoinflux.toinflux.Settings") as mock_settings:
                mock_settings.return_value.toinflux = {"default_source": "hue"}
                with patch("sendtoinflux.toinflux.get_class", return_value=mock_handler):
                    with patch("sendtoinflux.print") as mock_print:
                        with patch("sendtoinflux.sys.argv", ["sendtoinflux", "-d"]):
                            with pytest.raises(SystemExit):
                                sendtoinflux.main()
                            mock_handler.get_data.assert_called_once()
                            mock_print.assert_called_once()
                            call_arg = mock_print.call_args[0][0]
                            assert "temp" in call_arg
                            assert "21" in call_arg

    def test_main_print_mode_one_iteration(self):
        """main with --print runs one loop iteration then we break via sleep."""
        mock_handler = MagicMock()
        mock_handler.get_data.return_value = {"x": 1}
        mock_handler.source_settings = {"interval": 60}

        with patch("sendtoinflux.signal.signal"):
            with patch("sendtoinflux.toinflux.Settings") as mock_settings:
                mock_settings.return_value.toinflux = {"default_source": "hue"}
                with patch("sendtoinflux.toinflux.get_class", return_value=mock_handler):
                    with patch("sendtoinflux.time.time", side_effect=[1000.0, 1060.0]):
                        with patch("sendtoinflux.time.strftime", return_value="Thu, 01 Jan 1970 00:00:00 UTC"):
                            with patch("sendtoinflux.time.sleep") as mock_sleep:
                                # Exit after first sleep to avoid infinite loop
                                mock_sleep.side_effect = SystemExit(0)
                                with pytest.raises(SystemExit):
                                    with patch("sendtoinflux.sys.argv", ["sendtoinflux", "-p"]):
                                        sendtoinflux.main()
                                assert mock_handler.get_data.called

    def test_main_send_mode_one_iteration(self):
        """main without --print sends data once then we break via sleep."""
        mock_handler = MagicMock()
        mock_handler.get_data.return_value = {"x": 1}
        mock_handler.source_settings = {"interval": 60}

        with patch("sendtoinflux.signal.signal"):
            with patch("sendtoinflux.toinflux.Settings") as mock_settings:
                mock_settings.return_value.toinflux = {"default_source": "hue"}
                with patch("sendtoinflux.toinflux.get_class", return_value=mock_handler):
                    with patch("sendtoinflux.time.time", side_effect=[1000.0, 1060.0]):
                        with patch("sendtoinflux.time.sleep") as mock_sleep:
                            mock_sleep.side_effect = SystemExit(0)
                            with pytest.raises(SystemExit):
                                with patch("sendtoinflux.sys.argv", ["sendtoinflux"]):
                                    sendtoinflux.main()
                            mock_handler.send_data.assert_called()

    def test_main_uses_source_arg(self):
        """main with -s source passes source to get_class."""
        mock_handler = MagicMock()
        mock_handler.get_data.return_value = {}
        mock_handler.source_settings = {"interval": 60}
        with patch("sendtoinflux.signal.signal"):
            with patch("sendtoinflux.toinflux.Settings") as mock_settings:
                mock_settings.return_value.toinflux = {"default_source": "hue"}
                with patch("sendtoinflux.toinflux.get_class") as mock_get_class:
                    mock_get_class.return_value = mock_handler
                    with patch("sendtoinflux.time.sleep") as mock_sleep:
                        mock_sleep.side_effect = SystemExit(0)
                        with pytest.raises(SystemExit):
                            with patch("sendtoinflux.sys.argv", ["sendtoinflux", "-s", "zappi"]):
                                sendtoinflux.main()
                        mock_get_class.assert_called_once_with("zappi")
