import requests
from tabulate import tabulate  # pip install tabulate


def fetch_open_sky_data(country_code=None):
    """Запрашиваем данные о самолётах с OpenSky Network API"""
    base_url = "https://opensky-network.org/api/states/all"
    params = {}
    if country_code is not None:
        params['icao24'] = country_code.lower()
    response = requests.get(base_url, params=params)
    data = response.json()
    return data["states"]


def display_top_n_by_altitude(states, n):
    """Отображаем топ-N самолётов по высоте полёта"""
    sorted_states = sorted(states, key=lambda x: x[7], reverse=True)[:n]
    headers = ["Callsign", "Country", "Altitude (m)", "Velocity (km/h)"]
    rows = [[state[1], state[2], state[7], round(state[9] * 3.6)] for state in sorted_states]
    print(tabulate(rows, headers=headers))


def main():
    while True:
        user_input = input("\\nВыберите режим:\\n"
                           "1. Показать самолёты по стране\\n"
                           "2. Топ-N самолётов по высоте полёта\\n"
                           "3. Выход\\n")

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
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
