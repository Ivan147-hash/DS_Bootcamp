from bs4 import BeautifulSoup
import re
from collections import Counter
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from collections import defaultdict, OrderedDict
import datetime
import re
import csv



class Links:
    """
    Analyzing data from links.csv
    """
    # Вынести список id фильмов в конструктор
    def __init__(self, path_to_the_file):
        self.filename = path_to_the_file
        self.data = self.read_links_id()
        self.title = self.read_title_id()
        self.info = self.get_info(self.data)
    
    def read_links_id(self):
        try:
            with open(self.filename, 'r') as inf:
                next(inf)
                lines = inf.readlines()
                result = []
                for lin in lines:
                    result.append(lin.strip().split(','))
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"File {'links.csv'} not found.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        
    def read_title_id(self):
        try:
            with open("data/ml-latest-small/movies.csv", 'r') as inf:
                next(inf)
                lines = inf.readlines()
                result = []
                for lin in lines:
                    moveid = lin.strip().split(',')[0]
                    title = lin.strip().split(',')[1]
                    result.append([moveid, title[:-7]])
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"File {'links.csv'} not found.")
        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        
    def write_res(self, filename, data):
        with open(filename, 'w') as ouf:
            for key, value in data.items():
                ouf.write(f"{key}: {value}\n") 

    def write_data(self, data):
        with open('data_analys.csv', 'w') as ouf:
            for item in data:
                ouf.write(str(item) + "\n")

        
    def moveid_to_title(self, movid):
        titles = self.title
        title = ''
        for line in titles:
            if int(line[0]) == int(movid):
                title = line[1]
                break
        return title
        
    async def fetch(session, url, headers):
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Error fetching {url}: {e}")
            return None
        except asyncio.TimeoutError:
            print(f"Timeout fetching {url}")
            return None

    async def main(urls, headers):
        batch_size = 50
        htmls = []

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                tasks = [Links.fetch(session, url, headers) for url in batch_urls]
                batch_htmls = await asyncio.gather(*tasks)
                htmls.extend(batch_htmls)

                print(f"Processed batch {i//batch_size + 1}, sleeping for 5 seconds...")
                await asyncio.sleep(5)  # Используем asyncio.sleep для асинхронной задержки

        return htmls

    def get_info(self, data):
        movid = []
        for line in data:
            movid.append(line[0])
        info = self.get_imdb(movid, ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime'])
        # print(info[0])
        return info

    def async_get(urls, headers):
        return asyncio.run(Links.main(urls, headers))

    def parse_imdb(lists, value, move_info):
            result = []
            i = 0
            for lis in lists:
                if lis is None:
                    print(f"Skipping None HTML at index {i}")
                    i += 1
                    continue
                soup = BeautifulSoup(lis, 'html.parser')
                elements_class1 = soup.find_all(class_="ipc-metadata-list__item")
                elements_class2 = soup.find_all(class_="sc-ec65ba05-1 fUCCIx")
                line = list(set(elements_class1 + elements_class2))
                info = [x for x in range(len(value))]
                for item in line:
                    if item:
                        for x in range(1, len(value)):
                            if value[x] in item.text:
                                info[x] = item.text.split(value[x])[1]
                info[0] = int(move_info[i])
                i += 1
                result.append(info)
            return result
    
    def time_str_to_min(self, time_str):
        hours = re.search(r'(\d+)\s+hour', time_str)
        minutes = re.search(r'(\d+)\s+minute', time_str)
        total_min = 0
        if hours:
            total_min += int(hours.group(1)) * 60
        if minutes:
            total_min += int(minutes.group(1))
        return total_min
    
    def time_min_to_str(self, time):
        if time < 0:
            return "Invalid time"
        hours, minutes = divmod(time, 60)
        hours_str = f"{hours} hour{'s' if hours != 1 else ''}" if hours > 0 else ""
        minutes_str = f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else ""

        return f"{hours_str} {minutes_str}".strip()
    
    def str_to_num(self, str):
        try:
            num_str = re.sub(r'[^\d\.]', '', str)
            if '.' in num_str:
                number = float(num_str)
            else:
                number = int(num_str)
        except ValueError:
            print(f"Не удалось преобразовать строку '{str}' в число.")
            return int(0)
        return number

    # @staticmethod
    def get_imdb(self, list_of_movies, list_of_fields):
        """
    The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
     Sort it by movieId descendingly.
        """
        if list_of_movies == [] or list_of_fields == []:
            raise ValueError("Empty list. Provide movie ids and fields.")
        imdb_info = []
        lines = self.data
        urls = []
        move_id = []
        # i = 0
        for line in lines:
            # if i > 50:
            #     break
            if line[0] in list_of_movies:
                urls.append(f'https://www.imdb.com/title/tt{line[1]}/')
                move_id.append(line[0])
            # i += 1
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        res = Links.async_get(urls, headers)
        imdb_info = Links.parse_imdb(res, list_of_fields, move_id)
        imdb_info.sort(key= lambda x: x[0], reverse=True)
        return imdb_info
        
    def top_directors(self, n):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """

        dir_info = self.info
    
        director_list = [item[1] for item in dir_info if item[1] is not None]
        directors_count = Counter(director_list)
        directors = dict(directors_count)
        return directors
        
    def most_expensive(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        """

        # dir_info = self.get_imdb(list_of_movies, ['movieId', 'Runtime'])
        # ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime']

        dir_info = self.info
        expensive_most = []
        for item in dir_info:
            title = self.moveid_to_title(item[0])
            budget = item[2]
            try:
                if isinstance(item[2], str):
                    budget = re.sub(r'[$,€£]', '', item[2]).strip()
                    budget = int(budget.split()[0])
            except (ValueError, IndexError):
                budget = self.str_to_num(item[2])
                continue
            expensive_most.append((title, budget))
        expensive_most.sort(key= lambda x: x[1], reverse=True)
        # top_n = expensive_most[:n]
        budgets = dict(expensive_most)

        return budgets
        
    def most_profitable(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
     Sort it by the difference descendingly.
        """

        # ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime']
        dir_info = self.info
        profitable = []
        for item in dir_info:
            title = self.moveid_to_title(item[0])
            worldwide = item[3]
            budget = item[2]
            if isinstance(item[2], str):
                try:
                    budget = re.sub(r'[$,€£]', '', item[2]).strip()
                    budget = int(budget.split()[0])
                except (ValueError, IndexError):
                    budget = self.str_to_num(item[2])
            if isinstance(item[3], str):
                try:
                    worldwide = re.sub(r'[$,€£]', '', item[3]).strip()
                    worldwide = int(item[3].split()[0])
                except (ValueError, IndexError):
                    worldwide = self.str_to_num(item[3])
            profit = worldwide - budget
            profitable.append((title, profit))
        profitable.sort(key= lambda x: x[1], reverse=True)
        # top_n = profitable[:n]
        profits = dict(profitable)

        return profits
        
    def longest(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
     Sort it by runtime descendingly.
        """

        # ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime']
        dir_info = self.info
        long = []
        for item in dir_info:
            title = self.moveid_to_title(item[0])
            runtime = item[4]
            try:
                if isinstance(item[4], str):
                        runtime = self.time_str_to_min(item[4])
            except (ValueError, IndexError):
                print(f"Skipping invalid gross value: {item[4]}")
                continue
            long.append((title, runtime))
        long.sort(key= lambda x: x[1], reverse=True)
        # top_n = long[:n]
        runtimes = {}
        for movie, duration_minutes in long:
            runtimes[movie] = self.time_min_to_str(duration_minutes)

        return runtimes
        
    def top_cost_per_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. 
     The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """

        dir_info = self.info
        per_minute = []
        for item in dir_info:
            title = self.moveid_to_title(item[0])
            if isinstance(item[4], str):
                try:
                    runtime = self.time_str_to_min(item[4])
                except (ValueError, IndexError):
                    runtime = self.str_to_num(item[4])
            if isinstance(item[2], str):
                try:
                    budget = re.sub(r'[$,€£]', '', item[2]).strip()
                    budget = int(budget.split()[0])
                except (ValueError, IndexError):
                    budget = self.str_to_num(item[2])
            if item[4] == 0:
                per = 0
            else:
                per = budget // runtime
            per_minute.append((title, per))
        per_minute.sort(key= lambda x: x[1], reverse=True)
        # top_10 = per_minute[:n]
        costs = dict(per_minute)

        return costs
    
    def top_cost_profit_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. 
     The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """

        # ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime']
        dir_info = self.info
        profit_minute = []
        for item in dir_info:
            title = self.moveid_to_title(item[0])
            worldwide = item[3]
            if isinstance(item[4], str):
                try:
                    runtime = self.time_str_to_min(item[4])
                except (ValueError, IndexError):
                    runtime = self.str_to_num(item[4])
            if isinstance(item[3], str):
                try:
                    worldwide = re.sub(r'[$,€£]', '', item[3]).strip()
                    worldwide = int(worldwide.split()[0])
                except (ValueError, IndexError):
                    worldwide = self.str_to_num(item[3])
            if item[4] == 0:
                prof = 0
            else:
                prof = worldwide // runtime
            profit_minute.append((title, prof))
        profit_minute.sort(key= lambda x: x[1], reverse=True)
        # top_10 = profit_minute[:n]
        profit = dict(profit_minute)

        return profit



class Ratings:
    """
    Analyzing data from ratings.csv
    """
    def __init__(self, path_to_the_file, path_to_movies):
        """
        Put here any fields that you think you will need.
        """
        self.path_to_ratings = path_to_the_file
        self.path_to_movies = path_to_movies
        self.df_ratings = self._load_ratings()
        self.movies = self.Movies(self, self.path_to_movies)
        self.users = self.Users(self) 


    def _load_ratings(self):
        """
        Загружает данные о рейтингах.
        """
        try:
            df = pd.read_csv(self.path_to_ratings)
            return df
        except Exception as e:
            print(f"Ошибка при загрузке данных о рейтингах: {e}")
            return None


    class Movies:    

        def __init__(self, ratings_instance, path_to_movies):
            self.ratings = ratings_instance
            self.path_to_movies = path_to_movies
            self.df_movies = self._load_movies()

        def _load_movies(self):
            """
            Загружает данные о фильмах.
            """
            try:
                df = pd.read_csv(self.path_to_movies)
                return df
            except Exception as e:
                print(f"Ошибка при загрузке данных о фильмах: {e}")
                return None

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.
            """

            self.ratings.df_ratings["year"] = self.ratings.df_ratings["timestamp"].apply(
            lambda x: datetime.datetime.fromtimestamp(x).year)
            year_counts = self.ratings.df_ratings["year"].value_counts().sort_index()
            ratings_by_year = OrderedDict(year_counts.items())

            return ratings_by_year
        
        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
         Sort it by ratings ascendingly.
            """

            rating_counts = self.ratings.df_ratings["rating"].value_counts().sort_index()
            ratings_distribution = OrderedDict(rating_counts.items())

            return ratings_distribution
        
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
     Sort it by numbers descendingly.
            """

            movie_ratings_count = self.ratings.df_ratings.groupby("movieId").size().reset_index(name="num_ratings")
            top_movies_df = pd.merge(movie_ratings_count, self.df_movies, on="movieId")
            top_movies_df = top_movies_df.sort_values(by=["num_ratings", "title"], ascending=[False, True])
            top_n_movies = top_movies_df.head(n)
            top_movies = OrderedDict(zip(top_n_movies["title"], top_n_movies["num_ratings"]))

            return top_movies
        
        def top_by_ratings(self, n, metric="average"):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """

            if metric == "average":
                movie_ratings = self.ratings.df_ratings.groupby("movieId")["rating"].mean().reset_index(name="metric")
            elif metric == "median":
                movie_ratings = self.ratings.df_ratings.groupby("movieId")["rating"].median().reset_index(name="metric")
            else:
                raise ValueError("Метрика должна быть 'average' или 'median'")
            
            top_movies_df = pd.merge(movie_ratings, self.df_movies, on="movieId")
            top_movies_df = top_movies_df.sort_values(by="metric", ascending=False)
            top_movies_df["metric"] = top_movies_df["metric"].round(2)
            top_n_movies = top_movies_df.head(n)
            top_movies = OrderedDict(zip(top_n_movies["title"], top_n_movies["metric"]))

            return top_movies
        
        def top_controversial(self, n):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
          Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """

            movie_variances = self.ratings.df_ratings.groupby("movieId")["rating"].var().reset_index(name="variance")
            top_movies_df = pd.merge(movie_variances, self.df_movies, on="movieId")
            top_movies_df = top_movies_df.sort_values(by=["variance", "title"], ascending=[False, True])
            top_movies_df["variance"] = top_movies_df["variance"].round(2)
            top_n_movies = top_movies_df.head(n)
            top_movies = OrderedDict(zip(top_n_movies["title"], top_n_movies["variance"]))

            return top_movies

        def top_controversial_std_dev(self, n):
            """
            The method returns top-n movies by the standard deviation of the ratings.
            It is a dict where the keys are movie titles and the values are standard deviations.
            Sort it by standard deviation descendingly.
            The values should be rounded to 2 decimals.
            """
            movie_std_devs = self.ratings.df_ratings.groupby("movieId")["rating"].std().reset_index(name="std_dev")
            top_movies_df = pd.merge(movie_std_devs, self.df_movies, on="movieId")
            top_movies_df = top_movies_df.sort_values(by=["std_dev", "title"], ascending=[False, True])
            top_movies_df["std_dev"] = top_movies_df["std_dev"].round(2)
            top_n_movies = top_movies_df.head(n)
            top_movies = OrderedDict(zip(top_n_movies["title"], top_n_movies["std_dev"]))

            return top_movies

    class Users(Movies):
        """
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
     Inherit from the class Movies. Several methods are similar to the methods from it.
        """        
        def __init__(self, ratings_instance):
            # Наследуемся от Movies, но не загружаем данные о фильмах
            super().__init__(ratings_instance, ratings_instance.path_to_movies)
            self.ratings = ratings_instance

        def dist_by_num_ratings(self):
            """
            The method returns the distribution of users by the number of ratings made by them.
            It is a dict where the keys are user IDs and the values are counts.
            Sort it by counts descendingly.
            """
            user_ratings_count = self.ratings.df_ratings.groupby("userId").size().reset_index(name="num_ratings")
            user_ratings_count = user_ratings_count.sort_values(by="num_ratings", ascending=False)
            user_distribution = OrderedDict(zip(user_ratings_count["userId"], user_ratings_count["num_ratings"]))
            return user_distribution

        def top_by_ratings(self, metric="average"):
            """
            The method returns the distribution of users by average or median ratings made by them.
            It is a dict where the keys are user IDs and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            # Используем метод top_by_ratings из класса Movies, адаптировав его для пользователей
            if metric == "average":
                user_ratings = self.ratings.df_ratings.groupby("userId")["rating"].mean().reset_index(name="metric")
            elif metric == "median":
                user_ratings = self.ratings.df_ratings.groupby("userId")["rating"].median().reset_index(name="metric")
            else:
                raise ValueError("Метрика должна быть 'average' или 'median'")

            user_ratings = user_ratings.sort_values(by="metric", ascending=False)
            user_ratings["metric"] = user_ratings["metric"].round(2)
            user_distribution = OrderedDict(zip(user_ratings["userId"], user_ratings["metric"]))
            return user_distribution

        def top_controversial(self, n):
            """
            The method returns top-n users with the biggest variance of their ratings.
            It is a dict where the keys are user IDs and the values are variances.
            Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """
            # Используем метод top_controversial из класса Movies, адаптировав его для пользователей
            user_variances = self.ratings.df_ratings.groupby("userId")["rating"].var().reset_index(name="variance")
            user_variances = user_variances.sort_values(by="variance", ascending=False)
            user_variances["variance"] = user_variances["variance"].round(2)
            top_n_users = user_variances.head(n)
            top_users = OrderedDict(zip(top_n_users["userId"], top_n_users["variance"]))
            return top_users


class Movies:
    """
    Analyzing data from movies.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """    
        self.path_to_the_file = path_to_the_file
        self.df_movies = self._load_data()

    def _load_data(self):
        """
        Загружает данные из CSV-файла и сохраняет их в self.df_movies.
        """
        try:
            df = pd.read_csv(self.path_to_the_file)
            return df
            
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return None

    def _extract_year(self, title):
        """
        Извлекает год выпуска из названия фильма.
        Предполагается, что год указан в конце названия в скобках, например, "Toy Story (1995)".
        """
        match = re.search(r"\((\d{4})\)", title)
        if match:
            return int(match.group(1))
        return None

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        self.df_movies["year"] = self.df_movies["title"].apply(self._extract_year)
        df_filtered = self.df_movies.dropna(subset=["year"])
        year_counts = df_filtered["year"].value_counts().sort_values(ascending=False)
        release_years = OrderedDict(year_counts.items())

        return release_years
    
    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
     Sort it by counts descendingly.
        """

        genre_counts = defaultdict(int)
        for genres in self.df_movies["genres"]:
            for genre in genres.split("|"):
                genre_counts[genre] += 1
        genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))

        return genres

    def dist_by_genres_proportion(self):

        genre_counts = self.dist_by_genres()
        total_movies = len(self.df_movies)
        genre_proportions = {genre: round((count / total_movies)*100, 2) for genre, count in genre_counts.items()}
        sorted_genre_proportions = dict(sorted(genre_proportions.items(), key=lambda x: x[1], reverse=True))

        return sorted_genre_proportions
        
    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """

        self.df_movies["genre_count"] = self.df_movies["genres"].apply(lambda x: len(x.split("|")))
        df_sorted = self.df_movies.sort_values(by="genre_count", ascending=False)
        top_n_movies = df_sorted.head(n)
        movies = dict(zip(top_n_movies["title"], top_n_movies["genre_count"]))

        return movies


class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.path_to_the_file = path_to_the_file
        self.df_tags = self._load_data()

    def _load_data(self):
        """
        Загружает данные из CSV-файла и сохраняет их в self.df_tags.
        """
        try:
            df = pd.read_csv(self.path_to_the_file)
            return df
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return None

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict 
 where the keys are tags and the values are the number of words inside the tag.
 Drop the duplicates. Sort it by numbers descendingly.
        """
        self.df_tags["word_count"] = self.df_tags["tag"].str.split().str.len()
        df_unique_tags = self.df_tags.drop_duplicates(subset=["tag"], keep="first")
        df_sorted_tags = df_unique_tags.sort_values(by="word_count", ascending=False)
        top_n_tags = df_sorted_tags.head(n)[["tag", "word_count"]]
        big_tags = dict(zip(top_n_tags["tag"], top_n_tags["word_count"]))

        return big_tags

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """

        df_unique_tags = self.df_tags.drop_duplicates(subset=["tag"], keep="first").copy()
        df_unique_tags["tag_length"] = df_unique_tags["tag"].str.len()
        df_sorted_tags = df_unique_tags.sort_values(by="tag_length", ascending=False)
        big_tags = df_sorted_tags.head(n)["tag"].tolist()

        return big_tags

    def shortest(self, n):

        df_unique_tags = self.df_tags.drop_duplicates(subset=["tag"], keep="first").copy()
        df_unique_tags["tag_length"] = df_unique_tags["tag"].str.len()
        df_sorted_tags = df_unique_tags.sort_values(by="tag_length", ascending=True)
        short_tags = df_sorted_tags.head(n)["tag"].tolist()

        return short_tags
        
    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """

        df_unique_tags = self.df_tags.drop_duplicates(subset=["tag"], keep="first").copy()
        df_unique_tags["word_count"] = df_unique_tags["tag"].str.split().str.len()
        df_sorted_by_words = df_unique_tags.sort_values(by="word_count", ascending=False)
        top_n_words = df_sorted_by_words.head(n)["tag"].tolist()
        df_unique_tags["tag_length"] = df_unique_tags["tag"].str.len()
        df_sorted_by_length = df_unique_tags.sort_values(by="tag_length", ascending=False)
        top_n_length = df_sorted_by_length.head(n)["tag"].tolist()
        big_tags = list(set(top_n_words).intersection(set(top_n_length)))

        return big_tags
        
    def most_popular(self, n):
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """

        tag_counts = self.df_tags["tag"].value_counts()
        top_n_tags = tag_counts.head(n)
        popular_tags = top_n_tags.to_dict()
        return popular_tags
        
    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """

        filtered_tags = self.df_tags[self.df_tags["tag"].str.contains(word, case=False, na=False)]
        unique_tags = filtered_tags["tag"].drop_duplicates()
        tags_with_word = unique_tags.sort_values().tolist()

        return tags_with_word


if __name__ == '__main__':
    links = Links("data/ml-latest-small/links.csv")
    # links.write_data(links.info)

    top_10_dir = links.top_directors(10)
    print('Топ-10 режисеров:')
    # for dir in top_10_dir:
    #     print(dir, 'снял фильмов:', top_10_dir[dir])
    print(type(top_10_dir))
    links.write_res('top_dir.csv', top_10_dir)

    top_10_bud = links.most_expensive(10)
    print('Топ-10 фильмов по сумме бюджета:')
    # for film in top_10_bud:
    #     print('Бюджет фильма', film, 'составляет:', top_10_bud[film])
    # print()
    links.write_res('top_bud.csv', top_10_bud)


    top_10_prok = links.most_profitable(10)
    print('Топ-10 фильмов по прибыли от проката:')
    # for profit in top_10_prok:
    #     print('Фильм', profit, 'получил в прокате:', top_10_prok[profit])
    # print()
    links.write_res('top_prok.csv', top_10_prok)

    top_10_lon = links.longest(10)
    print('Топ-10 фильмов по продолжительности сеанса:')
    # for film in top_10_lon:
    #     print('Продолжительность фильма', film, 'составляет:', top_10_lon[film])
    # print()
    links.write_res('top_lon.csv', top_10_lon)

    top_10_lper = links.top_cost_per_minute(10)
    print('Топ-10 фильмов по потраченным в минуту деньгам:')
    # for dir in top_10_lper:
    #     print('На сьемку фильма', dir, 'потратили:', top_10_lper[dir], '$/min')
    # print()
    links.write_res('top_lper.csv', top_10_lper)

    res = links.top_cost_profit_minute(10)
    print('Топ-10 фильмов по прибыли за каждую минуту:')
    # for dir in res:
    #     print('Фильм', dir, 'принес:', res[dir], '$ за каждую снятую минуту')
    links.write_res('top_res.csv', res)
