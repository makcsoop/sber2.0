from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from server import open_data, all_info
import logging
import requests
import sqlite3
import json

# logging.basicConfig(format='', level=logging.DEBUG)
# logger = logging.getLogger(__name__)


# Список админов
admins = ['Arz_solo_guitar']


async def start(update, context):
    global admins
    # logger.info('HELLO')
    user = update.effective_user
    if user.username in admins:
        await update.message.reply_text("Возможность написания запроса доступна только пользователям!")
        return ConversationHandler.END
    await update.message.reply_text(f"Здравствуйте,  {user.first_name}!\n"
                                    f"Вас приветствует техническая поддержка корпоративного питания Сбербанка! "
                                    f"Пожалуйста, введите ваш вопрос. "
                                    f"Для отмены введите /cancel")
    return 1


async def help(update, context):
    global admins
    user = update.effective_user
    if user.username in admins:
        await update.message.reply_text("Вас приветствует техническая поддержка корпоративного питания Сбербанка! "
                                        "Версия для администратора. "
                                        "Бот предоставляет работу со следующими командами:\n"
                                        "/answer_request - Ввод и обработка запросов.")
        return

    await update.message.reply_text("Вас приветствует техническая поддержка корпоративного питания Сбербанка! "
                                    "Версия для пользователя. "
                                    "Бот предоставляет работу со следующими командами:\n"
                                    "/start - Ввод и обработка запросов.")


async def write_request(update, context):
    request = update.message.text
    user = update.effective_user
    url = "https://api.telegram.org/bot6509053870:AAHr8bWvPyUG3pf4JYCKdldd5P9xsIczJL0/getUpdates"
    chat_id = requests.get(url).json()['result'][0]['message']['chat']['id']

    con = sqlite3.connect('ticket_base.db')
    cur = con.cursor()
    con.execute("""INSERT INTO telegram_tickets (topic, user_id, status, chat_id) VALUES (?, ?, 'active', ?)""", (request, user.id, chat_id))
    con.commit()
    id = cur.execute("""SELECT id from telegram_tickets WHERE topic = ? AND user_id = ? AND status = 'active' AND chat_id = ?""",
                     (request, user.id, chat_id)).fetchone()[0]
    message_text = f"Запрос номер {id}. Вопрос: '{request}'. Отправитель: {user.username}"
    con.close()

    # Выбор админа, добавление админа: масштабируемость
    url = f"https://api.telegram.org/bot6509053870:AAHr8bWvPyUG3pf4JYCKdldd5P9xsIczJL0/sendMessage?chat_id=1864568706&text={message_text}"
    requests.get(url)
    await update.message.reply_text("Ваш запрос отправлен, ожидайте ответа.")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Отмена")
    context.user_data.clear()
    return ConversationHandler.END


make_request_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, write_request)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)


async def answer_request(update, context):
    global admins
    user = update.effective_user
    if user.username not in admins:
        await update.message.reply_text("Возможность ответа на запрос доступна только админам!")
        return ConversationHandler.END

    con = sqlite3.connect('ticket_base.db')
    cur = con.cursor()
    tickets_info = cur.execute("""SELECT * FROM telegram_tickets WHERE status = ?""", ('active',)).fetchmany(10)
    con.close()
    for i in tickets_info:
        await update.message.reply_text(f"Запрос #{i[0]}: '{i[1]}'.")

    await update.message.reply_text("Введите id запроса, на который хотите ответить. Для отмены введите /cancel")
    return 1


async def write_request_id(update, context):
    context.user_data['request_id'] = update.message.text
    try:
        con = sqlite3.connect('ticket_base.db')
        cur = con.cursor()
        context.user_data['topic'], context.user_data['user_id'], context.user_data['status'], context.user_data['chat_id'] = cur.execute(
            """SELECT topic, user_id, status, chat_id from telegram_tickets WHERE id = ?""",
            (context.user_data['request_id'],)).fetchone()
        cur.execute("""UPDATE telegram_tickets SET status = ? WHERE id = ?""", ('passive', context.user_data['request_id']))
        con.commit()
        con.close()
    except TypeError:
        await update.message.reply_text("id запроса указан неверно!")
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text("Введите ответ на выбранный вопрос.")
    return 2


async def write_answer(update, context):
    answer = update.message.text
    user = update.effective_user

    message_text = f"Ответ на вопрос '{context.user_data['topic']}' от админа {user.username}: {answer}"

    url = f"https://api.telegram.org/bot6509053870:AAHr8bWvPyUG3pf4JYCKdldd5P9xsIczJL0/sendMessage?chat_id={context.user_data['chat_id']}&text={message_text}"
    requests.get(url)
    await update.message.reply_text(f"Ответ на вопрос {context.user_data['request_id']} отправлен.")
    context.user_data.clear()
    return ConversationHandler.END


answer_request_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('answer_request', answer_request)],
    states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, write_request_id)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, write_answer)]},
    fallbacks=[CommandHandler('cancel', cancel)]
)


def main():
    application = Application.builder().token('6509053870:AAHr8bWvPyUG3pf4JYCKdldd5P9xsIczJL0').build()

    application.add_handler(CommandHandler("help", help))

    application.add_handler(make_request_conv_handler)
    application.add_handler(answer_request_conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
