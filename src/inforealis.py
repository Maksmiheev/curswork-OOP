class Airplane:
    def __init__(self, registration_country, callsign, velocity, altitude):
        self.registration_country = registration_country
        self.callsign = callsign.strip() if callsign else "N/A"
        self.velocity = self.validate_float(velocity)
        self.altitude = self.validate_float(altitude)

    @staticmethod
    def validate_float(value):
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    def __lt__(self, other):
        # сравнение по высоте
        return self.altitude < other.altitude

    def __eq__(self, other):
        return (self.velocity == other.velocity) and (self.altitude == other.altitude)

    def __gt__(self, other):
        # сравнение по скорости
        return self.velocity > other.velocity

    def __repr__(self):
        return f"<Airplane {self.callsign} from {self.registration_country} Alt:{self.altitude} Vel:{self.velocity}>"
