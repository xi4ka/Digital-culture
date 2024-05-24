import logging
import config
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from handlers import (
    start,
    userecipe,
    button,
    shopping_list,
    saverecipe,
    createrecipe,
    addingredient,
    addinstructions,
    deleteingredient,
    deleteinstruction,
    deleterecipe,
    search_by_ingredients,
    search_recipe
)




def main() -> None:
    application = Application.builder().token(config.TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("userecipe", userecipe))
    application.add_handler(CommandHandler("shoppinglist", shopping_list))
    application.add_handler(CommandHandler("saverecipe", saverecipe))
    application.add_handler(CommandHandler("createrecipe", createrecipe)) 
    application.add_handler(CommandHandler("addingredient", addingredient)) 
    application.add_handler(CommandHandler("addinstructions", addinstructions))
    application.add_handler(CommandHandler("deleteingredient", deleteingredient))
    application.add_handler(CommandHandler("deleteinstruction", deleteinstruction))
    application.add_handler(CommandHandler("deleterecipe", deleterecipe))
    application.add_handler(CommandHandler("searchbyingredients", search_by_ingredients))
    application.add_handler(CommandHandler("searchrecipe", search_recipe))
    application.add_handler(CallbackQueryHandler(button))


    application.run_polling()


if __name__ == '__main__':
    main()
