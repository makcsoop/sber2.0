# import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton


# logging.basicConfig(format='', level=logging.DEBUG)
# logger = logging.getLogger(__name__)


async def start(update, context):
    # user = update.effective_user
    await update.message.reply_text(rf"КОМАНДА START")


async def help(update, context):
    user = update.effective_user
    await update.message.reply_text(f"Здравствуйте, {user.first_name}!\n"
                                    f"Бот предоставляет работу со следующими командами:\n"
                                    f"/start - ***\n"
                                    f"/help - Информация о боте\n"
                                    
                                    f"/show_menu - Показ меню\n"
                                    
                                    f"/make_order - Создать заказ")


async def show_menu(update, context):
    # user = update.effective_user
    # Получение меню из БД
    await update.message.reply_text(rf"Меню")


async def make_order(update, context):
    await update.message.reply_text(rf"Запрос на создание заказа. Ознакомьтесь с меню:"
                                    rf"*Меню*"
                                    rf"Для добавления блюд в заказ введите сообщение в следующем формате:"
                                    rf"id позиции * количество порций;"
                                    rf"Для отмены заказа введите /cancel")
    return 1


async def choose_positions(update, context):
    positions = update.message.text
    # Распаковка списка и создание заказа
    await update.message.reply_text("Введите данные банковской карты для оплаты")
    return 2


async def pay(update, context):
    card_data = update.message.text
    # Оплата заказа
    await update.message.reply_text("Ваш заказ оплачен. Номер заказа: ***.")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text(rf"Отмена")
    return ConversationHandler.END


make_order_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('make_order', make_order)],
    states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_positions)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, pay)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)


def main():
    application = Application.builder().token('6483910113:AAFZuaDBnl_TwnN1tV0PeEZvlTXIbQ7fSKA').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("show_menu", show_menu))

    application.add_handler(make_order_conv_handler)

    # reply_keyboard = [['/start']]
    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    application.run_polling()


if __name__ == '__main__':
    main()
