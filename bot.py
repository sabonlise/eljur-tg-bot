from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from api import TOKEN


def menu(update, context):
    keyboard = [[InlineKeyboardButton("расписание", callback_data='table'),
                 InlineKeyboardButton("чат", callback_data='chat')],
                [InlineKeyboardButton("книги", callback_data='books'),
                 InlineKeyboardButton("помощь", callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите функцию:", reply_markup=reply_markup)


def start(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="введите логин")

    kb = [[KeyboardButton('меню', callbackdata='menu')]]
    ReplyMarkup = ReplyKeyboardMarkup(kb)
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=ReplyMarkup)


def button(update, context):
    query = update.callback_query
    query.answer()
    try:
        if query.data == 'table':
            Functions.table(update, context)
            inf = "расписание:"
        elif query.data == 'chat':
            Functions.chat(update, context)
            inf = "чат:"
        elif query.data == 'books':
            Functions.books(update, context)
            inf = "библиотека:"
        elif query.data == 'help':
            inf = 'помощь:'
            Functions.help(update, context)
        else:
            inf = 'error'
    except Exception as er:
        print(er)
    query.edit_message_text(text=inf)


class Functions:
    def books(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="ого, это же библиотека, кто этим вообще пользуется?")

    def chat(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Здесь могла быть ваша реклама, но мы сделаем чат")

    def table(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Здесь будет расписание")

    def help(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Команды:")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/table - расписание")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/chat - чат")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/books - библиотека книг")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/menu - меню")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/help - помощь")


#start app
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

#commands
start = CommandHandler('start', start)
menu = CommandHandler('menu', menu)
table = CommandHandler("table", Functions.table)
chat = CommandHandler("chat", Functions.chat)
books = CommandHandler("books", Functions.books)
help = CommandHandler('help', Functions.help)


#add commands
dispatcher.add_handler(start)
dispatcher.add_handler(help)
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(table)
dispatcher.add_handler(menu)
dispatcher.add_handler(chat)
dispatcher.add_handler(books)

#start app
updater.start_polling()
