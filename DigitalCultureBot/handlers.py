import telebot
import json
import os
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types, TeleBot

from DigitalCultureBot.config import TOKEN

bot = telebot.TeleBot(TOKEN)

all_recipes_file_path = os.path.join(os.path.dirname(__file__), '..', 'txt_file', 'all_recipes.txt')
save_recipes_file_path = os.path.join(os.path.dirname(__file__), '..', 'txt_file', 'save_recipes.txt')

recipe_name = ""
all_ingredients = []
timewait = 1

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_'))
def back(call):

    callback_data = call.data
    
    #0 этаж
    if callback_data == 'back_to_welcome':
        start_command(call.message)

    #1 этаж
    elif callback_data == 'back_to_save_recipe':
        show_save_recipe(call)

    #2 этаж
    elif callback_data == 'back_to_show_one_of_save_recipe':
        show_one_of_save_recipe(call)


    #1 этаж
    elif callback_data == 'back_to_doing_recipe':
        doing_recipe(call)
    
    #2 этаж
    elif callback_data == 'back_to_all_recipe':
        show_all_recipe(call)

    #3 этаж
    elif callback_data == 'back_to_show_one_of_all_recipe':
        show_one_of_all_recipe(call)

    #4 этаж
    elif callback_data == 'back_to_edit_all_recipe':
        edit_all_recipe(call) 



#0 этаж
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        pass

    markup = types.InlineKeyboardMarkup(row_width=4)
    item_save_recipe = types.InlineKeyboardButton("Выбранные рецепты", callback_data='save_recipe')
    item_shope_list = types.InlineKeyboardButton("Список покупок", callback_data='shope_list')
    item_recipe = types.InlineKeyboardButton("Рецепты", callback_data='doing_recipe')
    item_time = types.InlineKeyboardButton("Настройка уведомлений", callback_data='time')

    markup.add(item_save_recipe)
    markup.add(item_shope_list)
    markup.add(item_recipe)
    markup.add(item_time)

    bot.send_message(message.chat.id, 'Выберете действие', reply_markup=markup)



#1 этаж
@bot.callback_query_handler(func=lambda call: call.data == 'save_recipe')
def show_save_recipe(call):

    global recipe_name
    recipe_name = ""

    bot.delete_message(call.message.chat.id, call.message.message_id)

    with open(save_recipes_file_path, 'r', encoding='utf-8') as file:
        recipes = json.load(file)
    if len(recipes):
        # Создаем клавиатуру с кнопками для выбора рецепта
        keyboard = InlineKeyboardMarkup()
        for recipe_name_model in recipes:
            keyboard.add(InlineKeyboardButton(recipe_name_model, callback_data=f'show_one_of_save_recipe:{recipe_name_model}'))
        
        keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_welcome'))

        # Отправляем сообщение с клавиатурой
        bot.send_message(call.message.chat.id, 'Выберите рецепт:', reply_markup=keyboard)

    else:
        sent_message = bot.send_message(call.message.chat.id, "Список выбранных рецептов пуст.")
        global timewait
        time.sleep(timewait)  # Задержка в 2 секунды 
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        start_command(call.message)

#2 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('show_one_of_save_recipe:'))
def show_one_of_save_recipe(call):
    try:
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Получаем название рецепта из callback_data
        global recipe_name
        if len(recipe_name) == 0:
            recipe_name = call.data.split(':')[1]
        
        # Открываем файл с рецептами
        with open(save_recipes_file_path, 'r', encoding='utf-8') as file:
            recipes = json.load(file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = recipes.get(recipe_name)
        
        if recipe_info:
            # Формируем сообщение с информацией о рецепте
            recipe_text = f"📋 *{recipe_name}*\n\n"
            recipe_text += f"🕒 *Время приготовления:* {recipe_info.get('time')}\n\n"
            recipe_text += "🥦 *Ингредиенты:*\n"
            for ingredient, amount in recipe_info.get('ingredients', {}).items():
                recipe_text += f"- {ingredient}: {amount}\n"
            
            recipe_text += "\n📝 *Инструкции:*\n"
            for instructions, amount in recipe_info.get('instructions', {}).items():
                recipe_text += f"{instructions}) {amount}\n"
            # Разделяем инструкции по строкам и добавляем их к сообщению
            
            sent_message = bot.send_message(call.message.chat.id, recipe_text, parse_mode='Markdown')
            
            # Добавляем кнопки "Добавить" и "Назад"
            keyboard = InlineKeyboardMarkup(row_width=3)
            keyboard.add(InlineKeyboardButton("Удалить", callback_data=f'delete_save_recipe:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Редактировать", callback_data=f'edit_save_recipe:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_save_recipe'))
            
            # Отправляем сообщение с кнопками
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=sent_message.message_id, reply_markup=keyboard)
    
    except Exception as e:
        print(f"An error occurred: {e}")

#3 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_save_recipe:'))
def delete_save_recipe(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name 

        with open(save_recipes_file_path, 'r', encoding='utf-8') as save_recipes_file:
                    save_recipes = json.load(save_recipes_file)
               
        del save_recipes[recipe_name]

        with open(save_recipes_file_path, 'w', encoding='utf-8') as save_recipes_file:
            json.dump(save_recipes, save_recipes_file, ensure_ascii=False, indent=4)

                    
        
        sent_message = bot.send_message(call.message.chat.id, "Рецепт успешно удален из списка сохраненных рецептов.")
        global timewait
        time.sleep(timewait)  # Задержка в 2 секунды 
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        start_command(call.message)

    except Exception as e:
        print(f"An error occurred: {e}")

#3 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_save_recipe:'))
def edit_save_recipe(call):
    try:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except telebot.apihelper.ApiException as e:
            pass
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(save_recipes_file_path, 'r', encoding='utf-8') as save_recipes_file:
            all_recipes = json.load(save_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            # Формируем сообщение с информацией о рецепте
            recipe_text = f"📋 *{recipe_name}*\n\n"
            recipe_text += f"🕒 *Время приготовления:* {recipe_info.get('time')}\n\n"
            recipe_text += "🥦 *Ингредиенты:*\n"
            for ingredient, amount in recipe_info.get('ingredients', {}).items():
                recipe_text += f"- {ingredient}: {amount}\n"
            
            recipe_text += "\n📝 *Инструкции:*\n"
            for instructions, amount in recipe_info.get('instructions', {}).items():
                recipe_text += f"{instructions}) {amount}\n"
            
            # Добавляем кнопки "Время", "Ингредиенты", "Инструкция"
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("Изменить название", callback_data=f'edit_save_recipe_name:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить время", callback_data=f'edit_save_recipe_time:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить ингредиенты", callback_data=f'edit_save_recipe_ingredients:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить инструкцию", callback_data=f'edit_save_recipe_instructions:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_show_one_of_save_recipe'))
            
            # Отправляем сообщение с кнопками
            bot.send_message(call.message.chat.id, recipe_text, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_save_recipe_name:'))
def edit_save_recipe_name(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name

        
        sent_message = bot.send_message(call.message.chat.id, f"Введите новое название для рецепта {recipe_name}:")
        
        # Ожидаем ответа пользователя
        @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
        def handle_user_input(message):
            if message.text:
                new_recipe_name = message.text.strip()
                
                with open(save_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
                    all_recipes = json.load(all_recipes_file)
               
                
                # Проверяем, существует ли рецепт с таким новым названием
                if new_recipe_name in all_recipes:
                    bot.send_message(call.message.chat.id, f"Рецепт с названием {new_recipe_name} уже существует. Пожалуйста, выберите другое название.")
                    return
                
                global recipe_name
                # Получаем информацию о рецепте с старым названием
                recipe_info = all_recipes.pop(recipe_name, None)
                
                if recipe_info:
                    # Добавляем рецепт с новым названием и информацией из старого рецепта
                    all_recipes[new_recipe_name] = recipe_info
                    
                    # Перезаписываем данные в файле
                    with open(save_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    
                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
    
                    recipe_name = new_recipe_name
                    edit_save_recipe(call)

                else:
                    bot.send_message(call.message.chat.id, f"Рецепт с названием {recipe_name} не найден.")
                
        # Ожидаем следующего шага - ввода нового названия рецепта
        bot.register_next_step_handler(sent_message, handle_user_input)
        
    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_save_recipe_time:'))
def edit_save_recipe_time(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(save_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            # Получаем текущее время из рецепта
            current_time = recipe_info.get('time', '')
            
            # Отправляем сообщение с текущим временем и просьбой ввести новое время
            sent_message = bot.send_message(call.message.chat.id, f"Текущее время для рецепта {recipe_name}: {current_time}\n\nВведите новое время:")
            
            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_time = message.text.strip()
                    
                    # Обновляем время рецепта
                    recipe_info['time'] = new_time
                    
                    # Перезаписываем данные в файле
                    with open(save_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    
                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_save_recipe(call)
                
            # Ожидаем следующего шага - ввода времени пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_save_recipe_ingredients:'))
def edit_save_recipe_ingredients(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(save_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            current_ingredients_str = f"Текущие ингредиенты для рецепта {recipe_name}:\n"
            for ingredient, quantity in recipe_info.get('ingredients', {}).items():
                current_ingredients_str += f"{ingredient} - {quantity}\n"

            # Затем отправляем запрос на ввод новых ингредиентов
            sent_message = bot.send_message(call.message.chat.id, current_ingredients_str + "\nВведите новые ингредиенты (каждый с новой строки):")

            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_ingredients = message.text.strip().split('\n')
                    
                    # Обновляем ингредиенты рецепта
                    updated_ingredients = {}
                    delete = []
                    for ingredient in new_ingredients:
                        ingredient_split = ingredient.strip().split(' ')
                        if len(ingredient_split) >= 2 and ingredient_split[1] == '0':
                            delete.append(ingredient_split[0])
                        elif len(ingredient_split) >= 2:
                            ingredient_name = str(ingredient_split[0])
                            quantity = ingredient_split[-1]
                            updated_ingredients[ingredient_name] = quantity
                        elif len(ingredient_split) == 1:
                            ingredient_name = str(ingredient_split[0])
                            quantity = " "
                            updated_ingredients[ingredient_name] = quantity
                        else:
                            bot.send_message(call.message.chat.id, f"Ошибка: Неверный формат ввода для ингредиента: {ingredient}. Используйте формат 'ингредиент - количество'")
                    
                    # Обновляем ингредиенты рецепта
                    if updated_ingredients:
                        recipe_info['ingredients'].update(updated_ingredients)
                    for a in delete:
                        if a in recipe_info['ingredients']:
                            del recipe_info['ingredients'][a]

                        
                    # Перезаписываем данные в файле
                    with open(save_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    

                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_save_recipe(call)
            
            # Ожидаем следующего шага - ввода новых ингредиентов пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_save_recipe_instructions:'))
def edit_save_recipe_instructions(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(save_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            current_instructions_str = f"Как использовать:\n"
            current_instructions_str += f"'число') - удаление инструкции под номером 'число'\n"
            current_instructions_str += f"'число') 'любой текст' - добавление инструкции под номером 'число' с текстом 'любой текст'\n"
            for instructions, quantity in recipe_info.get('instructions', {}).items():
                current_instructions_str += f"{instructions}) {quantity}\n"

            # Затем отправляем запрос на ввод новых инструкций
            sent_message = bot.send_message(call.message.chat.id, current_instructions_str + "\nВведите новые инструкции (каждая с новой строки):")


            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_instruction = message.text.strip().split('\n')
                    
                    # Обновляем ингредиенты рецепта
                    updated_instruction = {}
                    delete = []
                    for instruction in new_instruction:
                        instruction_stripped = instruction.strip()
                        instruction_split = instruction_stripped.split(')')
                        if len(instruction_split) == 2 and instruction_split[1] == '':
                            delete.append(instruction_split[0])
                        elif len(instruction_split) >= 2:
                            instruction_name = str(instruction_split[0])
                            quantity = instruction_split[-1]
                            updated_instruction[instruction_name] = quantity
                        else:
                            bot.send_message(call.message.chat.id, f"Ошибка: Неверный формат ввода для ингредиента: {instruction}. Используйте формат 'ингредиент - количество'")
                    
                    # Обновляем ингредиенты рецепта
                    if updated_instruction:
                        recipe_info['instructions'].update(updated_instruction)
                    for a in delete:
                        if a in recipe_info['instructions']:
                            del recipe_info['instructions'][a]

                        
                    # Перезаписываем данные в файле
                    with open(save_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    

                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_save_recipe(call)
            
            # Ожидаем следующего шага - ввода новых ингредиентов пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")



#1 этаж
@bot.callback_query_handler(func=lambda call: call.data == 'shope_list')
def shope_list(call):

    global all_ingredients
    MAX_BUTTON_TEXT_LENGTH = 27

    bot.delete_message(call.message.chat.id, call.message.message_id)

    if len(all_ingredients):
                

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for i in range(len(all_ingredients)):
            keyboard.add(types.InlineKeyboardButton(text=all_ingredients[i], callback_data=f'choose_shope_ingredient:{i}'))


        keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_welcome'))
        bot.send_message(call.message.chat.id, 'Ингредиенты для покупок:', reply_markup=keyboard)


    else:
        sent_message = bot.send_message(call.message.chat.id, "Список пуст.")
        global timewait
        time.sleep(timewait)  # Задержка в 2 секунды 
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        start_command(call.message)

#2 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_shope_ingredient:'))
def choose_shope_ingredient(call):

    ingredient = call.data
    ingredient = int(ingredient.split(':')[1])
    del all_ingredients[ingredient]
    shope_list(call)








#1 этаж
@bot.callback_query_handler(func=lambda call: call.data == 'doing_recipe')
def doing_recipe(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)

    markup = types.InlineKeyboardMarkup(row_width=4)
    item_all_recipe = types.InlineKeyboardButton("Все рецепты", callback_data='all_recipe')
    item_created_recipe = types.InlineKeyboardButton("Создать рецепт", callback_data='created_recipe')
    item_internet_recipe = types.InlineKeyboardButton("Рецепты с интернета", callback_data='internet_recipe')

    markup.add(item_all_recipe)
    markup.add(item_created_recipe)
    markup.add(item_internet_recipe)

    markup.add(InlineKeyboardButton("Назад", callback_data='back_to_welcome'))

    bot.send_message(call.message.chat.id, 'Выберете действие', reply_markup=markup)

#2 этаж
@bot.callback_query_handler(func=lambda call: call.data == 'all_recipe')
def show_all_recipe(call):

    global recipe_name
    recipe_name = ""

    bot.delete_message(call.message.chat.id, call.message.message_id)

    try:
        # Открываем файл с рецептами
        with open(all_recipes_file_path, 'r', encoding='utf-8') as file:
            recipes = json.load(file)
        
        # Проверяем, пуст ли файл
        if not recipes:
            bot.send_message(call.message.chat.id, "Список рецептов пуст.")
            return
        
        # Создаем клавиатуру с кнопками для выбора рецепта
        keyboard = InlineKeyboardMarkup()
        for recipe_name_model in recipes:
            keyboard.add(InlineKeyboardButton(recipe_name_model, callback_data=f'show_one_of_all_recipe:{recipe_name_model}'))
        
        keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_doing_recipe'))

        # Отправляем сообщение с клавиатурой
        bot.send_message(call.message.chat.id, 'Выберите рецепт:', reply_markup=keyboard)
        
    except Exception as e:
        print(f"An error occurred: {e}")

#3 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('show_one_of_all_recipe:'))
def show_one_of_all_recipe(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Получаем название рецепта из callback_data
        global recipe_name
        if len(recipe_name) == 0:
            recipe_name = call.data.split(':')[1]
        
        # Открываем файл с рецептами
        with open(all_recipes_file_path, 'r', encoding='utf-8') as file:
            recipes = json.load(file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = recipes.get(recipe_name)
        
        if recipe_info:
            # Формируем сообщение с информацией о рецепте
            recipe_text = f"📋 *{recipe_name}*\n\n"
            recipe_text += f"🕒 *Время приготовления:* {recipe_info.get('time')}\n\n"
            recipe_text += "🥦 *Ингредиенты:*\n"
            for ingredient, amount in recipe_info.get('ingredients', {}).items():
                recipe_text += f"- {ingredient}: {amount}\n"
            
            recipe_text += "\n📝 *Инструкции:*\n"
            for instructions, amount in recipe_info.get('instructions', {}).items():
                recipe_text += f"{instructions}) {amount}\n"
            
            sent_message = bot.send_message(call.message.chat.id, recipe_text, parse_mode='Markdown')
            
            # Добавляем кнопки "Добавить" и "Назад"
            keyboard = InlineKeyboardMarkup(row_width=3)
            keyboard.add(InlineKeyboardButton("Добавить", callback_data=f'add_all_recipe:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Удалить", callback_data=f'delete_all_recipe:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Редактировать", callback_data=f'edit_all_recipe:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_all_recipe'))
            
            # Отправляем сообщение с кнопками
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=sent_message.message_id, reply_markup=keyboard)
    
    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('add_all_recipe:'))
def add_all_recipe(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        with open(save_recipes_file_path, 'r', encoding='utf-8') as save_recipes_file:
            save_recipes = json.load(save_recipes_file)


        global all_ingredients
        ingredients = all_recipes[recipe_name].get('ingredients', {})
        # Проходим по ингредиентам текущего рецепта
        for ingredient, quantity in ingredients.items():
            # Форматируем строку для включения ингредиента и его количества
            ingredient_str = f"{ingredient} - {quantity}"

            # Проверяем, есть ли уже ингредиент в списке all_ingredients
            found = False
            for idx, existing_ingredient in enumerate(all_ingredients):
                if ingredient in existing_ingredient:
                    found = True
                    existing_ingredient_parts = existing_ingredient.split(' - ')[1].split(' | ')

                    new_quantity = int(quantity.split(' ')[0])
                    new_name = quantity.split(' ')[1]

                    updated_ingredient_str = f"{ingredient} -"

                    b = True

                    for i in range(len(existing_ingredient_parts)):
                        existing_quantity = existing_ingredient_parts[i].split(' ')[0]
                        existing_name = ' '.join(existing_ingredient_parts[i].split(' ')[1:])

                        if existing_name == new_name:
                            b == False
                            updated_quantity = existing_quantity + new_quantity
                            unit = existing_name
                            updated_ingredient_str += f" {updated_quantity} {unit} |"
                        else:
                            updated_ingredient_str += f" {existing_quantity} {existing_name} |"

                    if b:
                        updated_ingredient_str += f" {new_quantity} {new_name} |"

                    updated_ingredient_str = updated_ingredient_str[:len(updated_ingredient_str)-2]


                    all_ingredients[idx] = updated_ingredient_str
                    break

            # Если ингредиент не найден в списке, добавляем его
            if not found:
                all_ingredients.append(ingredient_str)


        save_recipes[recipe_name] = all_recipes[recipe_name]

        with open(save_recipes_file_path, 'w', encoding='utf-8') as save_recipes_file:
            json.dump(save_recipes, save_recipes_file, ensure_ascii=False, indent=4)

        

        sent_message = bot.send_message(call.message.chat.id, "Рецепт успешно добавлен в список сохраненных рецептов.")
        global timewait
        time.sleep(timewait)  # Задержка в 2 секунды 
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        start_command(call.message)

    except Exception as e:
        print(f"An error occurred: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_all_recipe:'))
def delete_all_recipe(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name 

        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
                    save_recipes = json.load(all_recipes_file)
               
        del save_recipes[recipe_name]

        with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
            json.dump(save_recipes, all_recipes_file, ensure_ascii=False, indent=4)

                    
        
        sent_message = bot.send_message(call.message.chat.id, "Рецепт успешно удален из списка сохраненных рецептов.")
        global timewait
        time.sleep(timewait)  # Задержка в 2 секунды 
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        start_command(call.message)

    except Exception as e:
        print(f"An error occurred: {e}")

#4 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_recipe:'))
def edit_all_recipe(call):
    try:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except telebot.apihelper.ApiException as e:
            pass
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            # Формируем сообщение с информацией о рецепте
            recipe_text = f"📋 *{recipe_name}*\n\n"
            recipe_text += f"🕒 *Время приготовления:* {recipe_info.get('time')}\n\n"
            recipe_text += "🥦 *Ингредиенты:*\n"
            for ingredient, amount in recipe_info.get('ingredients', {}).items():
                recipe_text += f"- {ingredient}: {amount}\n"
            
            recipe_text += "\n📝 *Инструкции:*\n"
            for instructions, amount in recipe_info.get('instructions', {}).items():
                recipe_text += f"{instructions}) {amount}\n"
            
            # Добавляем кнопки "Время", "Ингредиенты", "Инструкция"
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("Изменить название", callback_data=f'edit_all_recipe_name:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить время", callback_data=f'edit_all_recipe_time:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить ингредиенты", callback_data=f'edit_all_recipe_ingredients:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Изменить инструкцию", callback_data=f'edit_all_recipe_instructions:{recipe_name}'))
            keyboard.add(InlineKeyboardButton("Назад", callback_data='back_to_show_one_of_all_recipe'))
            
            # Отправляем сообщение с кнопками
            bot.send_message(call.message.chat.id, recipe_text, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#5 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_recipe_name:'))
def edit_all_recipe_name(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name

        
        sent_message = bot.send_message(call.message.chat.id, f"Введите новое название для рецепта {recipe_name}:")
        
        # Ожидаем ответа пользователя
        @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
        def handle_user_input(message):
            if message.text:
                new_recipe_name = message.text.strip()
                
                with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
                    all_recipes = json.load(all_recipes_file)
               
                
                # Проверяем, существует ли рецепт с таким новым названием
                if new_recipe_name in all_recipes:
                    bot.send_message(call.message.chat.id, f"Рецепт с названием {new_recipe_name} уже существует. Пожалуйста, выберите другое название.")
                    return
                
                global recipe_name
                # Получаем информацию о рецепте с старым названием
                recipe_info = all_recipes.pop(recipe_name, None)
                
                if recipe_info:
                    # Добавляем рецепт с новым названием и информацией из старого рецепта
                    all_recipes[new_recipe_name] = recipe_info
                    
                    # Перезаписываем данные в файле
                    with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    
                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
    
                    recipe_name = new_recipe_name
                    edit_all_recipe(call)

                else:
                    bot.send_message(call.message.chat.id, f"Рецепт с названием {recipe_name} не найден.")
                
        # Ожидаем следующего шага - ввода нового названия рецепта
        bot.register_next_step_handler(sent_message, handle_user_input)
        
    except Exception as e:
        print(f"An error occurred: {e}")

#5 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_recipe_time:'))
def edit_all_recipe_time(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            # Получаем текущее время из рецепта
            current_time = recipe_info.get('time', '')
            
            # Отправляем сообщение с текущим временем и просьбой ввести новое время
            sent_message = bot.send_message(call.message.chat.id, f"Текущее время для рецепта {recipe_name}: {current_time}\n\nВведите новое время:")
            
            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_time = message.text.strip()
                    
                    # Обновляем время рецепта
                    recipe_info['time'] = new_time
                    
                    # Перезаписываем данные в файле
                    with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    
                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_all_recipe(call)
                
            # Ожидаем следующего шага - ввода времени пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#5 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_recipe_ingredients:'))
def edit_all_recipe_ingredients(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info: 
            current_ingredients_str = f"Текущие ингредиенты для рецепта {recipe_name}:\n"
            for ingredient, quantity in recipe_info.get('ingredients', {}).items():
                current_ingredients_str += f"{ingredient} - {quantity}\n"

            current_ingredients_str += f"\nКак использовать:\n"
            current_ingredients_str += f"'ингредиент' - 0 - удаление ингредиента под номером 'число'\n"
            current_ingredients_str += f"'ингредиент' - 'любой текст' - добавление ингредиента\n"
            current_ingredients_str += "\n\nВведите новые ингредиенты (каждый с новой строки):"
            # Затем отправляем запрос на ввод новых ингредиентов
            sent_message = bot.send_message(call.message.chat.id, current_ingredients_str)

            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_ingredients = message.text.strip().split('\n')
                    
                    # Обновляем ингредиенты рецепта
                    updated_ingredients = {}
                    delete = []
                    for ingredient in new_ingredients:
                        ingredient_split = ingredient.strip().split('-')
                        if len(ingredient_split) == 2 and ingredient_split[1] == '0':
                            delete.append(ingredient_split[0])
                        elif len(ingredient_split) >= 2:
                            ingredient_name = str(ingredient_split[0])
                            quantity = ingredient_split[-1]
                            updated_ingredients[ingredient_name] = quantity
                        elif len(ingredient_split) == 1:
                            ingredient_name = str(ingredient_split[0])
                            quantity = " "
                            updated_ingredients[ingredient_name] = quantity
                        else:
                            bot.send_message(call.message.chat.id, f"Ошибка: Неверный формат ввода для ингредиента: {ingredient}. Используйте формат 'ингредиент - количество'")
                    
                    # Обновляем ингредиенты рецепта
                    if updated_ingredients:
                        recipe_info['ingredients'].update(updated_ingredients)
                    for a in delete:
                        if a in recipe_info['ingredients']:
                            del recipe_info['ingredients'][a]

                        
                    # Перезаписываем данные в файле
                    with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    

                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_all_recipe(call)
            
            # Ожидаем следующего шага - ввода новых ингредиентов пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

#5 этаж
@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_all_recipe_instructions:'))
def edit_all_recipe_instructions(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name
        
        # Открываем файл с рецептами для чтения
        with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
            all_recipes = json.load(all_recipes_file)
        
        # Получаем информацию о выбранном рецепте
        recipe_info = all_recipes.get(recipe_name)
        
        if recipe_info:
            current_instructions_str = f"Как использовать:\n"
            current_instructions_str += f"'число') - удаление инструкции под номером 'число'\n"
            current_instructions_str += f"'число') 'любой текст' - добавление инструкции под номером 'число' с текстом 'любой текст'\n"
            for instructions, quantity in recipe_info.get('instructions', {}).items():
                current_instructions_str += f"{instructions}) {quantity}\n"

            # Затем отправляем запрос на ввод новых инструкций
            sent_message = bot.send_message(call.message.chat.id, current_instructions_str + "\nВведите новые инструкции (каждая с новой строки):")


            # Ожидаем ответа пользователя
            @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
            def handle_user_input(message):
                if message.text:
                    new_instruction = message.text.strip().split('\n')
                    
                    # Обновляем ингредиенты рецепта
                    updated_instruction = {}
                    delete = []
                    for instruction in new_instruction:
                        instruction_stripped = instruction.strip()
                        instruction_split = instruction_stripped.split(')')
                        if len(instruction_split) == 2 and instruction_split[1] == '':
                            delete.append(instruction_split[0])
                        elif len(instruction_split) >= 2:
                            instruction_name = str(instruction_split[0])
                            quantity = instruction_split[-1]
                            updated_instruction[instruction_name] = quantity
                        else:
                            bot.send_message(call.message.chat.id, f"Ошибка: Неверный формат ввода для ингредиента: {instruction}. Используйте формат 'ингредиент - количество'")
                    
                    # Обновляем ингредиенты рецепта
                    if updated_instruction:
                        recipe_info['instructions'].update(updated_instruction)
                    for a in delete:
                        if a in recipe_info['instructions']:
                            del recipe_info['instructions'][a]

                        
                    # Перезаписываем данные в файле
                    with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                        json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    

                    # Удаляем предыдущее сообщение бота и сообщение пользователя
                    try:
                        bot.delete_message(sent_message.chat.id, sent_message.message_id)
                        bot.delete_message(message.chat.id, message.message_id)
                    except Exception as e:
                        print(f"An error occurred while deleting message: {e}")
                    
                    # Вызываем функцию для редактирования других аспектов рецепта
                    edit_all_recipe(call)
            
            # Ожидаем следующего шага - ввода новых ингредиентов пользователем
            bot.register_next_step_handler(sent_message, handle_user_input)
        else:
            bot.send_message(call.message.chat.id, f"Рецепт {recipe_name} не найден.")
    
    except Exception as e:
        print(f"An error occurred: {e}")



#2 этаж
@bot.callback_query_handler(func=lambda call: call.data == 'created_recipe')
def created_recipe(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        # Получаем название рецепта из callback_data
        global recipe_name

        
        sent_message = bot.send_message(call.message.chat.id, f"Введите название для рецепта {recipe_name}:")
        
        # Ожидаем ответа пользователя
        @bot.message_handler(func=lambda message: message.chat.id == call.message.chat.id)
        def handle_user_input(message):
            if message.text:
                new_recipe_name = message.text.strip()
                
                with open(all_recipes_file_path, 'r', encoding='utf-8') as all_recipes_file:
                    all_recipes = json.load(all_recipes_file)
               
                
                # Проверяем, существует ли рецепт с таким новым названием
                if new_recipe_name in all_recipes:
                    bot.send_message(call.message.chat.id, f"Рецепт с названием {new_recipe_name} уже существует. Пожалуйста, выберите другое название.")
                    return
                
                new_recipe = {
                            "ingredients": {},
                            "instructions": {},
                            "time": ''
                }
                
                all_recipes[new_recipe_name] = new_recipe

                with open(all_recipes_file_path, 'w', encoding='utf-8') as all_recipes_file:
                    json.dump(all_recipes, all_recipes_file, ensure_ascii=False, indent=4)
                    
                # Удаляем предыдущее сообщение бота и сообщение пользователя
                try:
                    bot.delete_message(sent_message.chat.id, sent_message.message_id)
                    bot.delete_message(message.chat.id, message.message_id)
                except Exception as e:
                    print(f"An error occurred while deleting message: {e}")
    
                global recipe_name
                recipe_name = new_recipe_name
                edit_all_recipe(call)

            else:
                bot.send_message(call.message.chat.id, f"Рецепт с названием {recipe_name} не найден.")
                
        # Ожидаем следующего шага - ввода нового названия рецепта
        bot.register_next_step_handler(sent_message, handle_user_input)
        
    except Exception as e:
        print(f"An error occurred: {e}")








def get_user_input(message):
    # Функция будет ожидать ввод от пользователя и возвращать текст сообщения
    user_input = message.text
    return user_input
