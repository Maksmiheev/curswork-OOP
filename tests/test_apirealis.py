import unittest
from unittest.mock import patch, Mock
from src.apirealis import OpenSkyAPI, NominatimAPI
import requests


class TestOpenSkyAPI(unittest.TestCase):

    @patch("requests.get")
    def test_connect_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None  # нет исключения
        mock_get.return_value = mock_response

        api = OpenSkyAPI()
        result = api.connect()
        self.assertTrue(result)
        mock_get.assert_called_once_with(api.base_url)

    @patch("requests.get")
    def test_connect_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException

        api = OpenSkyAPI()
        result = api.connect()
        self.assertFalse(result)

    @patch("requests.get")
    def test_get_data_success(self, mock_get):
        expected_json = {"states": []}
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        api = OpenSkyAPI()
        result = api.get_data()
        self.assertEqual(result, expected_json)
        mock_get.assert_called_once_with(api.base_url)

    @patch("requests.get")
    def test_get_data_raises(self, mock_get):
        mock_get.side_effect = requests.RequestException

        api = OpenSkyAPI()
        with self.assertRaises(requests.RequestException):
            api.get_data()


class TestNominatimAPI(unittest.TestCase):

    @patch("requests.get")
    def test_connect_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        api = NominatimAPI()
        result = api.connect()
        self.assertTrue(result)
        mock_get.assert_called_once_with(api.base_url, params={"q": "Russia", "format": "json"})

    @patch("requests.get")
    def test_connect_failure(self, mock_get):
        mock_get.side_effect = requests.RequestException

        api = NominatimAPI()
        result = api.connect()
        self.assertFalse(result)

    @patch("requests.get")
    def test_get_data_success(self, mock_get):
        expected_json = [{"lat": "55.7558", "lon": "37.6173", "display_name": "Russia"}]
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = expected_json
        mock_get.return_value = mock_response

        api = NominatimAPI()
        result = api.get_data("Russia")
        self.assertEqual(result, expected_json)
        mock_get.assert_called_once_with(api.base_url, params={"q": "Russia", "format": "json", "limit": 1})

    @patch("requests.get")
    def test_get_data_raises(self, mock_get):
        mock_get.side_effect = requests.RequestException

        api = NominatimAPI()
        with self.assertRaises(requests.RequestException):
            api.get_data("Russia")


if __name__ == "__main__":
    unittest.main()
