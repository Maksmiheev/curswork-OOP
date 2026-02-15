import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import src.usercon


class TestOpenSkyModule(unittest.TestCase):

    @patch("src.usercon.requests.get")
    def test_fetch_open_sky_data_no_country(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "states": [["abc123", "CALLSIGN", "Country", None, None, None, None, 1000, None, 200]]
        }
        mock_get.return_value = mock_response

        result = src.usercon.fetch_open_sky_data()
        self.assertEqual(result, [["abc123", "CALLSIGN", "Country", None, None, None, None, 1000, None, 200]])
        mock_get.assert_called_with("https://opensky-network.org/api/states/all", params={})

    @patch("src.usercon.requests.get")
    def test_fetch_open_sky_data_with_country(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "states": [["abc123", "CALLSIGN", "Country", None, None, None, None, 1500, None, 250]]
        }
        mock_get.return_value = mock_response

        result = src.usercon.fetch_open_sky_data("RU")
        self.assertEqual(result, [["abc123", "CALLSIGN", "Country", None, None, None, None, 1500, None, 250]])
        mock_get.assert_called_with("https://opensky-network.org/api/states/all", params={"icao24": "ru"})

    def test_display_top_n_by_altitude(self):
        states = [
            ["id1", "CS1", "Country1", None, None, None, None, 1000, None, 200],
            ["id2", "CS2", "Country2", None, None, None, None, 3000, None, 250],
            ["id3", "CS3", "Country3", None, None, None, None, 2000, None, 220],
        ]
        captured_output = StringIO()

        with patch("sys.stdout", new=captured_output):
            src.usercon.display_top_n_by_altitude(states, 2)

        output = captured_output.getvalue()
        self.assertIn("CS2", output)
        self.assertIn("CS3", output)
        self.assertNotIn("CS1", output)
        self.assertIn("Altitude (m)", output)
        self.assertIn("Velocity (km/h)", output)

    @patch("builtins.input", side_effect=["1", "RU", "3"])
    @patch("src.usercon.fetch_open_sky_data")
    @patch("src.usercon.print")
    def test_main_option_1(self, mock_print, mock_fetch, mock_input):
        mock_fetch.return_value = [["id", "CS1", "RU", None, None, None, None, 1000, None, 250]]
        src.usercon.main()

        mock_fetch.assert_called_with("RU")
        mock_print.assert_any_call(unittest.mock.ANY)

    @patch("builtins.input", side_effect=["2", "1", "3"])
    @patch("src.usercon.fetch_open_sky_data")
    @patch("src.usercon.display_top_n_by_altitude")
    def test_main_option_2(self, mock_display, mock_fetch, mock_input):
        mock_fetch.return_value = [["id", "CS1", "Country", None, None, None, None, 1500, None, 250]]
        src.usercon.main()

        mock_fetch.assert_called_with()
        mock_display.assert_called_with(mock_fetch.return_value, 1)

    @patch("builtins.input", side_effect=["4", "3"])
    @patch("src.usercon.print")
    def test_main_invalid_option(self, mock_print, mock_input):
        src.usercon.main()
        mock_print.assert_any_call("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    unittest.main()
