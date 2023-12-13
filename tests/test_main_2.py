import unittest
from unittest.mock import Mock, patch
from src.main_2 import (
    HeadHunterAPI,
    SuperJobAPI,
    JSONSaver,
    filter_vacancies,
    sort_vacancies,
    sort_vacancies_by_salary,
    get_top_vacancies,
    user_interaction,
    extract_salary,
)


class TestHeadHunterAPI(unittest.TestCase):
    def setUp(self):
        self.hh_api = HeadHunterAPI()

    def test_get_vacancies(self):
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'items': []}
            mock_get.return_value = mock_response

            vacancies = self.hh_api.get_vacancies('software engineer')
            self.assertEqual(vacancies, [])
            mock_get.assert_called_once()


class TestSuperJobAPI(unittest.TestCase):
    def setUp(self):
        self.superjob_api = SuperJobAPI()

    def test_get_vacancies(self):
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'objects': []}
            mock_get.return_value = mock_response

            vacancies = self.superjob_api.get_vacancies('software engineer')
            self.assertEqual(vacancies, [])
            mock_get.assert_called_once()


class TestJSONSaver(unittest.TestCase):
    def setUp(self):
        self.json_saver = JSONSaver()

    def test_add_vacancy(self):
        with patch('builtins.open', create=True) as mock_open:
            mock_file = mock_open.return_value
            self.json_saver.add_vacancy('test_file.json', [])
            mock_file.__enter__.return_value.write.assert_called_once()



class TestFunctions(unittest.TestCase):
    def test_extract_salary(self):
        salary_data = {'from': 50000, 'to': 80000, 'currency': 'RUB'}
        result = extract_salary(salary_data)
        self.assertEqual(result, (50000, 80000))



if __name__ == '__main__':
    unittest.main()
