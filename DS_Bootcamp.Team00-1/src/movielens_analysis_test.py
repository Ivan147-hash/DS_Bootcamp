import pandas as pd
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from collections import defaultdict, OrderedDict
from movielens_analysis import Tags
from movielens_analysis import Movies
from movielens_analysis import Ratings
from movielens_analysis import Links

#################################################################################
################################ get_imdb #######################################
#################################################################################
@pytest.fixture
def links_instance():
        """Фикстура для создания экземпляра Links."""
        return Links('data/ml-latest-small/links.csv')

class TestGetimdb:
    def test_get_imdb_empty_lists(self, links_instance):
        """Тест на пустые списки movie_ids и fields."""
        with pytest.raises(ValueError):
            asyncio.run(links_instance.get_imdb([], []))

    def test_get_imdb_empty_movie_ids(self, links_instance):
        """Тест на пустой список movie_ids."""
        with pytest.raises(ValueError):
            asyncio.run(links_instance.get_imdb([], ['Director']))

    def test_get_imdb_empty_fields(self, links_instance):
        """Тест на пустой список fields."""
        with pytest.raises(ValueError):
            asyncio.run(links_instance.get_imdb([1, 2, 3], []))


    @patch('movielens_analysis.Links.parse_imdb')
    @patch('movielens_analysis.Links.async_get')
    def test_get_imdb_valid_input(self, mock_async_get, mock_parse_imdb, links_instance): # links_instance в аргументах
        """Тест на валидные входные данные."""

        # Mocking external dependencies
        links_instance.data = [
            ['1', '0114709'],  # Toy Story (1995)
            ['2', '0113497'],  # Jumanji (1995)
            ['3', '0113228'],  # Grumpier Old Men (1995)
        ]

        mock_async_get.return_value = ['html_content_1', 'html_content_2']

        mock_parse_imdb.return_value = [
            ['2', 'Joe Johnston', '65000000', '262797249', '104 minutes'],
            ['1', 'John Lasseter', '30000000', '373554033', '81 minutes'],
        ]

        # Call the method with test data
        movie_ids = ['1', '2']
        fields = ['Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']
        result = links_instance.get_imdb(movie_ids, fields)

        # Assertions

        # Verify calls
        mock_async_get.assert_called_once_with(
            ['https://www.imdb.com/title/tt0114709/', 'https://www.imdb.com/title/tt0113497/'],
            {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        )
        mock_parse_imdb.assert_called_once_with(
            ['html_content_1', 'html_content_2'],
            ['Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime'],
            ['1', '2']
        )

        # Verify result
        assert result == [
            ['2', 'Joe Johnston', '65000000', '262797249', '104 minutes'],
            ['1', 'John Lasseter', '30000000', '373554033', '81 minutes'],
        ]

    @patch('movielens_analysis.Links.parse_imdb')
    @patch('movielens_analysis.Links.async_get')
    def test_get_imdb_movie_not_found(self, mock_async_get, mock_parse_imdb, links_instance):
        """Тест, когда movie_id не найден в links.csv."""

        # Mocking external dependencies
        links_instance.data = [
            ['1', '0114709'],
            ['2', '0113497'],
        ]
        mock_async_get.return_value = []
        mock_parse_imdb.return_value = []

        movie_ids = ['3']  # Movie ID, которого нет в links.csv
        fields = ['Director']
        result = links_instance.get_imdb(movie_ids, fields)

        assert result == []  # Проверяем, что возвращается пустой список


    @patch('movielens_analysis.Links.read_links_id')
    def test_get_imdb_read_links_id_exception(self, mock_read_links_id):
        """Тест на случай, когда read_links_id вызывает исключение."""
        mock_read_links_id.side_effect = Exception("Error reading links file")  # Имитируем ошибку чтения

        movie_ids = ['1', '2']
        fields = ['Director']

        with pytest.raises(Exception, match="Error reading links file"):  # Проверяем, что исключение перехвачено
            Links.get_imdb(movie_ids, fields)

#################################################################################
########################### top_directors #######################################
#################################################################################
@pytest.fixture
def links_instance():
        """Фикстура для создания экземпляра Links."""
        return Links('data/ml-latest-small/links.csv')

class TestTopDirectors:
    @patch('movielens_analysis.Links.get_imdb')
    def test_top_directors_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3'], ['4']]

        mock_get_imdb.return_value = [
            ['1', 'Director A'],
            ['2', 'Director B'],
            ['3', 'Director A'],
            ['4', 'Director C'],
        ]

        result = links_instance.top_directors(2)

        assert result == {'Director A': 2, 'Director B': 1}
        mock_get_imdb.assert_called_once_with(['1', '2', '3', '4'], ['movieId', 'Director'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_directors_n_greater_than_num_directors(self, mock_get_imdb, links_instance):
        """Тест, когда n больше чем число режиссеров."""
        links_instance.data = [['1'], ['2'], ['3']]

        mock_get_imdb.return_value = [
            ['1', 'Director A'],
            ['2', 'Director B'],
            ['3', 'Director A'],
        ]

        result = links_instance.top_directors(5)
        assert result == {'Director A': 2, 'Director B': 1}

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_directors_with_none_directors(self, mock_get_imdb, links_instance):
        """Тест со значением None для режиссера."""
        links_instance.data = [['1'], ['2'], ['3']]

        mock_get_imdb.return_value = [
            ['1', 'Director A'],
            ['2', None],
            ['3', 'Director A'],
        ]

        result = links_instance.top_directors(2)
        assert result == {'Director A': 2}

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_directors_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.top_directors(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Director'])


    @patch('movielens_analysis.Links.get_imdb')
    def test_top_directors_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching directors")

        with pytest.raises(Exception, match="Error fetching directors"):
            links_instance.top_directors(2)

#################################################################################
########################## most_expensive #######################################
#################################################################################
@pytest.fixture
def links_instance():
    """Фикстура для создания экземпляра Links."""
    return Links('data/ml-latest-small/links.csv')

class TestMostExpensive:
    @patch('movielens_analysis.Links.get_imdb')
    def test_most_expensive_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000'],
            ['2', '€50,000,000'],
            ['3', '$200,000,000'],
        ]

        result = links_instance.most_expensive(2)
        assert result == {'Grumpier Old Men': 200000000, 'Toy Story': 100000000}
        mock_get_imdb.assert_called_once_with(['1', '2', '3'], ['movieId', 'Budget'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_most_expensive_n_greater_than_num_movies(self, mock_get_imdb, links_instance):
        """Тест, когда n больше чем число фильмов."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000'],
            ['2', '€50,000,000'],
        ]
        result = links_instance.most_expensive(5)
        assert result == {'Toy Story': 100000000, 'Jumanji': 50000000}


    @patch('movielens_analysis.Links.get_imdb')
    def test_most_expensive_with_invalid_budget(self, mock_get_imdb, links_instance):
        """Тест с невалидным бюджетом."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000'],
            ['2', 'invalid budget'],
            ['3', '$200,000,000'],
        ]
        result = links_instance.most_expensive(2)
        assert result == {'Grumpier Old Men': 200000000, 'Toy Story': 100000000}


    @patch('movielens_analysis.Links.get_imdb')
    def test_most_expensive_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.most_expensive(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Budget'])


    @patch('movielens_analysis.Links.get_imdb')
    def test_most_expensive_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching movie data")

        with pytest.raises(Exception, match="Error fetching movie data"):
            links_instance.most_expensive(2)

#################################################################################
########################## most_profitable ######################################
#################################################################################
@pytest.fixture
def links_instance():
    """Фикстура для создания экземпляра Links."""
    return Links('data/ml-latest-small/links.csv')


class TestMostProfitable:
    @patch('movielens_analysis.Links.get_imdb')
    def test_most_profitable_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000', '$500,000,000'],
            ['2', '€50,000,000', '€200,000,000'],
            ['3', '$200,000,000', '$1,000,000,000'],
        ]

        result = links_instance.most_profitable(2)
        assert result == {'Grumpier Old Men': 800000000, 'Toy Story': 400000000}
        mock_get_imdb.assert_called_once_with(['1', '2', '3'], ['movieId', 'Budget', 'Gross worldwide'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_most_profitable_n_greater_than_num_movies(self, mock_get_imdb, links_instance):
        """Тест, когда n больше чем число фильмов."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000', '$500,000,000'],
            ['2', '€50,000,000', '€200,000,000'],
        ]
        result = links_instance.most_profitable(5)
        assert result == {'Toy Story': 400000000, 'Jumanji': 150000000}

    @patch('movielens_analysis.Links.get_imdb')
    def test_most_profitable_with_invalid_budget_gross(self, mock_get_imdb, links_instance):
        """Тест с невалидным бюджетом и валовым сбором."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '$100,000,000', '$500,000,000'],
            ['2', 'invalid budget', 'invalid gross'],
            ['3', '$200,000,000', '$1,000,000,000'],
        ]
        result = links_instance.most_profitable(2)
        assert result == {'Grumpier Old Men': 800000000, 'Toy Story': 400000000}

    @patch('movielens_analysis.Links.get_imdb')
    def test_most_profitable_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.most_profitable(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Budget', 'Gross worldwide'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_most_profitable_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching movie data")

        with pytest.raises(Exception, match="Error fetching movie data"):
            links_instance.most_profitable(2)

#################################################################################
############################## longest ##########################################
#################################################################################
@pytest.fixture
def links_instance():
    """Фикстура для создания экземпляра Links."""
    return Links('data/ml-latest-small/links.csv')


class TestLongest:
    @patch('movielens_analysis.Links.get_imdb')
    def test_longest_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes'],
            ['2', '90 minutes'],
            ['3', '150 minutes'],
        ]
        result = links_instance.longest(2)
        expected = {'Grumpier Old Men': '2 hours 30 minutes', 'Toy Story': '2 hours'}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)
        mock_get_imdb.assert_called_once_with(['1', '2', '3'], ['movieId', 'Runtime'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_longest_n_greater_than_num_movies(self, mock_get_imdb, links_instance):
        """Тест, когда n больше чем число фильмов."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes'],
            ['2', '90 minutes'],
        ]
        result = links_instance.longest(5)
        expected = {'Toy Story': '2 hours', 'Jumanji': '1 hour 30 minutes'}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_longest_with_invalid_runtime(self, mock_get_imdb, links_instance):
        """Тест с невалидным значением runtime."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes'],
            ['2', 'invalid runtime'],
            ['3', '150 minutes'],
        ]
        result = links_instance.longest(2)
        expected = {'Grumpier Old Men': '2 hours 30 minutes', 'Toy Story': '2 hours'}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_longest_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.longest(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Runtime'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_longest_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching movie data")

        with pytest.raises(Exception, match="Error fetching movie data"):
            links_instance.longest(2)

def sort_dict_by_value(d):
    """Сортирует словарь по значениям в убывающем порядке и возвращает список кортежей."""
    return sorted(d.items(), key=lambda item: item[1], reverse=True)

#################################################################################
########################## top_cost_per_minute ##################################
#################################################################################
@pytest.fixture
def links_instance():
    """Фикстура для создания экземпляра Links."""
    return Links('data/ml-latest-small/links.csv')

class TestTopCostPerMinute:
    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_per_minute_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', '90 minutes', '€90000000'],
            ['3', '150 minutes', '$150000000'],
        ]
        result = links_instance.top_cost_per_minute(2)
        expected = {'Toy Story': 1000000, 'Jumanji': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)
        mock_get_imdb.assert_called_once_with(['1', '2', '3'], ['movieId', 'Runtime', 'Budget'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_per_minute_n_greater_than_num_movies(self, mock_get_imdb, links_instance):
        """Тест, когда n больше, чем количество фильмов."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', '90 minutes', '€90000000'],
        ]
        result = links_instance.top_cost_per_minute(5)
        expected = {'Toy Story': 1000000, 'Jumanji': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_per_minute_with_invalid_runtime_budget(self, mock_get_imdb, links_instance):
        """Тест с невалидным временем выполнения и бюджетом."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', 'invalid runtime', 'invalid budget'],
            ['3', '150 minutes', '$150000000'],
        ]
        result = links_instance.top_cost_per_minute(2)
        expected = {'Toy Story': 1000000, 'Grumpier Old Men': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_per_minute_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.top_cost_per_minute(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Runtime', 'Budget'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_per_minute_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching movie data")

        with pytest.raises(Exception, match="Error fetching movie data"):
            links_instance.top_cost_per_minute(2)

def sort_dict_by_value(d):
    """Сортирует словарь по значениям в убывающем порядке и возвращает список кортежей."""
    return sorted(d.items(), key=lambda item: item[1], reverse=True)

#################################################################################
########################## top_cost_profit_minute ##################################
#################################################################################
@pytest.fixture
def links_instance():
    """Фикстура для создания экземпляра Links."""
    return Links('data/ml-latest-small/links.csv')

class TestTopCostPerMinute:
    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_profit_minute_valid_input(self, mock_get_imdb, links_instance):
        """Тест на валидные входные данные."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', '90 minutes', '€90000000'],
            ['3', '150 minutes', '$15000000'],
        ]
        result = links_instance.top_cost_profit_minute(2)
        expected = {'Toy Story': 1000000, 'Jumanji': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)
        mock_get_imdb.assert_called_once_with(['1', '2', '3'], ['movieId', 'Runtime', 'Gross worldwide'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_profit_minute_n_greater_than_num_movies(self, mock_get_imdb, links_instance):
        """Тест, когда n больше, чем количество фильмов."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', '90 minutes', '€90000000'],
        ]
        result = links_instance.top_cost_profit_minute(5)
        expected = {'Toy Story': 1000000, 'Jumanji': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_profit_minute_with_invalid_runtime_budget(self, mock_get_imdb, links_instance):
        """Тест с невалидным временем выполнения и бюджетом."""
        links_instance.data = [['1'], ['2'], ['3']]
        mock_get_imdb.return_value = [
            ['1', '120 minutes', '$120000000'],
            ['2', 'invalid runtime', 'invalid budget'],
            ['3', '150 minutes', '$150000000'],
        ]
        result = links_instance.top_cost_profit_minute(2)
        expected = {'Toy Story': 1000000, 'Grumpier Old Men': 1000000}
        assert sort_dict_by_value(result) == sort_dict_by_value(expected)

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_profit_minute_empty_data(self, mock_get_imdb, links_instance):
        """Тест на пустые данные."""
        links_instance.data = []
        mock_get_imdb.return_value = []
        result = links_instance.top_cost_profit_minute(5)
        assert result == {}
        mock_get_imdb.assert_called_once_with([], ['movieId', 'Runtime', 'Gross worldwide'])

    @patch('movielens_analysis.Links.get_imdb')
    def test_top_cost_profit_minute_get_imdb_exception(self, mock_get_imdb, links_instance):
        """Тест на исключение в get_imdb."""
        links_instance.data = [['1'], ['2']]
        mock_get_imdb.side_effect = Exception("Error fetching movie data")

        with pytest.raises(Exception, match="Error fetching movie data"):
            links_instance.top_cost_profit_minute(2)

def sort_dict_by_value(d):
    """Сортирует словарь по значениям в убывающем порядке и возвращает список кортежей."""
    return sorted(d.items(), key=lambda item: item[1], reverse=True)


@pytest.fixture
def analyzer():
    path_to_test_file = "data/tags_test.csv"
    analyzer = Tags(path_to_test_file)
    analyzer._load_data()
    return analyzer

@pytest.fixture
def movies():
    path_to_test_file = "data/movies_test.csv"
    movies = Movies(path_to_test_file)
    print(movies.df_movies)
    return movies

@pytest.fixture
def ratings():
    path_to_ratings = "data/ratings_test.csv"
    path_to_movies = "data/movies_test.csv"
    ratings = Ratings(path_to_ratings, path_to_movies)
    return ratings

@pytest.fixture
def ratings_users():
    path_to_ratings = "data/ratings_test_users.csv"
    path_to_movies = "data/movies_test.csv"
    ratings = Ratings(path_to_ratings, path_to_movies)
    return ratings

# Тест 1: Проверка, что метод возвращает правильный топ-N тегов
@pytest.mark.tags
def test_most_words_top_n(analyzer):
    result = analyzer.most_words(2)
    expected = {
        "Highly quotable": 2,  # 2 слова
        "action packed": 2      # 2 слова
    }
    assert result == expected

# Тест 2: Проверка, что метод корректно обрабатывает случай, когда N больше количества уникальных тегов
@pytest.mark.tags
def test_most_words_n_larger_than_unique_tags(analyzer):
    result = analyzer.most_words(10)
    expected = {
        "Highly quotable": 2,  # 2 слова
        "action packed": 2,     # 2 слова
        "classic movies": 2,     # 2 слова
        "funny": 1              # 1 слово
    }
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает случай, когда N = 0
@pytest.mark.tags
def test_most_words_n_zero(analyzer):
    result = analyzer.most_words(0)
    expected = {}
    assert result == expected

# Тест 5: Проверка, что метод корректно обрабатывает случай, когда теги содержат только одно слово
@pytest.mark.tags
def test_most_words_single_word_tags(analyzer):
    # Добавляем теги с одним словом в тестовые данные
    analyzer.df_tags = pd.DataFrame({
        "userId": [1, 2, 3],
        "movieId": [101, 101, 101],
        "tag": ["funny", "action", "classic"],
        "timestamp": [1445714994, 1445714996, 1445714998]
    })
    result = analyzer.most_words(2)
    expected = {
        "funny": 1,  # 1 слово
        "action": 1   # 1 слово
    }
    assert result == expected

# Тест 6: Проверка, что метод корректно удаляет дубликаты тегов
@pytest.mark.tags
def test_most_words_drop_duplicates(analyzer):
    # Добавляем дубликаты тегов в тестовые данные
    analyzer.df_tags = pd.DataFrame({
        "userId": [1, 2, 3, 4],
        "movieId": [101, 101, 101, 101],
        "tag": ["funny", "funny", "action packed", "action packed"],
        "timestamp": [1445714994, 1445714996, 1445714998, 1445715000]
    })
    result = analyzer.most_words(2)
    expected = {
        "action packed": 2,  # 2 слова
        "funny": 1           # 1 слово
    }
    assert result == expected


    # Тест 7: Проверка, что метод возвращает правильный тип данных (dict)
@pytest.mark.tags
def test_most_words_return_type(analyzer):
    result = analyzer.most_words(2)
    assert isinstance(result, dict), "Метод должен возвращать словарь."

# Тест 8: Проверка, что ключи и значения в словаре имеют правильные типы данных
@pytest.mark.tags
def test_most_words_data_types(analyzer):
    result = analyzer.most_words(2)
    for tag, word_count in result.items():
        assert isinstance(tag, str), "Ключи словаря должны быть строками."
        assert isinstance(word_count, int), "Значения словаря должны быть целыми числами."

# Тест 9: Проверка, что данные отсортированы по количеству слов в порядке убывания
@pytest.mark.tags
def test_most_words_sorted_correctly(analyzer):
    result = analyzer.most_words(3)
    values = list(result.values())
    # Проверяем, что значения отсортированы по убыванию
    assert all(values[i] >= values[i + 1] for i in range(len(values) - 1)), "Данные должны быть отсортированы по убыванию."

    # Тест 1: Проверка, что метод возвращает правильный топ-N самых длинных тегов
@pytest.mark.tags
def test_longest_top_n(analyzer):
    result = analyzer.longest(2)
    expected = [
        "Highly quotable",
        "classic movies"
    ]
    assert result == expected

# Тест 2: Проверка, что метод корректно обрабатывает случай, когда N больше количества уникальных тегов
@pytest.mark.tags
def test_longest_n_larger_than_unique_tags(analyzer):
    result = analyzer.longest(10)
    expected = [
        "Highly quotable",          # 16 символов
        "classic movies",            # 13 символов
        "action packed",            # 12 символов
        "funny"                     # 5 символов
    ]
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает случай, когда N = 0
@pytest.mark.tags
def test_longest_n_zero(analyzer):
    result = analyzer.longest(0)
    expected = []
    assert result == expected

# Тест 5: Проверка, что метод корректно удаляет дубликаты тегов
@pytest.mark.tags
def test_longest_drop_duplicates(analyzer):
    # Добавляем дубликаты тегов в тестовые данные
    analyzer.df_tags = pd.DataFrame({
        "userId": [1, 2, 3, 4],
        "movieId": [101, 101, 101, 101],
        "tag": ["funny", "funny", "action packed", "action packed"],
        "timestamp": [1445714994, 1445714996, 1445714998, 1445715000]
    })
    result = analyzer.longest(2)
    expected = [
        "action packed",  # 12 символов
        "funny"           # 5 символов
    ]
    assert result == expected

# Тест 6: Проверка, что метод возвращает правильный тип данных (list)
@pytest.mark.tags
def test_longest_return_type(analyzer):
    result = analyzer.longest(2)
    assert isinstance(result, list), "Метод должен возвращать список."

# Тест 7: Проверка, что элементы списка имеют правильный тип данных (str)
@pytest.mark.tags
def test_longest_data_types(analyzer):
    result = analyzer.longest(2)
    for tag in result:
        assert isinstance(tag, str), "Элементы списка должны быть строками."

# Тест 8: Проверка, что данные отсортированы по длине тегов в порядке убывания
@pytest.mark.tags
def test_longest_sorted_correctly(analyzer):
    result = analyzer.longest(3)
    lengths = [len(tag) for tag in result]
    # Проверяем, что длины тегов отсортированы по убыванию
    assert all(lengths[i] >= lengths[i + 1] for i in range(len(lengths) - 1)), "Данные должны быть отсортированы по убыванию длины."

# Тест 1: Проверка, что метод возвращает правильное пересечение
@pytest.mark.tags
def test_most_words_and_longest_intersection(analyzer):
    result = analyzer.most_words_and_longest(2)
    expected = [
        "Highly quotable"  # Тег с наибольшим количеством слов и самый длинный
    ]
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает случай, когда N = 0
@pytest.mark.tags
def test_most_words_and_longest_n_zero(analyzer):
    result = analyzer.most_words_and_longest(0)
    expected = []
    assert result == expected

# Тест 5: Проверка, что метод возвращает правильный тип данных (list)
@pytest.mark.tags
def test_most_words_and_longest_return_type(analyzer):
    result = analyzer.most_words_and_longest(2)
    assert isinstance(result, list), "Метод должен возвращать список."

# Тест 6: Проверка, что элементы списка имеют правильный тип данных (str)
@pytest.mark.tags
def test_most_words_and_longest_data_types(analyzer):
    result = analyzer.most_words_and_longest(2)
    for tag in result:
        assert isinstance(tag, str), "Элементы списка должны быть строками."

# Тест 1: Проверка, что метод возвращает правильный топ-N самых популярных тегов
@pytest.mark.tags
def test_most_popular_top_n(analyzer):
    result = analyzer.most_popular(2)
    expected = {
        "funny": 2,              # Тег "funny" упоминается 2 раза
        "Highly quotable": 2     # Тег "Highly quotable" упоминается 2 раза
    }
    assert result == expected

# Тест 2: Проверка, что метод корректно обрабатывает случай, когда N больше количества уникальных тегов
@pytest.mark.tags
def test_most_popular_n_larger_than_unique_tags(analyzer):
    result = analyzer.most_popular(10)
    expected = {
        "funny": 2,              # Тег "funny" упоминается 2 раза
        "Highly quotable": 2,    # Тег "Highly quotable" упоминается 2 раза
        "action packed": 1,      # Тег "action packed" упоминается 1 раз
        "classic movies": 1      # Тег "classic movies" упоминается 1 раз
    }
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает случай, когда N = 0
@pytest.mark.tags
def test_most_popular_n_zero(analyzer):
    result = analyzer.most_popular(0)
    expected = {}
    assert result == expected

# Тест 5: Проверка, что метод возвращает правильный тип данных (dict)
@pytest.mark.tags
def test_most_popular_return_type(analyzer):
    result = analyzer.most_popular(2)
    assert isinstance(result, dict), "Метод должен возвращать словарь."

# Тест 6: Проверка, что ключи и значения в словаре имеют правильные типы данных
@pytest.mark.tags
def test_most_popular_data_types(analyzer):
    result = analyzer.most_popular(2)
    for tag, count in result.items():
        assert isinstance(tag, str), "Ключи словаря должны быть строками."
        assert isinstance(count, int), "Значения словаря должны быть целыми числами."

# Тест 7: Проверка, что данные отсортированы по количеству упоминаний в порядке убывания
@pytest.mark.tags
def test_most_popular_sorted_correctly(analyzer):
    result = analyzer.most_popular(3)
    counts = list(result.values())
    # Проверяем, что значения отсортированы по убыванию
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1)), "Данные должны быть отсортированы по убыванию."

# Тест 1: Проверка, что метод возвращает все теги, содержащие заданное слово
@pytest.mark.tags
def test_tags_with_word(analyzer):
    result = analyzer.tags_with("funny")
    expected = [
        "funny"                  # Тег "funny"
    ]
    assert result == expected

# Тест 2: Проверка, что метод возвращает пустой список, если слово не найдено
@pytest.mark.tags
def test_tags_with_word_not_found(analyzer):
    result = analyzer.tags_with("nonexistent")
    expected = []
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает регистр букв
@pytest.mark.tags
def test_tags_with_case_insensitive(analyzer):
    result = analyzer.tags_with("FUNNY")
    expected = [
        "funny"
    ]
    assert result == expected

# Тест 4: Проверка, что метод корректно удаляет дубликаты тегов
@pytest.mark.tags
def test_tags_with_drop_duplicates(analyzer):
    # Добавляем дубликаты тегов в тестовые данные
    analyzer.df_tags = pd.DataFrame({
        "userId": [1, 2, 3, 4],
        "movieId": [101, 101, 101, 101],
        "tag": ["funny", "funny", "action packed", "action packed"],
        "timestamp": [1445714994, 1445714996, 1445714998, 1445715000]
    })
    result = analyzer.tags_with("funny")
    expected = ["funny"]  # Ожидаем только один уникальный тег
    assert result == expected

# Тест 5: Проверка, что метод возвращает правильный тип данных (list)
@pytest.mark.tags
def test_tags_with_return_type(analyzer):
    result = analyzer.tags_with("funny")
    assert isinstance(result, list), "Метод должен возвращать список."

# Тест 6: Проверка, что элементы списка имеют правильный тип данных (str)
@pytest.mark.tags
def test_tags_with_data_types(analyzer):
    result = analyzer.tags_with("funny")
    for tag in result:
        assert isinstance(tag, str), "Элементы списка должны быть строками."

# Тест 7: Проверка, что данные отсортированы по алфавиту
@pytest.mark.tags
def test_tags_with_sorted_correctly(analyzer):
    result = analyzer.tags_with("funny")
    # Проверяем, что теги отсортированы по алфавиту
    assert result == sorted(result), "Данные должны быть отсортированы по алфавиту."

# Тест 1: Проверка, что метод возвращает правильное распределение по годам
@pytest.mark.movies
def test_dist_by_release(movies):
    result = movies.dist_by_release()
    expected = OrderedDict([
        (1995, 8)  # В 1995 году выпущено 8 фильмов
    ])
    assert result == expected

# Тест 2: Проверка, что метод корректно обрабатывает случай, когда год выпуска отсутствует
@pytest.mark.movies
def test_dist_by_release_missing_year(movies):
    # Добавляем фильм без года выпуска в тестовые данные
    movies.df_movies = pd.DataFrame({
        "movieId": [1, 2, 3],
        "title": ["Toy Story (1995)", "Jumanji (1995)", "No Year Movie"],
        "genres": ["Adventure|Animation", "Adventure|Children", "Comedy"]
    })
    result = movies.dist_by_release()
    expected = OrderedDict([
        (1995, 2)  # В 1995 году выпущено 2 фильма
    ])
    assert result == expected

# Тест 4: Проверка, что метод возвращает правильный тип данных (OrderedDict)
@pytest.mark.movies
def test_dist_by_release_return_type(movies):
    result = movies.dist_by_release()
    assert isinstance(result, OrderedDict), "Метод должен возвращать OrderedDict."

# Тест 5: Проверка, что данные отсортированы по количеству фильмов в порядке убывания
@pytest.mark.movies
def test_dist_by_release_sorted_correctly(movies):
    result = movies.dist_by_release()
    counts = list(result.values())
    # Проверяем, что значения отсортированы по убыванию
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1)), "Данные должны быть отсортированы по убыванию."


# Тест 1: Проверка, что метод возвращает правильное распределение по жанрам
@pytest.mark.movies
def test_dist_by_genres(movies):
    result = movies.dist_by_genres()
    expected = {
        "Comedy": 5,
        "Adventure": 3,
        "Romance": 3,
        "Children": 3,
        "Fantasy": 2,
        "Animation": 1,
        "Drama": 1,
        "Action": 1,
        "Crime": 1,
        "Thriller": 1
    }
    assert result == expected

# Тест 3: Проверка, что метод возвращает правильный тип данных (dict)
@pytest.mark.movies
def test_dist_by_genres_return_type(movies):
    result = movies.dist_by_genres()
    assert isinstance(result, dict), "Метод должен возвращать словарь."

# Тест 4: Проверка, что ключи и значения в словаре имеют правильные типы данных
@pytest.mark.movies
def test_dist_by_genres_data_types(movies):
    result = movies.dist_by_genres()
    for genre, count in result.items():
        assert isinstance(genre, str), "Ключи словаря должны быть строками."
        assert isinstance(count, int), "Значения словаря должны быть целыми числами."

# Тест 5: Проверка, что данные отсортированы по количеству фильмов в порядке убывания
@pytest.mark.movies
def test_dist_by_genres_sorted_correctly(movies):
    result = movies.dist_by_genres()
    counts = list(result.values())
    # Проверяем, что значения отсортированы по убыванию
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1)), "Данные должны быть отсортированы по убыванию."

# Тест 1: Проверка, что метод возвращает правильный топ-N фильмов
@pytest.mark.movies
def test_most_genres_top_n(movies):
    result = movies.most_genres(3)
    expected = {
        "Toy Story (1995)": 5,  # 5 жанров
        "Jumanji (1995)": 3,    # 3 жанра
        "Waiting to Exhale (1995)": 3  # 3 жанра
    }
    assert result == expected

# Тест 2: Проверка, что метод корректно обрабатывает случай, когда N больше количества фильмов
@pytest.mark.movies
def test_most_genres_n_larger_than_movies(movies):
    result = movies.most_genres(10)
    expected = {
        "Toy Story (1995)": 5,
        "Jumanji (1995)": 3,
        "Waiting to Exhale (1995)": 3,
        "Grumpier Old Men (1995)": 2,
        "Sabrina (1995)": 2,
        "Tom and Huck (1995)": 2,
        "Father of the Bride Part II (1995)": 1,
        "Heat (1995)": 3
    }
    assert result == expected

# Тест 3: Проверка, что метод корректно обрабатывает случай, когда N = 0
@pytest.mark.movies
def test_most_genres_n_zero(movies):
    result = movies.most_genres(0)
    expected = {}
    assert result == expected

# Тест 5: Проверка, что метод возвращает правильный тип данных (dict)
@pytest.mark.movies
def test_most_genres_return_type(movies):
    result = movies.most_genres(3)
    assert isinstance(result, dict), "Метод должен возвращать словарь."

# Тест 6: Проверка, что ключи и значения в словаре имеют правильные типы данных
@pytest.mark.movies
def test_most_genres_data_types(movies):
    result = movies.most_genres(3)
    for title, count in result.items():
        assert isinstance(title, str), "Ключи словаря должны быть строками."
        assert isinstance(count, int), "Значения словаря должны быть целыми числами."

# Тест 7: Проверка, что данные отсортированы по количеству жанров в порядке убывания
@pytest.mark.movies
def test_most_genres_sorted_correctly(movies):
    result = movies.most_genres(3)
    counts = list(result.values())
    # Проверяем, что значения отсортированы по убыванию
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1)), "Данные должны быть отсортированы по убыванию."


# Тест 1: Проверка, что метод возвращает правильное распределение по годам
@pytest.mark.ratings
def test_dist_by_year(ratings):
    result = ratings.movies.dist_by_year()
    expected = OrderedDict([
        (2000, 8)  # В 2000 году было 8 рейтингов
    ])
    assert result == expected

# Тест 3: Проверка, что метод возвращает правильный тип данных (OrderedDict)
@pytest.mark.ratings
def test_dist_by_year_return_type(ratings):
    result = ratings.movies.dist_by_year()
    assert isinstance(result, OrderedDict), "Метод должен возвращать OrderedDict."

# Тест 4: Проверка, что данные отсортированы по годам в порядке возрастания
@pytest.mark.ratings
def test_dist_by_year_sorted_correctly(ratings):
    result = ratings.movies.dist_by_year()
    years = list(result.keys())
    # Проверяем, что годы отсортированы по возрастанию
    assert all(years[i] <= years[i + 1] for i in range(len(years) - 1)), "Данные должны быть отсортированы по возрастанию."

@pytest.mark.ratings
def test_dist_by_rating(ratings):
    # Ожидаемое распределение рейтингов
    expected_distribution = OrderedDict([
        (3.0, 1),  # Рейтинг 3.0 встречается 1 раз
        (4.0, 4),  # Рейтинг 4.0 встречается 4 раза
        (5.0, 3)   # Рейтинг 5.0 встречается 3 раза
    ])

    # Получаем фактическое распределение рейтингов
    actual_distribution = ratings.movies.dist_by_rating()

    # Проверяем, что распределение совпадает с ожидаемым
    assert actual_distribution == expected_distribution, \
        f"Ожидалось: {expected_distribution}, получено: {actual_distribution}"
    
# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_dist_by_rating_return_type(ratings):
    result = ratings.movies.dist_by_rating()
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_dist_by_rating_element_types(ratings):
    result = ratings.movies.dist_by_rating()
    for key, value in result.items():
        assert isinstance(key, float), \
            f"Ключи должны быть float, получен ключ типа: {type(key)}"
        assert isinstance(value, int), \
            f"Значения должны быть int, получено значение типа: {type(value)}"

# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_dist_by_rating_sorted_correctly(ratings):
    result = ratings.movies.dist_by_rating()
    sorted_keys = sorted(result.keys())  # Сортируем ключи в порядке возрастания
    assert list(result.keys()) == sorted_keys, \
        "Ключи в OrderedDict должны быть отсортированы по возрастанию"
    
# Тест для метода top_by_num_of_ratings
@pytest.mark.ratings
def test_top_by_num_of_ratings(ratings):
    # Ожидаемый результат для топ-3 фильмов
    expected_top_movies = OrderedDict([
        ('Grumpier Old Men (1995)', 1),
        ('Heat (1995)', 1),
        ('Toy Story (1995)', 1)
    ])

    # Получаем фактический результат
    actual_top_movies = ratings.movies.top_by_num_of_ratings(3)

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_top_movies == expected_top_movies, \
        f"Ожидалось: {expected_top_movies}, получено: {actual_top_movies}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_top_by_num_of_ratings_return_type(ratings):
    result = ratings.movies.top_by_num_of_ratings(3)
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_top_by_num_of_ratings_element_types(ratings):
    result = ratings.movies.top_by_num_of_ratings(3)
    for key, value in result.items():
        assert isinstance(key, str), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, int), \
            f"Значения должны быть int, получено значение типа: {type(value)}"

# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_top_by_num_of_ratings_sorted_correctly(ratings):
    result = ratings.movies.top_by_num_of_ratings(3)
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"
    
# Тест для метода top_by_ratings (средний рейтинг)
@pytest.mark.ratings
def test_top_by_ratings_average(ratings):
    # Ожидаемый результат для топ-3 фильмов по среднему рейтингу
    expected_top_movies = OrderedDict([
        ('Toy Story (1995)', 4.0),
        ('Grumpier Old Men (1995)', 4.0),
        ('Heat (1995)', 4.0)
    ])

    # Получаем фактический результат
    actual_top_movies = ratings.movies.top_by_ratings(3, metric="average")

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_top_movies == expected_top_movies, \
        f"Ожидалось: {expected_top_movies}, получено: {actual_top_movies}"

# Тест для метода top_by_ratings (медианный рейтинг)
@pytest.mark.ratings
def test_top_by_ratings_median(ratings):
    # Ожидаемый результат для топ-3 фильмов по медианному рейтингу
    expected_top_movies = OrderedDict([
        ('Toy Story (1995)', 4.0),
        ('Grumpier Old Men (1995)', 4.0),
        ('Heat (1995)', 4.0)
    ])

    # Получаем фактический результат
    actual_top_movies = ratings.movies.top_by_ratings(3, metric="median")

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_top_movies == expected_top_movies, \
        f"Ожидалось: {expected_top_movies}, получено: {actual_top_movies}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_top_by_ratings_return_type(ratings):
    result = ratings.movies.top_by_ratings(3, metric="average")
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_top_by_ratings_element_types(ratings):
    result = ratings.movies.top_by_ratings(3, metric="average")
    for key, value in result.items():
        assert isinstance(key, str), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"

# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_top_by_ratings_sorted_correctly(ratings):
    result = ratings.movies.top_by_ratings(3, metric="average")
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"
    
# Тест для метода top_controversial
@pytest.mark.ratings
def test_top_controversial():
    path_to_ratings = "data/ratings_test2.csv"
    path_to_movies = "data/movies_test.csv"
    ratings = Ratings(path_to_ratings, path_to_movies)
    # Ожидаемый результат для топ-3 самых противоречивых фильмов
    expected_top_movies = OrderedDict([
        ('Heat (1995)', 2.0),
        ('Grumpier Old Men (1995)', 0.5),
        ('Toy Story (1995)', 0.5)
    ])

    # Получаем фактический результат
    actual_top_movies = ratings.movies.top_controversial(3)

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_top_movies == expected_top_movies, \
        f"Ожидалось: {expected_top_movies}, получено: {actual_top_movies}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_top_controversial_return_type(ratings):
    result = ratings.movies.top_controversial(3)
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_top_controversial_element_types(ratings):
    result = ratings.movies.top_controversial(3)
    for key, value in result.items():
        assert isinstance(key, str), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"

# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_top_controversial_sorted_correctly(ratings):
    result = ratings.movies.top_controversial(3)
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"

@pytest.mark.ratings
def test_dist_by_num_ratings_users(ratings_users):
    result = ratings_users.users.dist_by_num_ratings()
    expected = OrderedDict([(377, 13), (490, 12), (1, 7)])
    assert result == expected, f"Ожидалось: {expected}, получено: {result}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_dist_by_num_ratings_users_return_type(ratings_users):
    result = ratings_users.users.dist_by_num_ratings()
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"
    
# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_dist_by_num_ratings_users_element_types(ratings_users):
    result = ratings_users.users.dist_by_num_ratings()
    for key, value in result.items():
        assert isinstance(key, int), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, int), \
            f"Значения должны быть float, получено значение типа: {type(value)}"
        
# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_dist_by_num_ratings_users_sorted_correctly(ratings_users):
    result = ratings_users.users.dist_by_num_ratings()
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"
        
@pytest.mark.ratings
def test_top_by_ratings_average_users(ratings_users):
    result = ratings_users.users.top_by_ratings(metric="average")
    expected = OrderedDict([(1, 4.29), (377, 3.81), (490, 2.67)])
    assert result == expected, f"Ожидалось: {expected}, получено: {result}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_top_by_ratings_average_users_return_type(ratings_users):
    result = ratings_users.users.top_by_ratings(metric="average")
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"
    
# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_top_by_ratings_average_users_element_types(ratings_users):
    result = ratings_users.users.top_by_ratings(metric="average")
    for key, value in result.items():
        assert isinstance(key, int), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"
        
# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_top_by_ratings_average_users_sorted_correctly(ratings_users):
    result = ratings_users.users.top_by_ratings(metric="average")
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"
    
@pytest.mark.ratings
def test_top_by_ratings_median_users(ratings_users):
    result = ratings_users.users.top_by_ratings(metric="median")
    expected = OrderedDict([(1, 4.0), (377, 4.0), (490, 2.75)])
    assert result == expected, f"Ожидалось: {expected}, получено: {result}"

@pytest.mark.ratings
def test_top_controversial_users(ratings_users):
    result = ratings_users.users.top_controversial(2)
    expected = OrderedDict([(490, 1.06), (1, 0.57)])
    assert result == expected, f"Ожидалось: {expected}, получено: {result}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings
def test_top_controversial_users_return_type(ratings_users):
    result = ratings_users.users.top_controversial(3)
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings
def test_top_controversial_users_element_types(ratings_users):
    result = ratings_users.users.top_controversial(3)
    for key, value in result.items():
        assert isinstance(key, int), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"
        
# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings
def test_top_controversial_users_sorted_correctly(ratings_users):
    result = ratings_users.users.top_controversial(3)
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"


@pytest.mark.movies_dop
def test_dist_by_genres_proportion(movies):
    expected_result = {'Comedy': 62.5, 
                       'Adventure': 37.5, 
                       'Children': 37.5, 
                       'Romance': 37.5, 
                       'Fantasy': 25.0, 
                       'Animation': 12.5, 
                       'Drama': 12.5, 
                       'Action': 12.5, 
                       'Crime': 12.5, 
                       'Thriller': 12.5}

    actual_result = movies.dist_by_genres_proportion()

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_result == expected_result, \
        f"Ожидалось: {expected_result}, получено: {actual_result}"
    
# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.movies_dop
def test_dist_by_genres_proportion_return_type(movies):
    result =  movies.dist_by_genres_proportion()
    assert isinstance(result, dict), \
        f"Метод должен возвращать Dict, получен: {type(result)}"
    
# Тест для проверки типов данных элементов
@pytest.mark.movies_dop
def test_dist_by_genres_proportion_element_types(movies):
    result =  movies.dist_by_genres_proportion()
    for key, value in result.items():
        assert isinstance(key, str), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"
        
# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.movies_dop
def test_dist_by_genres_proportion_sorted_correctly(movies):
    result =  movies.dist_by_genres_proportion()
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"
    
@pytest.mark.tags_dop
def test_shortest_n_greater_than_unique(analyzer):
    # В нашем уникальном наборе всего 4 тега
    expected_result = ["funny", "action packed", "classic movies", "Highly quotable"]
    actual_result = analyzer.shortest(10)

    # Проверяем, что возвращаются все уникальные теги
    assert actual_result == expected_result

@pytest.mark.tags_dop
def test_shortest_n_equals_one(analyzer):
    expected_result = ["funny"]
    actual_result = analyzer.shortest(1)

    # Проверяем, что возвращается самый короткий тег
    assert actual_result == expected_result

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.tags_dop
def test_shortest_return_type(analyzer):
    result =  analyzer.shortest(10)
    assert isinstance(result, list), \
        f"Метод должен возвращать Dict, получен: {type(result)}"
    
# Тест 7: Проверка, что элементы списка имеют правильный тип данных (str)
@pytest.mark.tags_dop
def test_shortest_data_types(analyzer):
    result = analyzer.shortest(2)
    for tag in result:
        assert isinstance(tag, str), "Элементы списка должны быть строками."

# Тест 8: Проверка, что данные отсортированы по длине тегов в порядке убывания
@pytest.mark.tags_dop
def test_shortest_sorted_correctly(analyzer):
    result = analyzer.shortest(3)
    lengths = [len(tag) for tag in result]
    # Проверяем, что длины тегов отсортированы по убыванию
    assert all(lengths[i] <= lengths[i + 1] for i in range(len(lengths) - 1)), "Данные должны быть отсортированы по возрастанию длины."

@pytest.mark.ratings_dop
def test_top_controversial_std_dev():
    path_to_ratings = "data/ratings_test2.csv"
    path_to_movies = "data/movies_test.csv"
    ratings = Ratings(path_to_ratings, path_to_movies)
    # Ожидаемый результат для топ-3 самых противоречивых фильмов
    expected_top_movies = OrderedDict([
        ('Heat (1995)', 1.41),
        ('Grumpier Old Men (1995)', 0.71),
        ('Toy Story (1995)', 0.71)
    ])

    # Получаем фактический результат
    actual_top_movies = ratings.movies.top_controversial_std_dev(3)

    # Проверяем, что результат совпадает с ожидаемым
    assert actual_top_movies == expected_top_movies, \
        f"Ожидалось: {expected_top_movies}, получено: {actual_top_movies}"

# Тест для проверки корректности типа данных, возвращаемого методом
@pytest.mark.ratings_dop
def test_top_controversial_std_dev_return_type(ratings):
    result = ratings.movies.top_controversial_std_dev(3)
    assert isinstance(result, OrderedDict), \
        f"Метод должен возвращать OrderedDict, получен: {type(result)}"

# Тест для проверки типов данных элементов в возвращаемом OrderedDict
@pytest.mark.ratings_dop
def test_top_controversial_std_dev_element_types(ratings):
    result = ratings.movies.top_controversial_std_dev(3)
    for key, value in result.items():
        assert isinstance(key, str), \
            f"Ключи должны быть str, получен ключ типа: {type(key)}"
        assert isinstance(value, float), \
            f"Значения должны быть float, получено значение типа: {type(value)}"

# Тест для проверки корректности сортировки возвращаемых данных
@pytest.mark.ratings_dop
def test_top_controversial_std_dev_sorted_correctly(ratings):
    result = ratings.movies.top_controversial_std_dev(3)
    sorted_values = sorted(result.values(), reverse=True)  # Сортируем значения по убыванию
    assert list(result.values()) == sorted_values, \
        "Значения в OrderedDict должны быть отсортированы по убыванию"