import unittest
from unittest.mock import patch, MagicMock
from src.apirealis import OpenSkyAPI, NominatimAPI
from src.inforealis import Airplane
from src.workclass import JSONStorage
import tempfile
import os
import json


# Тесты для OpenSkyAPI
class TestOpenSkyAPI(unittest.TestCase):

    @patch("your_module.requests.get")
    def test_connect_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        api = OpenSkyAPI()
        self.assertTrue(api.connect())
        mock_get.assert_called_with(api.base_url)

    @patch("your_module.requests.get")
    def test_connect_failure(self, mock_get):
        mock_get.side_effect = Exception("Error")
        api = OpenSkyAPI()
        self.assertFalse(api.connect())

    @patch("your_module.requests.get")
    def test_get_data(self, mock_get):
        expected_data = {"states": []}
        mock_resp = MagicMock()
        mock_resp.json.return_value = expected_data
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        api = OpenSkyAPI()
        data = api.get_data()
        self.assertEqual(data, expected_data)
        mock_get.assert_called_with(api.base_url)


# Тесты для NominatimAPI
class TestNominatimAPI(unittest.TestCase):

    @patch("your_module.requests.get")
    def test_connect_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        api = NominatimAPI()
        self.assertTrue(api.connect())
        mock_get.assert_called_with(api.base_url, params={"q": "Russia", "format": "json"})

    @patch("your_module.requests.get")
    def test_connect_failure(self, mock_get):
        mock_get.side_effect = Exception("Error")
        api = NominatimAPI()
        self.assertFalse(api.connect())

    @patch("your_module.requests.get")
    def test_get_data(self, mock_get):
        expected_data = [{"display_name": "Russia"}]
        mock_resp = MagicMock()
        mock_resp.json.return_value = expected_data
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        api = NominatimAPI()
        data = api.get_data("Russia")
        self.assertEqual(data, expected_data)
        mock_get.assert_called_with(api.base_url, params={"q": "Russia", "format": "json", "limit": 1})


# Тесты для Airplane
class TestAirplane(unittest.TestCase):

    def test_callsign_strip_or_default(self):
        a1 = Airplane("USA", " ABC123 ", 500, 10000)
        self.assertEqual(a1.callsign, "ABC123")

        a2 = Airplane("USA", None, 500, 10000)
        self.assertEqual(a2.callsign, "N/A")

        a3 = Airplane("USA", "", 500, 10000)
        self.assertEqual(a3.callsign, "N/A")

    def test_validate_float(self):
        self.assertEqual(Airplane.validate_float("123.45"), 123.45)
        self.assertEqual(Airplane.validate_float(None), 0.0)
        self.assertEqual(Airplane.validate_float("abc"), 0.0)

    def test_comparisons(self):
        a1 = Airplane("A", "CS1", 300, 1000)
        a2 = Airplane("B", "CS2", 400, 2000)

        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

        a3 = Airplane("C", "CS3", 300, 1000)
        self.assertTrue(a1 == a3)
        self.assertFalse(a1 == a2)

        self.assertTrue(a2 > a1)
        self.assertFalse(a1 > a2)

    def test_repr(self):
        a = Airplane("Russia", "AB123", 700, 12000)
        expected = "<Airplane AB123 from Russia Alt:12000.0 Vel:700.0>"
        self.assertEqual(repr(a), expected)


# Тесты для JSONStorage
class TestJSONStorage(unittest.TestCase):

    def setUp(self):
        # Создаем временный файл с пустым json-массивом
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+")
        self.temp_file.write("[]")
        self.temp_file.close()
        self.storage = JSONStorage(self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_add_airplane(self):
        plane = Airplane("USA", "CS123", 500, 10000)
        self.storage.add_airplane(plane)

        with open(self.temp_file.name, "r") as f:
            data = json.load(f)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["callsign"], "CS123")

    def test_get_by_criteria(self):
        self.storage.data = [
            {"registration_country": "USA", "callsign": "CS1", "velocity": 300, "altitude": 1000},
            {"registration_country": "Russia", "callsign": "CS2", "velocity": 400, "altitude": 2000},
            {"registration_country": "USA", "callsign": "CS3", "velocity": 500, "altitude": 3000},
        ]
        self.storage.save()

        result = self.storage.get_by_criteria({"registration_country": "USA"})
        self.assertEqual(len(result), 2)

        result = self.storage.get_by_criteria({"callsign": "CS2"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["registration_country"], "Russia")

    def test_delete_airplanes(self):
        self.storage.data = [
            {"registration_country": "USA", "callsign": "CS1", "velocity": 300, "altitude": 1000},
            {"registration_country": "Russia", "callsign": "CS2", "velocity": 400, "altitude": 2000},
            {"registration_country": "USA", "callsign": "CS3", "velocity": 500, "altitude": 3000},
        ]
        self.storage.save()

        self.storage.delete_airplanes({"registration_country": "USA"})

        self.assertEqual(len(self.storage.data), 1)
        self.assertEqual(self.storage.data[0]["registration_country"], "Russia")


if __name__ == "__main__":
    unittest.main()
