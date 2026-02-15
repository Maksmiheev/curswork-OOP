import unittest
from unittest.mock import patch, mock_open
from src.workclass import JSONStorage
from src.inforealis import Airplane


class TestJSONStorage(unittest.TestCase):

    def setUp(self):
        # Создаем пример объекта Airplane
        self.plane = Airplane(
            registration_country="RU",
            callsign="CALL123",
            velocity=900,
            altitude=10000,
        )

    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    def test_init_loads_empty_list_when_file_not_found_or_empty(self, mock_file):
        storage = JSONStorage("fakefile.json")
        self.assertEqual(storage.data, [])
        mock_file.assert_called_once_with("fakefile.json", "r")

    @patch("builtins.open", new_callable=mock_open, read_data='[{"registration_country": "RU"}]')
    def test_init_loads_data_from_file(self):
        storage = JSONStorage("fakefile.json")
        self.assertEqual(len(storage.data), 1)
        self.assertEqual(storage.data[0]["registration_country"], "RU")

    @patch("builtins.open", new_callable=mock_open)
    def test_add_airplane_appends_and_saves(self):
        storage = JSONStorage("fakefile.json")
        storage.data = []

        with patch.object(storage, "save") as mock_save:
            storage.add_airplane(self.plane)
            self.assertEqual(len(storage.data), 1)
            self.assertEqual(storage.data[0]["callsign"], "CALL123")
            mock_save.assert_called_once()

    def test_get_by_criteria_returns_matching(self):
        storage = JSONStorage("fakefile.json")
        storage.data = [
            {"registration_country": "RU", "callsign": "CS1", "velocity": 900, "altitude": 10000},
            {"registration_country": "US", "callsign": "CS2", "velocity": 850, "altitude": 9000},
        ]

        result = storage.get_by_criteria({"registration_country": "RU"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["callsign"], "CS1")

        result_empty = storage.get_by_criteria({"registration_country": "FR"})
        self.assertEqual(result_empty, [])

    @patch("builtins.open", new_callable=mock_open)
    def test_delete_airplanes_removes_and_saves(self):
        storage = JSONStorage("fakefile.json")
        storage.data = [
            {"registration_country": "RU", "callsign": "CS1"},
            {"registration_country": "US", "callsign": "CS2"},
        ]

        with patch.object(storage, "save") as mock_save:
            storage.delete_airplanes({"registration_country": "RU"})
            self.assertEqual(len(storage.data), 1)
            self.assertEqual(storage.data[0]["registration_country"], "US")
            mock_save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
