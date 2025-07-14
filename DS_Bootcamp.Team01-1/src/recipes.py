import pandas as pd
import numpy as np
import requests
import requests
from bs4 import BeautifulSoup
import re
import random
import joblib

class Rating:
    def __init__(self):
        self.data = self._read_recipes()
        self.model = joblib.load('model/choosed_model.pkl')
        self.ingridients = self._read_ingridients()

    def _read_recipes(self):
        data = pd.read_csv('data/extended_table.csv')
        return data
    
    def _read_ingridients(self):
        df = pd.read_csv('data/selected_columns_ingredients.csv')
        ingridients = df['Name'].tolist()
        return ingridients
    
    def predict(self, ingridients):
        X = np.zeros(len(self.ingridients))
        for product in ingridients:
            try:
                idx = self.ingridients.index(product)
                X[idx] = 1
            except:
                pass
        X = pd.DataFrame(X.reshape(1, -1), columns=self.ingridients)
        pred = self.model.predict(X)
        return pred[0]

    
    def print_rating_ingridients(self, ingridients):
        print("I. OUR FORECAST")
        pred = self.predict(ingridients)
        if pred == 0:
            message = """You might find it tasty, but in our opinion, it is a bad idea to have a dish with that list of ingredients."""
        elif pred == 1:
            message = """It is not good, but you can eat this if you really want. But you can to find something else."""
        elif pred == 2:
            message = """This is really good choice. We can help you to cook something delicious"""
        print(message)

class Ingredient:
    """Представляет ингредиенты с питательными веществами."""

    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key
        self.nutrition = self._fetch_nutrition()  # Словарь с питательными веществами (может быть пустым)
        self.ingridients = self._read_ingridients()

    def _read_ingridients(self):
        df = pd.read_csv('data/selected_columns_ingredients.csv')
        ingridients = df['Name'].tolist()
        return ingridients

    def _fetch_nutrition(self):
        nutrients = []
        food_component = pd.read_csv('data/created/Food Component.csv')
        for ingridient in self.name:
            url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingridient}&api_key={self.api_key}"

            try:
                response = requests.get(url)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                nutrients.append(self.creation_nutrition_dict(data, food_component, ingridient))
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {self.name}: {e}")
                nutrients.append({})
            except (KeyError, TypeError) as e:
                print(f"Error parsing data for {self.name}: {e}")
                nutrients.append({})
        return nutrients
        
    def creation_nutrition_dict(self, data, food_component, ingridient):
        nutrients = food_component['Nutrient'].tolist()
        if data["foods"]:
                food_nutrients = data["foods"][0]["foodNutrients"]
                nutrition_dict = {}
                nutrition_dict['name'] = ingridient
                for item in food_nutrients:
                    nutrient_name = item['nutrientName'].split(",")[0]
                    nutrient_value = item['value']
                    
                    if nutrient_name in nutrients:
                        adult_value = int(food_component.loc[food_component["Nutrient"] == nutrient_name, "Adults"].item())
                        if adult_value != 0 and nutrient_value != 0:
                            nutrition_dict[nutrient_name] = {'value': (nutrient_value * 100) / adult_value}
                return nutrition_dict
        else:
                print(f"No nutrition information found for {self.name}")
                return {}

    def print_nutrient_ingridient(self, recipe):
        nutrion_facts = self.nutrition
        for nutrient in nutrion_facts:
            colloms = recipe.find_ingridient_in_data(nutrient['name'])
            if not colloms:
                print(f'Ингридиента {nutrient["name"]} нет в списке рецептов')
                continue
            print(nutrient['name'])
            if nutrient:
                for i, (name, values) in enumerate(nutrient.items()):
                    if i == 0: continue
                    if values['value'] != 0.0:
                        print(f"  {name} - {values['value']:.1f}% of Daily Value")
            else:
                print("Информация о пищевой ценности отсутствует.")
            print()
        
class Recipe:
    """Представляет рецепт с его ингредиентами и рейтингом."""

    def __init__(self):
        self.data = self._read_recipes()
        self.ingridients = self._read_ingridients()

    def _read_ingridients(self):
        df = pd.read_csv('data/selected_columns_ingredients.csv')
        ingridients = df['Name'].tolist()
        return ingridients

    def _read_recipes(self):
        data = pd.read_csv('data/extended_table.csv')
        return data
    
    def find_ingridients(self, ingredients):
        result_ingredients= []
        for ingredient in ingredients:
            try:
                colloms = self.find_ingridient_in_data(ingredient)
                if not colloms:
                    print(f"Ингридиента {ingredient} нет в списке рецептов.")
                result_ingredients.append(colloms)
            except Exception as e:
                print(f"Ингридиента {ingredient} нет в списке рецептов.")
        result_ingredients = [item for list in result_ingredients for item in list]
        return result_ingredients

    def find_similar_recipes(self, ingredients, max_itaration = 10):
        recipes = []
        result_ingredients = self.find_ingridients(ingredients)
        if len(result_ingredients) == 0:
            return None
        non_zero_all = self.data[(self.data[result_ingredients] != 0).all(axis=1)]
        non_zero_all = non_zero_all.sort_values('rating', ascending=False)
        i = -1
        while len(non_zero_all) < 3 and -(i) > max_itaration:
            non_zero = self.data[(self.data[result_ingredients[:i]] != 0).all(axis=1)]
            non_zero = non_zero.sort_values('rating', ascending=False)
            non_zero_all = pd.concat([non_zero_all, non_zero.head(3)], ignore_index=True)
            i += -1
        for _, row in non_zero_all.head(3).iterrows():
            recipes.append((row.title, row.rating))
        return recipes
    
    def find_link_recipes(self, recipes):
        query = recipes.strip().replace('"', '')
        url = f"https://www.epicurious.com/search?q={query.replace(' ', '%20')}&page=1&content=recipe"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = None

                for links in soup.find_all('a', class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ BaseLink-eNWuiM Link-ehXskl iUEiRd bjMGUM kxxKIa", href=True):
                    if links.text.strip() == query:
                        results = "https://www.epicurious.com" + links['href']
                        return results
            else:
                print(f"Ошибка: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
        return f'Ссылка на рецепт "{recipes}" не найдена'
    
    def find_ingridient_in_data(self, ingredient):
        colloms = []
        if ingredient in self.ingridients:
            colloms.append(ingredient)
        else:
            for col in self.ingridients:
                split_string = re.split(r'[ ]', col)
                if ingredient in split_string:
                    colloms.append(col)
                    break
        return colloms
    
    def print_recipe(self, ingredients):
        similar_recipes = self.find_similar_recipes(ingredients)
        if similar_recipes:
            for recipet in similar_recipes:
                print(f'- {recipet[0]}, rating: {recipet[1]:.2f}, URL:')
                print(self.find_link_recipes(recipet[0]))
        else:
            print("  Похожих рецептов не найдено.")

class Ration:
    def __init__(self):
        self.data = self._read_recipes('data/extended_table.csv')
        self.df_url = self._read_recipes('data/created/link_html.csv')
        self.breakfasts = self.data[self.data["breakfast"] == 1]["title"].values
        self.lunch = self.data[self.data["lunch"] == 1]["title"].values
        self.dinner = self.data[self.data["dinner"] == 1]["title"].values
        self.protein_daily_norm = 71
        self.sodium_daily_norm = 2300
        self.calories_daily_norm = 2000

    def _read_recipes(self, filename):
        data = pd.read_csv(filename)
        return data
    
    def generate_ration(self):
        yield random.choice(self.breakfasts), random.choice(self.lunch), random.choice(self.dinner)

    def nutrient_calculation(self, menu):
        df = self.data

        result = []

        protein_breakfasts = df[df["title"] == menu[0][0]]["protein"].values[0]
        protein_lunch = df[df["title"] == menu[0][1]]["protein"].values[0]
        protein_dinner = df[df["title"] == menu[0][2]]["protein"].values[0]
        protein = protein_breakfasts + protein_lunch + protein_dinner
        protein_daily = protein * 100 / self.protein_daily_norm
        result.append(protein_daily)

        sodium_breakfasts = df[df["title"] == menu[0][0]]["sodium"].values[0]
        sodium_lunch = df[df["title"] == menu[0][1]]["sodium"].values[0]
        sodium_dinner = df[df["title"] == menu[0][2]]["sodium"].values[0]
        sodium = sodium_breakfasts + sodium_lunch + sodium_dinner
        sodium_daily = sodium * 100 / self.sodium_daily_norm
        result.append(sodium_daily)

        calories_breakfasts = df[df["title"] == menu[0][0]]["calories"].values[0]
        calories_lunch = df[df["title"] == menu[0][1]]["calories"].values[0]
        calories_dinner = df[df["title"] == menu[0][2]]["calories"].values[0]
        calories = calories_breakfasts + calories_lunch + calories_dinner
        calories_daily = calories * 100 / self.calories_daily_norm
        result.append(calories_daily)


        fat_breakfasts = df[df["title"] == menu[0][0]]["fat"].values[0]
        fat_lunch = df[df["title"] == menu[0][1]]["fat"].values[0]
        fat_dinner = df[df["title"] == menu[0][2]]["fat"].values[0]
        fat = fat_breakfasts + fat_lunch + fat_dinner
        result.append(fat)

        return result

    def menu_planning(self):
        i = 0
        while (1):
            menu = list(self.generate_ration())
            daily_norm = self.nutrient_calculation(menu)
            if (
                (70 < daily_norm[0] < 120) and 
                (70 < daily_norm[1] < 120) and 
                (70 < daily_norm[2] < 120) and 
                (daily_norm[3] < 120)
            ):
                return menu[0]
            if i > 20_000: break
            i += 1

    def print_ingridient(self, ingridients, recipe):
        ingridients_in_recipe = ingridients.columns[ingridients.iloc[0] == 1].tolist()
        rating = self.data[self.data['title'] == recipe][['rating']].values
        print(f"{recipe} (rating: {rating[0][0]:.2f})")
        print("Ingredients:")
        for ingridient in ingridients_in_recipe:
            print(f'- {ingridient}')
        print("Nutrients:")
        calories = self.data[self.data["title"] == recipe]["calories"].values[0]
        calories = calories * 100 / self.calories_daily_norm
        print(f'- calories: {calories:.1f}%')

        protein = self.data[self.data["title"] == recipe]["protein"].values[0]
        protein = protein * 100 / self.protein_daily_norm
        print(f'- protein: {protein:.1f}%')

        fat = self.data[self.data["title"] == recipe]["fat"].values[0]
        print(f'- fat: {fat:.1f}%')

        sodium = self.data[self.data["title"] == recipe]["sodium"].values[0]
        sodium = sodium * 100 / self.sodium_daily_norm
        print(f'- sodium: {sodium:.1f}%')

    def print_url(self, recipe):
        url = self.df_url[self.df_url["recept"] == recipe][['url']].values
        print(f'URL: {url[0][0]}')

    def print_menu(self):
        menu = self.menu_planning()
        print("BREAKFAST")
        print("---------------------")
        recipe_row = self.data[self.data['title'] == menu[0]]
        ingridients = recipe_row.drop('breakfast', axis=1)
        self.print_ingridient(ingridients, menu[0])
        self.print_url(menu[0])

        print("LUNCH")
        print("---------------------")
        recipe_row = self.data[self.data['title'] == menu[1]]
        ingridients = recipe_row.drop('breakfast', axis=1)
        self.print_ingridient(ingridients, menu[1])
        self.print_url(menu[1])

        print("DINNER")
        print("---------------------")
        recipe_row = self.data[self.data['title'] == menu[2]]
        ingridients = recipe_row.drop('breakfast', axis=1)
        self.print_ingridient(ingridients, menu[2])
        self.print_url(menu[2])


# if __name__ == '__main__':
#     ration = Ration()
#     ration.print_menu()
