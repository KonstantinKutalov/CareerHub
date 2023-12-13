import json
import os
from abc import ABC, abstractmethod
from colorama import Fore, Style
import requests
from datetime import datetime


class ApiClient(ABC):
    """Класс для получения вакансий с помощью API"""

    @abstractmethod
    def get_vacancies(self, vacancy, page=None):
        pass


class HeadHunterAPI(ApiClient):
    BASE_URL = 'https://api.hh.ru/'

    def get_vacancies(self, vacancy, page=None):
        url = f"{self.BASE_URL}vacancies"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        params = {
            'text': vacancy,
            'page': page
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            vacancies = response.json()['items']
            return vacancies
        else:
            print(f"Failed to fetch vacancies from HeadHunter API: {response.status_code}")
            print(response.content)
            return []


class SuperJobAPI(ApiClient):
    BASE_URL = 'https://api.superjob.ru/2.0/'

    def get_vacancies(self, vacancy, page=None):
        secret_key = os.getenv('TOKEN_SUPERJOB')
        url = f"{self.BASE_URL}vacancies/"
        headers = {
            'X-Api-App-Id': secret_key
        }
        params = {
            'keyword': vacancy,
            'page': page,
            'count': 100
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()["objects"]
        else:
            print(f"Failed to fetch vacancies from SuperJob API: {response.status_code}")
            return []


class Vacancy:
    def __init__(self, title, link, salary, description):
        self.title = title
        self.link = link
        self.salary = salary
        self.description = description


class JSONSaver:
    def add_vacancy(self, file_name, vacancies):
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(vacancies, file, ensure_ascii=False, indent=4)

    def get_vacancies_by_salary(self, salary):
        pass

    def delete_vacancy(self, vacancy):
        pass


def extract_salary(salary_data):
    if salary_data and 'from' in salary_data:
        # Для HeadHunter
        from_salary = salary_data['from']
        to_salary = salary_data['to']
        currency = salary_data['currency']

        # Возвращаем кортеж из двух числовых значений (от и до зарплаты), если они указаны
        return from_salary, to_salary
    elif 'payment_from' in salary_data:
        # Для SuperJob
        payment_from = salary_data['payment_from']
        payment_to = salary_data['payment_to']
        currency = salary_data['currency']

        # Возвращаем кортеж из двух числовых значений (от и до зарплаты), если они указаны
        return payment_from, payment_to
    else:
        return None  # Если нет информации о зарплате


def filter_vacancies(hh_vacancies, superjob_vacancies, filter_words):
    filtered_vacancies = []

    # Фильтрация вакансий от HeadHunter
    for vacancy in hh_vacancies:
        salary_info = extract_salary(vacancy.get('salary'))
        if 'salary' in vacancy and all(word.lower() in vacancy['name'].lower() or
                                       word.lower() in vacancy['snippet']['requirement'].lower() or
                                       word.lower() in vacancy['snippet']['responsibility'].lower() for word in
                                       filter_words):
            filtered_vacancies.append(vacancy)

    # Фильтрация вакансий от SuperJob
    for vacancy in superjob_vacancies:
        salary_info = extract_salary(vacancy)
        if all(word.lower() in vacancy['profession'].lower() for word in filter_words):
            filtered_vacancies.append(vacancy)

    return filtered_vacancies


def sort_vacancies(vacancies, top_n):
    # Сортировка вакансий от HeadHunter по 'published_at' или 'created_at' в порядке убывания
    sorted_hh_vacancies = sorted(
        [vacancy for vacancy in vacancies if 'published_at' in vacancy or 'created_at' in vacancy],
        key=lambda x: x.get('published_at', x.get('created_at')),
        reverse=True
    )

    # Сортировка вакансий от SuperJob по 'payment_from' в порядке убывания
    sorted_sj_vacancies = sorted(
        [vacancy for vacancy in vacancies if 'payment_from' in vacancy],
        key=lambda x: x.get('payment_from', 0),
        reverse=True
    )

    # Объединение отсортированных списков вакансий от HeadHunter и SuperJob
    sorted_vacancies = sorted_hh_vacancies + sorted_sj_vacancies

    return sorted_vacancies[:top_n]


def print_vacancies(top_vacancies):
    if not top_vacancies:
        print("Нет доступных вакансий для вывода.")
        return

    print("Список верхних вакансий:")
    for index, vacancy in enumerate(top_vacancies, start=1):
        print(f"Вакансия {index}:")
        if 'profession' in vacancy:  # Проверка наличия поля для SuperJob
            print(f"Название: {vacancy.get('profession', 'Нет информации')}")
            print(f"Город: {vacancy.get('town', 'Нет информации')}")
            print(f"Работодатель: {vacancy.get('firm_name', 'Нет информации')}")
            client_info = vacancy.get('client', {})
            client_url = client_info.get('url', 'Нет информации') if 'url' in client_info else 'Нет информации'
            print(f"Ссылка на работодателя: {client_url if client_url else 'Нет информации'}")
            print(f"Ссылка на вакансию: {vacancy.get('link', 'Нет информации')}")
            # Вывод по ЗП
            payment_from = vacancy.get('payment_from')
            payment_to = vacancy.get('payment_to')
            currency = vacancy.get('currency')
            if payment_from is not None:
                payment_range = f"от {payment_from} до {payment_to} {currency}" if payment_to else f"{payment_from} {currency}"
                print(f"Зарплата: {payment_range}")
            else:
                print("Информация о зарплате отсутствует")
            # Вывод краткой информации
            candidate_info = vacancy.get('candidat', 'Нет информации')
            candidate_info = candidate_info[:150] + f"{Fore.RED}...перейди по ссылке выше чтобы узнать больше{Style.RESET_ALL}" if len(candidate_info) > 120 else candidate_info
            print(f"Информация по вакансии: {candidate_info}")


        else:  # Для HeadHunter
            print(f"Название: {vacancy.get('name', 'Нет информации')}")
            print(f"Город: {vacancy.get('area', {}).get('name', 'Нет информации')}")
            print(f"Работодатель: {vacancy.get('employer', {}).get('name', 'Нет информации')}")
            print(f"Ссылка на вакансию: {vacancy.get('alternate_url', 'Нет информации')}")
            # Вывод по ЗП
            salary_info = ""
            salary_data = vacancy.get('salary')
            if salary_data:
                from_salary = salary_data.get('from')
                to_salary = salary_data.get('to')
                currency = salary_data.get('currency')
                if from_salary is not None and to_salary is not None:
                    salary_info = f"Зарплата: от {from_salary} до {to_salary} {currency}"
                elif from_salary is not None:
                    salary_info = f"Зарплата: от {from_salary} {currency}"
                elif to_salary is not None:
                    salary_info = f"Зарплата: до {to_salary} {currency}"
                else:
                    salary_info = "Информация о зарплате отсутствует"
            else:
                salary_info = "Информация о зарплате отсутствует"
            print(salary_info)
            # Вывод краткой информации
            snippet_responsibility = vacancy.get('snippet', {}).get('responsibility', 'Нет информации')
            snippet_responsibility = snippet_responsibility[:150] + f"{Fore.RED}...перейди по ссылке выше чтобы узнать больше{Style.RESET_ALL}" if len(
                snippet_responsibility) > 120 else snippet_responsibility
            print(f"Информация по вакансии: {snippet_responsibility}")

        print("-----------------------------------------")


def get_top_vacancies(sorted_vacancies, top_n):
    top_vacancies = sorted_vacancies[:top_n]
    return top_vacancies



def sort_vacancies_by_salary(hh_vacancies, superjob_vacancies):
    # Сортировка вакансий HeadHunter по зарплате (только от)
    sorted_hh_vacancies = sorted(
        [vacancy for vacancy in hh_vacancies if 'salary' in vacancy and vacancy['salary']['from'] is not None and vacancy['salary']['to'] is None],
        key=lambda x: x['salary']['from'],
        reverse=True
    )

    # Сортировка вакансий SuperJob по зарплате (только от)
    sorted_superjob_vacancies = sorted(
        [vacancy for vacancy in superjob_vacancies if 'payment_from' in vacancy and vacancy['payment_from'] is not None and vacancy['payment_to'] is None],
        key=lambda x: x['payment_from'],
        reverse=True
    )

    # Объединение отсортированных списков вакансий от HeadHunter и SuperJob
    sorted_vacancies = sorted_hh_vacancies + sorted_superjob_vacancies

    return sorted_vacancies


def user_interaction():
    hh_api = HeadHunterAPI()
    superjob_api = SuperJobAPI()
    json_saver = JSONSaver()

    platform_choice = input("Введите платформу для поиска вакансий (HH или SuperJob): ").lower()
    search_query = input("Введите поисковый запрос: ")
    top_n = int(input("Введите количество вакансий для вывода в топ N: "))

    hh_vacancies = []
    superjob_vacancies = []

    if platform_choice in ['hh', 'headhunter', 'хх', 'хедантер', "хэдхантер"]:  # Выбор HeadHunter
        hh_vacancies = hh_api.get_vacancies(search_query)
        if not hh_vacancies:
            print("Нет вакансий на HeadHunter, соответствующих заданным критериям.")
    elif platform_choice in ['superjob', 'sj', 'SuperJob', 'суперджоб', 'сд']:  # Выбор SuperJob
        superjob_vacancies = superjob_api.get_vacancies(search_query)
        if not superjob_vacancies:
            print("Нет вакансий на SuperJob, соответствующих заданным критериям.")
    else:
        print("Выбранная платформа не поддерживается.")
        return

    json_saver.add_vacancy('hh_vacancies.json', hh_vacancies)
    json_saver.add_vacancy('superjob_vacancies.json', superjob_vacancies)

    filtered_vacancies = filter_vacancies(hh_vacancies, superjob_vacancies, [])

    # Объединение вакансий из HeadHunter и SuperJob в один список для последующей сортировки
    all_vacancies = hh_vacancies + superjob_vacancies

    # Сортировка всех вакансий
    sorted_vacancies = sort_vacancies(all_vacancies, top_n)

    # Сортировка вакансий по заработной плате
    sorted_by_salary = sort_vacancies_by_salary(filtered_vacancies, superjob_vacancies)

    # Получение списка верхних вакансий по общей сортировке
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)

    # Получение списка верхних вакансий по сортировке по заработной плате
    top_vacancies_salary_sorted = get_top_vacancies(sorted_by_salary, top_n)

    # Выводите список верхних вакансий
    print("\nСписок верхних вакансий:")
    print_vacancies(top_vacancies)

    # Выводите список верхних вакансий, отсортированных по заработной плате
    print("\nСписок верхних вакансий (отсортированных по заработной плате):")
    print_vacancies(top_vacancies_salary_sorted)


if __name__ == "__main__":
    user_interaction()



# Точка невозврата