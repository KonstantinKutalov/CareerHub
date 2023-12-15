import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from src.main_2 import user_interaction, JSONSaver, print_vacancies, SuperJobAPI


class TestUserInteraction(unittest.TestCase):

    @patch('builtins.input', side_effect=['hh', 'python developer', '5'])
    def test_user_interaction_headhunter(self, mock_input):
        hh_api_mock = MagicMock()
        hh_api_mock.get_vacancies.return_value = [{'title': 'Python Developer', 'link': 'https://example.com'}]
        with patch('src.main_2.HeadHunterAPI', return_value=hh_api_mock):
            user_interaction()
        hh_api_mock.get_vacancies.assert_called_once_with('python developer')

    @patch('builtins.input', side_effect=['superjob', 'java developer', '3'])
    def test_user_interaction_superjob(self, mock_input):
        superjob_api_mock = MagicMock()
        superjob_api_mock.get_vacancies.return_value = [{'profession': 'Java Developer', 'link': 'https://example.com'}]
        with patch('src.main_2.SuperJobAPI', return_value=superjob_api_mock):
            user_interaction()
        superjob_api_mock.get_vacancies.assert_called_once_with('java developer')

    @patch('builtins.input', side_effect=['unsupported', 'superjob', 'java developer', '3'])
    def test_user_interaction_invalid_platform_then_superjob(self, mock_input):
        superjob_api_mock = MagicMock()
        superjob_api_mock.get_vacancies.return_value = [{'profession': 'Java Developer', 'link': 'https://example.com'}]
        with patch('src.main_2.SuperJobAPI', return_value=superjob_api_mock):
            user_interaction()
        superjob_api_mock.get_vacancies.assert_called_once_with('java developer')


class TestPrintVacancies(unittest.TestCase):
    def setUp(self):
        self.top_vacancies_with_profession = [
            {
                'profession': 'Software Engineer',
                'town': {'title': 'New York'},
                'firm_name': 'ABC Company',
                'client': {'url': 'http://example.com'},
                'link': 'http://example.com/vacancy',
                'payment_from': 50000,
                'payment_to': 80000,
                'currency': 'USD',
                'candidat': 'Тут типа информация'
            }
        ]

        self.top_vacancies_without_profession = [
            {
                'name': 'Software Engineer',
                'area': {'name': 'New York'},
                'employer': {'name': 'ABC Company'},
                'alternate_url': 'http://example.com/vacancy',
                'salary': {'from': 50000, 'to': 80000, 'currency': 'USD'},
                'snippet': {'responsibility': 'Тут типа информация'}
            }
        ]

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_vacancies_with_profession(self, mock_stdout):
        print_vacancies(self.top_vacancies_with_profession)
        expected_output = """Список верхних вакансий:
Вакансия 1:
Название: Software Engineer
Город: New York
Работодатель: ABC Company
Ссылка на работодателя: http://example.com
Ссылка на вакансию: http://example.com/vacancy
Зарплата: от 50000 до 80000 USD
Информация по вакансии: Тут типа информация
-----------------------------------------
"""
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_vacancies_without_profession(self, mock_stdout):
        print_vacancies(self.top_vacancies_without_profession)
        expected_output = """Список верхних вакансий:
Вакансия 1:
Название: Software Engineer
Город: New York
Работодатель: ABC Company
Ссылка на вакансию: http://example.com/vacancy
Зарплата: от 50000 до 80000 USD
Информация по вакансии: Тут типа информация
-----------------------------------------
"""
        self.assertEqual(mock_stdout.getvalue(), expected_output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_vacancies_no_vacancies(self, mock_stdout):
        print_vacancies([])
        expected_output = "Нет доступных вакансий для вывода.\n"
        self.assertEqual(mock_stdout.getvalue(), expected_output)


class TestSuperJobAPI(unittest.TestCase):

    @patch('src.main_2.requests.get')
    def test_get_vacancies(self, mock_requests_get):
        superjob = SuperJobAPI()

        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {'objects': []}

        vacancies = superjob.get_vacancies('python developer')
        self.assertEqual(vacancies, [])


if __name__ == '__main__':
    unittest.main()
