import unittest
from src.inforealis import Airplane


class TestAirplane(unittest.TestCase):

    def test_init_and_strip_callsign(self):
        a = Airplane("USA", " ABC123 ", "850", "10000")
        self.assertEqual(a.registration_country, "USA")
        self.assertEqual(a.callsign, "ABC123")
        self.assertEqual(a.velocity, 850.0)
        self.assertEqual(a.altitude, 10000.0)

    def test_callsign_default_and_none(self):
        a1 = Airplane("Russia", None, 900, 11000)
        self.assertEqual(a1.callsign, "N/A")

        a2 = Airplane("Russia", "", 900, 11000)
        self.assertEqual(a2.callsign, "N/A")

    def test_validate_float_valid_and_invalid(self):
        a = Airplane("USA", "CS1", "250.5", "5000")
        self.assertEqual(a.velocity, 250.5)
        self.assertEqual(a.altitude, 5000.0)

        a = Airplane("USA", "CS2", "not-a-number", None)
        self.assertEqual(a.velocity, 0.0)
        self.assertEqual(a.altitude, 0.0)

    def test_comparison_lt(self):
        a1 = Airplane("CountryA", "A1", 300, 5000)
        a2 = Airplane("CountryB", "B1", 400, 10000)
        self.assertTrue(a1 < a2)
        self.assertFalse(a2 < a1)

    def test_comparison_eq(self):
        a1 = Airplane("CountryA", "A1", 300, 5000)
        a2 = Airplane("CountryB", "B2", 300, 5000)
        a3 = Airplane("CountryC", "C3", 400, 5000)
        self.assertTrue(a1 == a2)
        self.assertFalse(a1 == a3)

    def test_comparison_gt(self):
        a1 = Airplane("CountryA", "A1", 300, 5000)
        a2 = Airplane("CountryB", "B1", 400, 4000)
        self.assertTrue(a2 > a1)  # по скорости
        self.assertFalse(a1 > a2)

    def test_repr(self):
        a = Airplane("France", "AF123", "750.5", "12000")
        expected = "<Airplane AF123 from France Alt:12000.0 Vel:750.5>"
        self.assertEqual(repr(a), expected)


if __name__ == "__main__":
    unittest.main()
