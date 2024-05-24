from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from recipes import recipes
import requests
from bs4 import BeautifulSoup

update_global = None
context_global = None

import json

def save_recipes(recipes):
    with open("recipes.txt", "w", encoding="utf-8") as file:
        json.dump(recipes, file, ensure_ascii=False, indent=4)

# Функция для загрузки словаря рецептов из файла JSON
def load_recipes():
    try:
        with open("recipes.txt", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

recipes = load_recipes()

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я кулинарный бот.\n'
        '/saverecipe - выбранные рецепты.\n'
        '/userecipe - просмотреть рецепты.\n'
        '/shoppinglist - продукты, которые нужны для блюд.\n'
        '/createrecipe "название рецепта" - создать новый рецепт.\n'
        '/addingredient "название рецепта" "игредиент" - добавить ингредиент к рецепту.\n'
        '/addinstructions "название рецепта" "инструкция" - добавить инструкции к рецепту.\n'
        '/deleterecipe "название рецепта" - удалить рецепт.\n'
        '/deleteingredient "название рецепта" - удалить ингредиент из рецепта.\n'
        '/deleteinstruction "название рецепта" "номер инструкции" - удалить инструкции из рецепта.\n'
        '/searchrecipe - поиск рецептов\n'
        '/searchbyingredients "Название ингредиента" - поиск рецептов с заданным ингредиентом \n'
    )

async def userecipe(update: Update, context: CallbackContext) -> None:
    global update_global, context_global
    update_global = update
    context_global = context

    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"userecipe_{name}")] for name in recipes.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите рецепт:', reply_markup=reply_markup)

async def saverecipe(update: Update, context: CallbackContext) -> None:
    global update_global, context_global
    update_global = update
    context_global = context
    if 'saved_recipes' not in context.user_data or not context.user_data['saved_recipes']:
        await update.message.reply_text('У вас нет сохраненных рецептов.')
        return

    saved_recipes = context.user_data['saved_recipes']
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"saverecipe_{name}")] for name in saved_recipes
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите рецепт для просмотра:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action.startswith("back_"):
        global update_global, context_global
        recipe_name = action.split("_")[1]
        if recipe_name == "userecipe":
            await userecipe(update_global, context_global)
            return
        if recipe_name == "saverecipe":
            await saverecipe(update_global, context_global)
            return

    if action.startswith("delete_"):
        # Пользователь выбрал рецепт из списка сохраненных рецептов для удаления
        saved_recipes = context.user_data.get('saved_recipes', [])
        recipe_name = action.split("_")[1]
        if recipe_name in saved_recipes:
            saved_recipes.remove(recipe_name)
            context.user_data['saved_recipes'] = saved_recipes
            await query.edit_message_text(text="Рецепт удален из сохраненных")
        else:
            await query.edit_message_text(text="Этот рецепт не был сохранен")
        return

    if action.startswith("add_"):
        # Пользователь выбрал кнопку "Добавить"
        recipe_name = action.split("_")[1]  # Получаем название рецепта
        if 'saved_recipes' not in context.user_data:
            context.user_data['saved_recipes'] = []
        if recipe_name not in context.user_data['saved_recipes']:
            context.user_data['saved_recipes'].append(recipe_name)
            await query.edit_message_text(text="Рецепт добавлен в сохраненные")
        else:
            await query.edit_message_text(text="Этот рецепт уже был добавлен в сохраненные")
        return
    
    if action.startswith("userecipe_"):
        recipe_name = action.split("_")[1]
        recipe = recipes[recipe_name]
        text = f"Рецепт: {recipe_name}:\n\nИнгредиенты:\n" + "\n".join([f"{ingredient}: {amount}" for ingredient, amount in recipe['ingredients'].items()]) + f"\n\nИнструкции:\n" + "\n".join(recipe['instructions'].split('_'))
        keyboard = [
        [InlineKeyboardButton("Добавить", callback_data=f"add_{recipe_name}"), InlineKeyboardButton("Назад", callback_data="back_userecipe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        context.user_data['selected_recipe'] = recipe_name

    if action.startswith("saverecipe_"):
        recipe_name = action.split("_")[1]
        recipe = recipes[recipe_name]
        text = f"Рецепт: {recipe_name}:\n\nИнгредиенты:\n" + "\n".join([f"{ingredient}: {amount}" for ingredient, amount in recipe['ingredients'].items()]) + f"\n\nИнструкции:\n" + "\n".join(recipe['instructions'].split('_'))
        keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=f"delete_{recipe_name}"), InlineKeyboardButton("Назад", callback_data="back_saverecipe")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
        context.user_data['selected_recipe'] = recipe_name

async def shopping_list(update: Update, context: CallbackContext) -> None:
    # Проверяем, есть ли сохраненные рецепты
    if 'saved_recipes' not in context.user_data or not context.user_data['saved_recipes']:
        await update.message.reply_text('У вас нет сохраненных рецептов. Сначала добавьте рецепт с помощью /userecipe')
        return

    # Создаем словарь для хранения ингредиентов
    shopping_dict = {}

    # Формируем список покупок для всех сохраненных рецептов
    for recipe_name in context.user_data['saved_recipes']:
        ingredients = recipes.get(recipe_name, {}).get("ingredients", {})
        if ingredients:
            for ingredient, amount in ingredients.items():
                # Проверяем, есть ли такой ингредиент уже в списке
                if ingredient in shopping_dict:
                    # Если ингредиент уже есть в списке, пытаемся сложить его количество
                    value_ingredient = amount.split(" ")
                    late_ingredient = shopping_dict[ingredient].split(" ")
                    stringnew = ""
                    b = True
                    for i in range(1,len(late_ingredient),2):
                        if (value_ingredient[1] == late_ingredient[i]):
                            newcount = int(value_ingredient[0]) + int(late_ingredient[i-1])
                            stringnew += str(newcount) + " " + late_ingredient[i] + " "
                            b = False
                        else:
                            stringnew += late_ingredient[i-1] + " " + late_ingredient[i] + " "
                    if b:
                        stringnew += value_ingredient[0] + " " + value_ingredient[1] + " "

                    del shopping_dict[ingredient]
                    shopping_dict[ingredient] = stringnew
                else:
                    # Если ингредиент еще не встречался, добавляем его в словарь
                    shopping_dict[ingredient] = amount

    # Форматируем список покупок для вывода
    shopping_list_text = "Список покупок для сохраненных рецептов:\n\n"
    for ingredient, amount in shopping_dict.items():
        shopping_list_text += f"- {ingredient}: {amount}\n"

    # Отправляем список покупок пользователю
    await update.message.reply_text(shopping_list_text)

async def createrecipe(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return

    # Проверяем, есть ли аргументы после команды
    if len(context.args) == 0:
        await update.message.reply_text("Вы не указали название рецепта.")
        return

    # Получаем название рецепта из аргументов команды
    recipe_name = ' '.join(context.args)

    # Проверяем, существует ли уже рецепт с таким названием
    if recipe_name in recipes:
        await update.message.reply_text("Рецепт с таким названием уже существует.")
        return

    # Добавляем новый рецепт в словарь рецептов
    recipes[recipe_name] = {"ingredients": {}, "instructions": ""}
    context.user_data['current_recipe'] = recipe_name

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    await update.message.reply_text(f"Рецепт '{recipe_name}' успешно создан. Теперь вы можете добавить ингредиенты с помощью команды /addingredient.")

async def addingredient(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return

    # Проверяем, указано ли название рецепта
    if len(context.args) < 2:
        await update.message.reply_text("Укажите название рецепта и ингредиенты для добавления.")
        return

    # Получаем название рецепта из аргументов
    recipe_name = context.args[0]
    ingredients = ' '.join(context.args[1:])

    # Проверяем, существует ли рецепт
    if recipe_name not in recipes:
        await update.message.reply_text("Указанный рецепт не найден.")
        return

    # Разделяем ингредиенты по запятой
    ingredient_list = ingredients.split(',')

    # Добавляем ингредиенты в рецепт
    for ingredient in ingredient_list:
        parts = ingredient.strip().split(' ')  # Разделяем название и количество ингредиента по пробелу
        if len(parts) < 2:
            await update.message.reply_text("Неверный формат ингредиента.")
            return
        name = ' '.join(parts[1:])
        amount = parts[0]
        recipes[recipe_name]["ingredients"][amount] = name

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    await update.message.reply_text("Ингредиенты успешно добавлены к рецепту.")

async def addinstructions(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return

    # Проверяем, указано ли название рецепта и инструкции
    if len(context.args) < 2:
        await update.message.reply_text("Укажите название рецепта и инструкции для добавления.")
        return

    # Получаем название рецепта из аргументов
    recipe_name = context.args[0]
    instructions = " ".join(context.args[1:])

    # Проверяем, существует ли рецепт
    if recipe_name not in recipes:
        await update.message.reply_text("Указанный рецепт не найден.")
        return

    # Получаем текущие инструкции и разбиваем их на пункты
    current_instructions = recipes[recipe_name]['instructions'].split('_')

    # Получаем номер последнего пункта инструкций
    last_step_number = len(current_instructions)

    # Формируем новые пункты инструкций, начиная с номера следующего после последнего
    new_instructions = [f"{last_step_number + i}) {step}" for i, step in enumerate(instructions.split('_'), start=1)]

    # Добавляем новые пункты инструкций к существующим
    recipes[recipe_name]['instructions'] += '_' + '_'.join(new_instructions)

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    await update.message.reply_text(f'Инструкции успешно добавлены к рецепту "{recipe_name}".')

async def deleteingredient(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return
    # Проверяем, указано ли название рецепта и ингредиент
    if len(context.args) < 2:
        await update.message.reply_text("Укажите название рецепта и ингредиент для удаления.")
        return

    # Получаем строку аргументов
    args_string = ' '.join(context.args)

    # Инициализируем список для хранения всех возможных комбинаций
    combinations = []

    # Перебираем длину строки аргументов
    for i in range(1, len(args_string)):
        # Разделяем строку на части с помощью разделителя на i-й позиции
        recipe_part = args_string[:i].strip()
        ingredient_part = args_string[i:].strip()

        # Проверяем, является ли текущая комбинация допустимой
        if recipe_part in recipes and ingredient_part in recipes[recipe_part]['ingredients']:
            combinations.append((recipe_part, ingredient_part))

    # Проверяем, были ли найдены допустимые комбинации
    if not combinations:
        await update.message.reply_text("Указанный рецепт или ингредиент не найдены.")
        return

    # Удаляем указанные ингредиенты из рецептов
    for recipe_name, ingredient_name in combinations:
        del recipes[recipe_name]['ingredients'][ingredient_name]

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    # Формируем ответное сообщение
    response = "\n".join([f'Ингредиент "{ingredient_name}" успешно удален из рецепта "{recipe_name}".' for recipe_name, ingredient_name in combinations])
    await update.message.reply_text(response)

async def deleteinstruction(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return

    # Проверяем, указано ли название рецепта и номер инструкции
    if len(context.args) < 2:
        await update.message.reply_text("Укажите название рецепта и номер инструкции для удаления.")
        return

    # Получаем название рецепта из аргументов
    recipe_name = ' '.join(context.args[:-1])  # Объединяем все слова, кроме последнего, в название рецепта
    instruction_number = int(context.args[-1])  # Последнее слово - это номер инструкции

    # Проверяем, существует ли рецепт
    if recipe_name not in recipes:
        await update.message.reply_text("Указанный рецепт не найден.")
        return

    # Получаем текущие инструкции и разбиваем их на пункты
    current_instructions = recipes[recipe_name]['instructions'].split('_')

    # Проверяем, существует ли указанный номер инструкции в рецепте
    if instruction_number < 1 or instruction_number > len(current_instructions):
        await update.message.reply_text("Указанный номер инструкции некорректен.")
        return

    # Удаляем указанную инструкцию из рецепта
    deleted_instruction = current_instructions.pop(instruction_number - 1)

    # Обновляем номера оставшихся инструкций
    for i in range(instruction_number - 1, len(current_instructions)):
        parts = current_instructions[i].split(') ')
        parts[0] = str(i + 1)
        current_instructions[i] = ') '.join(parts)

    # Обновляем инструкции в рецепте
    recipes[recipe_name]['instructions'] = '_'.join(current_instructions)

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    await update.message.reply_text(f'Инструкция "{deleted_instruction}" успешно удалена из рецепта "{recipe_name}".')

async def deleterecipe(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if not user:
        await update.message.reply_text("Извините, не могу получить информацию о вас.")
        return
    # Проверяем, указано ли название рецепта
    if len(context.args) == 0:
        await update.message.reply_text("Укажите название рецепта для удаления.")
        return

    # Получаем название рецепта из аргументов
    recipe_name = ' '.join(context.args)

    # Проверяем, существует ли рецепт
    if recipe_name not in recipes:
        await update.message.reply_text("Указанный рецепт не найден.")
        return

    # Удаляем рецепт
    del recipes[recipe_name]

    # Сохраняем обновленные рецепты
    save_recipes(recipes)

    await update.message.reply_text(f'Рецепт "{recipe_name}" успешно удален.')

async def search_by_ingredients(update: Update, context: CallbackContext) -> None:
    # Получаем список ингредиентов из сообщения пользователя
    ingredients_query = context.args
    
    if not ingredients_query:
        await update.message.reply_text("Пожалуйста, укажите хотя бы один ингредиент для поиска.")
        return
    
    # Приводим ингредиенты к нижнему регистру для удобства сравнения
    ingredients_query = [ingredient.lower() for ingredient in ingredients_query]
    
    # Инициализируем список найденных рецептов
    found_recipes = []
    
    # Перебираем все рецепты и ищем совпадения по ингредиентам
    for recipe_name, recipe in recipes.items():
        recipe_ingredients = [ingredient.lower() for ingredient in recipe['ingredients']]
        if all(ingredient in recipe_ingredients for ingredient in ingredients_query):
            found_recipes.append(recipe_name)
    
    if not found_recipes:
        await update.message.reply_text("По вашему запросу ничего не найдено.")
        return
    
    # Формируем сообщение с найденными рецептами
    reply_text = "Найденные рецепты:\n\n"
    for recipe_name in found_recipes:
        reply_text += f"- {recipe_name}\n"
    
    await update.message.reply_text(reply_text)

async def search_recipe(update: Update, context: CallbackContext) -> None:
    # Получаем параметры поиска из сообщения пользователя
    search_params = context.args
    
    if not search_params:
        await update.message.reply_text("Пожалуйста, укажите параметры для поиска рецепта.")
        return
    
    # Инициализируем список найденных рецептов
    found_recipes = []
    
    # Перебираем все рецепты и проверяем их на соответствие параметрам поиска
    for recipe_name, recipe in recipes.items():
        # Преобразуем название рецепта и ингредиенты в нижний регистр для удобства сравнения
        lowercase_recipe_name = recipe_name.lower()
        lowercase_ingredients = [ingredient.lower() for ingredient in recipe['ingredients']]
        
        # Проверяем каждый параметр поиска на соответствие с названием рецепта или ингредиентами
        for param in search_params:
            # Проверяем соответствие по названию рецепта
            if param.lower() in lowercase_recipe_name:
                found_recipes.append((recipe_name, recipe))
                break
            # Проверяем соответствие по ингредиентам
            for ingredient in lowercase_ingredients:
                if param.lower() in ingredient:
                    found_recipes.append((recipe_name, recipe))
                    break
            # Здесь можно добавить дополнительные параметры поиска, например, по категории и т. д.
            # Для каждого нового параметра поиска следует добавить новый внутренний цикл
            
    if not found_recipes:
        await update.message.reply_text("По вашему запросу ничего не найдено.")
        return
    
    # Формируем сообщение с найденными рецептами
    reply_text = "Найденные рецепты:\n\n"
    for recipe_name, recipe in found_recipes:
        reply_text += f"Рецепт: {recipe_name}:\n\nИнгредиенты:\n" + "\n".join([f"{ingredient}: {amount}" for ingredient, amount in recipe['ingredients'].items()]) + f"\n\nИнструкции:\n" + "\n".join(recipe['instructions'].split('_')) + "\n\n"
    
    await update.message.reply_text(reply_text)

