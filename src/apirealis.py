from abc import ABC, abstractmethod
import requests


class AbstractAPI(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get_data(self, **kwargs):
        pass


class OpenSkyAPI(AbstractAPI):
    def __init__(self):
        self.base_url = "https://opensky-network.org/api/states/all"

    def connect(self):
        # Проверка доступности API (можно реализовать ping запрос)
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


class NominatimAPI(AbstractAPI):
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"

    def connect(self):
        # Проверка доступности API
        try:
            response = requests.get(self.base_url, params={"q": "Russia", "format": "json"})
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def get_data(self, country_name):
        params = {"q": country_name, "format": "json", "limit": 1}
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()
