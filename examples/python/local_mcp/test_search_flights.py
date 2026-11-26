"""Check airport validation without contacting a flight provider."""
import unittest
from datetime import date

from search_flights import summarize


def report(origin, destination):
    leg = {"departure_airport": origin, "arrival_airport": destination,
           "departure_time": "2026-12-10T16:10:00", "airline": "Fixture Air",
           "airline_code": "XX", "flight_number": "123"}
    payload = {"success": True, "flights": [{"legs": [leg], "price": 100, "currency": "USD"}]}
    return summarize(payload, date(2026, 12, 10))


class AirportValidation(unittest.TestCase):
    def test_both_bangkok_airports_and_fli_display_names(self):
        for destination in ("BKK", "DMK", "Suvarnabhumi Airport", "Don Mueang International Airport"):
            with self.subTest(destination=destination):
                row, = report("Ngurah Rai (Bali) International Airport", destination)["flights"]
                self.assertEqual(row["arrival_airport"], destination)

    def test_wrong_reversed_and_missing_endpoints(self):
        for origin, destination in (("SIN", "BKK"), ("DPS", "SIN"), ("BKK", "DPS"), ("DPS", None)):
            with self.subTest(origin=origin, destination=destination):
                with self.assertRaisesRegex(ValueError, "Unexpected airport"):
                    report(origin, destination)
