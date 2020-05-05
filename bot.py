from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from api import TOKEN
import requests
from methods.authorization import auth
from database import database

REQUEST_KWARGS = {
    'proxy_url': 'socks5://77.81.226.18:1080',
}


def menu(update, context):
    keyboard = [[InlineKeyboardButton("Расписание", callback_data='table'),
                 InlineKeyboardButton("Чат", callback_data='chat')],
                [InlineKeyboardButton("Книги", callback_data='books'),
                 InlineKeyboardButton("Помощь", callback_data='help')]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text='фунции выведены', reply_markup=reply_markup)


def start(update, context):  # недоделано
    # ввод данных
    context.bot.send_message(chat_id=update.effective_chat.id, text="введите логин")
    login = 1
    context.bot.send_message(chat_id=update.effective_chat.id, text="введите пароль")
    password = 2
    # пока костыль
    user_check = password_check = True
    if check(login, password, update.message.from_user['id']):
        menu(update, context)


def button(update, context):
    query = update.callback_query
    query.answer()
    try:
        if query.data == 'table':
            Functions.table(update, context)
            inf = "Расписание:"
        elif query.data == 'chat':
            Functions.chat(update, context)
            inf = "Чат:"
        elif query.data == 'books':
            Functions.books(update, context)
            inf = "Библиотека:"
        elif query.data == 'help':
            inf = 'Помощь:'
            Functions.help(update, context)
        else:
            inf = 'Error'
    except Exception as er:
        print(er)
    query.edit_message_text(text=inf)


class Functions:
    @staticmethod
    def books(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="ого, это же библиотека, кто этим вообще пользуется?")

    @staticmethod
    def chat(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Здесь могла быть ваша реклама, но мы сделаем чат")

    @staticmethod
    def table(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Здесь будет расписание")

    @staticmethod
    def help(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Команды:\n"
                                                                        "/table - расписание\n"
                                                                        "/chat - чат\n"
                                                                        "/books - библиотека книг\n"
                                                                        "/menu - меню\n"
                                                                        "/help - помощь")


def main():
    # start app
    updater = Updater(token=TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    dispatcher = updater.dispatcher

    # commands
    start_ = CommandHandler('start', start)
    menu_ = CommandHandler('menu', menu)
    table = CommandHandler("table", Functions.table)
    chat = CommandHandler("chat", Functions.chat)
    books = CommandHandler("books", Functions.books)
    help = CommandHandler('help', Functions.help)

    # add commands
    dispatcher.add_handler(start_)
    dispatcher.add_handler(help)
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(table)
    dispatcher.add_handler(menu_)
    dispatcher.add_handler(chat)
    dispatcher.add_handler(books)

    # start app
    updater.start_polling()


if __name__ == '__main__':
    main()
