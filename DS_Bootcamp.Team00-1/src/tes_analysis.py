from bs4 import BeautifulSoup
import re
from collections import Counter
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from collections import defaultdict
import re



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
        
    # async def fetch_batch(session, urls, headers):
    #     for url in urls:
    #         try:
    #             async with session.get(url, headers=headers) as response:
    #                 response.raise_for_status()
    #                 yield await response.text()  # Возвращаем HTML по одному
    #         except aiohttp.ClientError as e:
    #             print(f"Error fetching {url}: {e}")
    #             yield None
    #         except asyncio.TimeoutError:
    #             print(f"Timeout fetching {url}")
    #             yield None
    @staticmethod
    async def fetch(session, url, headers, semaphore):
        async with semaphore:  # Ограничиваем количество одновременных запросов
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

    @staticmethod
    async def fetch_batch(session, urls, headers, semaphore):
        tasks = [Links.fetch(session, url, headers, semaphore) for url in urls]
        return await asyncio.gather(*tasks)  # Выполняем запросы параллельно

    async def main(urls, headers, move_id):
        # batch_size = 50
        # htmls = []
        # info = []
        # # semaphore = asyncio.Semaphore(50)

        # async with aiohttp.ClientSession() as session:
        #     for i in range(0, len(urls), batch_size):
        #         batch_urls = urls[i:i + batch_size]
        #         async for html in Links.fetch_batch(session, batch_urls, headers):
        #             htmls.append(html)
        #             print(html)
        #             data = Links.parse_imdb(htmls, ['movieId', 'Director', 'Budget','Gross worldwide', 'Runtime'], move_id)
        #             info.append(data)
        #             # print(info)
        #             htmls = []
        #             print(f"Processed batch {i//batch_size + 1}, sleeping for 5 seconds...")
        #             await asyncio.sleep(5)
        batch_size = 50
        semaphore = asyncio.Semaphore(10)  # Ограничиваем количество одновременных запросов
        info = []

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_move_id = move_id[i:i + batch_size]

                # Выполняем запросы для текущего пакета
                htmls = await Links.fetch_batch(session, batch_urls, headers, semaphore)

                # Парсим HTML-страницы
                batch_info = Links.parse_imdb(htmls, ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime'], batch_move_id)
                info.extend(batch_info)
                # print(info)

                print(f"Processed batch {i//batch_size + 1}, sleeping for 5 seconds...")
                await asyncio.sleep(5)  # Пауза между пакетами

        
        return info

    def async_get(urls, headers, move_id):
        return asyncio.run(Links.main(urls, headers, move_id))
    
    def get_info(self, data):
        movid = []
        for line in data:
            movid.append(line[0])
        info = self.get_imdb(movid, ['movieId', 'Director', 'Budget', 'Gross worldwide', 'Runtime'])
        # print(info[0])
        return info

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
        res = Links.async_get(urls, headers, move_id)
        # imdb_info = Links.parse_imdb(res, list_of_fields, move_id)
        # imdb_info.sort(key= lambda x: x[0], reverse=True)
        return res
        
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
        profit = []
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
            profit.append((worldwide, budget))
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
            if runtime == 0:
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
            if runtime == 0:
                prof = 0
            else:
                prof = worldwide // runtime
            profit_minute.append((title, prof))
        profit_minute.sort(key= lambda x: x[1], reverse=True)
        # top_10 = profit_minute[:n]
        profit = dict(profit_minute)

        return profit

if __name__ == '__main__':
    links = Links("data/ml-latest-small/links.csv")
    links.write_data(links.info)

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
