import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CallbackContext

def find_recipe(recipe_name):
    # URL, куда отправляем запрос
    url = "https://www.russianfood.com/search/content/"

    # Параметры для запроса (в данном случае - название рецепта)
    params = {"kw": recipe_name}

    try:
        # Отправляем POST-запрос
        response = requests.post(url, params=params)
        response.raise_for_status()  # Проверяем на ошибки при запросе

        # Парсим HTML-код страницы с помощью BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Находим первый элемент с классом rcp_wi_title
        first_result = soup.find("td", class_="rcp_wi_title")
        if first_result:
            # Находим ссылку на рецепт внутри первого элемента
            recipe_link = first_result.find("a")["href"]
            
            # Формируем полный URL-адрес рецепта
            full_recipe_url = f"https://www.russianfood.com{recipe_link}"
            
            # Возвращаем URL-адрес рецепта
            return full_recipe_url
        else:
            print("Рецепт не найден")
            return None

    except requests.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

# Команда для поиска рецепта
def search_recipe(update: Update, context: CallbackContext) -> None:
    recipe_name = ' '.join(context.args)
    found_recipes = find_recipe(recipe_name)
    print(found_recipes)
