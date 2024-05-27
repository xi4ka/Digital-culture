# main.py
from DigitalCultureBot.handlers import bot  # Импортируем для регистрации обработчиков

if __name__ == '__main__':
    bot.polling(none_stop=True)
