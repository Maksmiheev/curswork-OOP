import json
from typing import List, Dict
from abc import ABC, abstractmethod
from inforealis import Airplane


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


class JSONStorage(AbstractStorage):
    def __init__(self, filename):
        self.filename = filename
        try:
            with open(filename, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = []

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_airplane(self, airplane: Airplane) -> None:
        self.data.append(
            {
                "registration_country": airplane.registration_country,
                "callsign": airplane.callsign,
                "velocity": airplane.velocity,
                "altitude": airplane.altitude,
            }
        )
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
