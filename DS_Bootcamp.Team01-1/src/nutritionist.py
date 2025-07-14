import recipes
import sys

def main():
    """Основная функция скрипта."""
    if len(sys.argv) < 2:
        print("Usage: ./nutritionist.py ingredient1, ingredient2, ...")
        sys.exit(1)

    ingredients = [ing.strip(',') for ing in sys.argv[1:]]  # Разделяем строку на список ингредиентов
    recipe = recipes.Recipe()
    # Укажите свой ключ API
    api_key = "IX5S46qsEClnweZbMl7lyUERsakslbcRT1dgoiTr"

    # # I. OUR FORECAST
    # rating = recipes.Rating()
    # rating.print_rating_ingridients(ingredients)

    # # II. NUTRITION FACTS
    # ingredient = recipes.Ingredient(ingredients, api_key)
    # print("\nII. NUTRITION FACTS")
    # ingredient.print_nutrient_ingridient(recipe)

    # III. TOP-3 SIMILAR RECIPES
    print("\nIII. TOP-3 SIMILAR RECIPES:")
    recipe.print_recipe(ingredients)
    print()

    # # RATION
    # ration = recipes.Ration()
    # ration.print_menu()


if __name__ == "__main__":
    main()