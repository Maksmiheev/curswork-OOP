from abc import ABC, abstractmethod
import requests
from tabulate import tabulate  # pip install tabulate
import json
from typing import List, Dict


# Базовый абстрактный класс для API
class AbstractAPI(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_data(self, **kwargs):
        pass


# Конкретизация OpenSky API
class OpenSkyAPI(AbstractAPI):
    def __init__(self):
        self.base_url = "https://opensky-network.org/api/states/all"

    def connect(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def get_data(self, **kwargs):
        response = requests.get(self.base_url)
        response.raise_for_status()
        return response.json()


# Конкретизация Nominatim API
class NominatimAPI(AbstractAPI):
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"

    def connect(self):
        try:
            response = requests.get(self.base_url, params={'q': 'Russia', 'format': 'json'})
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def get_data(self, country_name):
        params = {'q': country_name, 'format': 'json', 'limit': 1}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()


# Класc самолёта
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
        return self.altitude < other.altitude

    def __eq__(self, other):
        return (self.velocity == other.velocity) and (self.altitude == other.altitude)

    def __gt__(self, other):
        return self.velocity > other.velocity

    def __repr__(self):
        return f"<Airplane {self.callsign} from {self.registration_country} Alt:{self.altitude} Vel:{self.velocity}>"


# Базовый абстрактный класс хранилища
class AbstractStorage(ABC):
    @abstractmethod
    def add_airplane(self, airplane: Airplane) -> None:
        pass

    @abstractmethod
    def get_by_criteria(self, criteria: Dict) -> List[Dict]:
        pass

    @abstractmethod
    def delete_airplanes(self, conditions: Dict) -> None:
        pass


# Хранилище на основе JSON-файлов
class JSONStorage(AbstractStorage):
    def __init__(self, filename):
        self.filename = filename
        try:
            with open(filename, 'r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_airplane(self, airplane: Airplane) -> None:
        self.data.append({
            "registration_country": airplane.registration_country,
            "callsign": airplane.callsign,
            "velocity": airplane.velocity,
            "altitude": airplane.altitude
        })
        self.save()

    def get_by_criteria(self, criteria: Dict) -> List[Dict]:
        result = []
        for item in self.data:
            if all(item.get(k) == v for k, v in criteria.items()):
                result.append(item)
        return result

    def delete_airplanes(self, conditions: Dict) -> None:
        self.data = [item for item in self.data if not all(item.get(k) == v for k, v in conditions.items())]
        self.save()


# Получение данных о самолётах с OpenSky API
def fetch_open_sky_data(country_code=None):
    base_url = "https://opensky-network.org/api/states/all"
    params = {}
    if country_code is not None:
        params['icao24'] = country_code.lower()
    response = requests.get(base_url, params=params)
    data = response.json()
    return data["states"]


# Отображение списка самолётов
def display_top_n_by_altitude(states, n):
    sorted_states = sorted(states, key=lambda x: x[7], reverse=True)[:n]
    headers = ["Callsign", "Country", "Altitude (m)", "Velocity (km/h)"]
    rows = [[state[1], state[2], state[7], round(state[9] * 3.6)] for state in sorted_states]
    print(tabulate(rows, headers=headers))


# Основная логика приложения
def main():
    storage = JSONStorage('airplanes.json')

    while True:
        user_input = input(
            "\nВыберите режим:\n"
            "1. Показать самолёты по стране\n"
            "2. Топ-N самолётов по высоте полёта\n"
            "3. Сохранить самолёт в базу данных\n"
            "4. Найти самолёты по критериям\n"
            "5. Удалить самолёты по условиям\n"
            "6. Выход\n"
        )

        if user_input == '1':
            country_code = input("Введите код страны (например RU для России): ").strip().upper()
            states = fetch_open_sky_data(country_code)
            if not states:
                print("Нет данных о самолётах для выбранной страны.")
            else:
                headers = ["Callsign", "Country", "Altitude (m)", "Velocity (km/h)"]
                rows = [[state[1], state[2], state[7], round(state[9] * 3.6)] for state in states]
                print(tabulate(rows, headers=headers))

        elif user_input == '2':
            n = int(input("Введите число N для отображения топ-N самолётов: "))
            states = fetch_open_sky_data()
            display_top_n_by_altitude(states, n)

        elif user_input == '3':
            reg_country = input("Регистрационная страна: ")
            callsign = input("Позывной: ")
            vel = float(input("Скорость (км/ч): "))
            alt = float(input("Высота (метры): "))
            plane = Airplane(reg_country, callsign, vel / 3.6, alt)
            storage.add_airplane(plane)
            print("Самолёт успешно сохранён в базу данных.")

        elif user_input == '4':
            crit_reg_country = input("Критерий по регистрационной стране (оставьте пустым, если неважно): ")
            crit_callsign = input("Критерий по позывному (оставьте пустым, если неважно): ")
            crit_velocity = input("Критерий по скорости (оставьте пустым, если неважно): ")
            crit_altitude = input("Критерий по высоте (оставьте пустым, если неважно): ")
            criteria = {}
            if crit_reg_country:
                criteria['registration_country'] = crit_reg_country
            if crit_callsign:
                criteria['callsign'] = crit_callsign
            if crit_velocity:
                criteria['velocity'] = float(crit_velocity)
            if crit_altitude:
                criteria['altitude'] = float(crit_altitude)
            results = storage.get_by_criteria(criteria)
            print(json.dumps(results, indent=4))

        elif user_input == '5':
            cond_reg_country = input("Удалять по критерию регистрации страны (оставьте пустым, если неважно): ")
            cond_callsign = input("Удалять по критерию позывного (оставьте пустым, если неважно): ")
            cond_velocity = input("Удалять по критерию скорости (оставьте пустым, если неважно): ")
            cond_altitude = input("Удалять по критерию высоты (оставьте пустым, если неважно): ")
            conditions = {}
            if cond_reg_country:
                conditions['registration_country'] = cond_reg_country
            if cond_callsign:
                conditions['callsign'] = cond_callsign
            if cond_velocity:
                conditions['velocity'] = float(cond_velocity)
            if cond_altitude:
                conditions['altitude'] = float(cond_altitude)
            storage.delete_airplanes(conditions)
            print("Самолёты удалены согласно указанным условиям.")

        elif user_input == '6':
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()