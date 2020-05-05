import requests
import secrets
from data import db_session
from data.users import User

from telegram import Update
from telegram import ParseMode
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
from telegram.utils.request import Request

from bot.buttons import get_base_reply_keyboard
from bot.settings import TOKEN

from methods.authorization import auth
from methods.journal import *
from methods.crypto import password_decrypt, password_encrypt


CALLBACK_BUTTON1_MARKS = "callback_button1_marks"
CALLBACK_BUTTON2_SKIPS = "callback_button2_skips"
CALLBACK_BUTTON3_SCHEDULE = "callback_button3_schedule"
CALLBACK_BUTTON4_BACK = "callback_button4_back"
CALLBACK_BUTTON5_MONDAY = "понедельник"
CALLBACK_BUTTON6_THURSDAY = "четверг"
CALLBACK_BUTTON7_TUESDAY = "вторник"
CALLBACK_BUTTON8_FRIDAY = 'пятница'
CALLBACK_BUTTON9_WEDNESDAY = 'среда'
CALLBACK_BUTTON10_SATURDAY = "суббота"
CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button9_hide"

TITLES = {
    CALLBACK_BUTTON1_MARKS: "Оценки️",
    CALLBACK_BUTTON2_SKIPS: "Пропуски️",
    CALLBACK_BUTTON3_SCHEDULE: "Дневник ➡️",
    CALLBACK_BUTTON4_BACK: "Назад ⬅️",
    CALLBACK_BUTTON5_MONDAY: "Понедельник ",
    CALLBACK_BUTTON6_THURSDAY: "Четверг ",
    CALLBACK_BUTTON7_TUESDAY: "Вторник ",
    CALLBACK_BUTTON8_FRIDAY: "Пятница ",
    CALLBACK_BUTTON9_WEDNESDAY: "Среда ",
    CALLBACK_BUTTON10_SATURDAY: "Суббота ",
    CALLBACK_BUTTON_HIDE_KEYBOARD: "Скрыть клавиатуру ",
}

REQUEST_KWARGS = {
    'proxy_url': 'socks5://77.81.226.18:1080',
}


def get_base_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_MARKS], callback_data=CALLBACK_BUTTON1_MARKS),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_SKIPS], callback_data=CALLBACK_BUTTON2_SKIPS),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_SCHEDULE], callback_data=CALLBACK_BUTTON3_SCHEDULE),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_keyboard2():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON5_MONDAY], callback_data=CALLBACK_BUTTON5_MONDAY),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON6_THURSDAY], callback_data=CALLBACK_BUTTON6_THURSDAY),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON7_TUESDAY], callback_data=CALLBACK_BUTTON7_TUESDAY),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON8_FRIDAY], callback_data=CALLBACK_BUTTON8_FRIDAY)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON9_WEDNESDAY], callback_data=CALLBACK_BUTTON9_WEDNESDAY),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON10_SATURDAY], callback_data=CALLBACK_BUTTON10_SATURDAY)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON1_MARKS:
        # тут будет информация об оценках
        query.edit_message_text(
            text=current_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        """context.bot.send_message(
            chat_id=chat_id,
            text="Новое сообщение".format(data),
            reply_markup=get_base_inline_keyboard(),
        )"""
    elif data == CALLBACK_BUTTON2_SKIPS:
        # тут будет информация о пропусках
        query.edit_message_text(
            text="что)",
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON3_SCHEDULE:
        # клавиатура с дневником
        query.edit_message_text(
            text=current_text,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON4_BACK:
        # возврат назад
        query.edit_message_text(
            text=current_text,
            reply_markup=get_base_inline_keyboard(),
        )
    elif data in (CALLBACK_BUTTON5_MONDAY, CALLBACK_BUTTON6_THURSDAY,
                  CALLBACK_BUTTON7_TUESDAY, CALLBACK_BUTTON8_FRIDAY,
                  CALLBACK_BUTTON9_WEDNESDAY, CALLBACK_BUTTON10_SATURDAY):
        session_db = db_session.create_session()
        user = session_db.query(User).filter(User.telegram_id == chat_id).first()
        if not user:
            output = ['Вы ещё не авторизованы! Для авторизации введите логин и пароль через команду /login '
                      'в формате /login login:password']
        else:
            output = []
            session = requests.Session()
            login = user.name
            key = user.hash
            password = password_decrypt(user.hashed_password, key).decode()
            auth(session, login, password)
            full_journal = get_full_journal_week(session)
            lessons_dictionary = get_lessons(full_journal)
            for days, lessons in lessons_dictionary.items():
                days = days.lower()
                if data in days:
                    output.append(f'Расписание за {days}:')
                    for lesson in lessons:
                        output.append(lesson)
        query.edit_message_text(
            text='\n'.join(output),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_keyboard2(),
        )
    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        context.bot.send_message(
            chat_id=chat_id,
            text="Скрыл клавиатуру.\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Привет! Для начала работы введь логин и пароль от элжура через команду /login"
             "в формате /login login:password",
        reply_markup=get_base_reply_keyboard(),
    )


def help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Тут будет подробная помощь",
        reply_markup=get_base_inline_keyboard(),
    )


def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == 'Помощь':
        return help(update=update, context=context)
    elif text.startswith('/login'):
        try:
            session_db = db_session.create_session()
            check_user = session_db.query(User).filter(User.telegram_id == chat_id).first()
            if check_user:
                reply_text = 'Вы уже авторизованы!'
            else:
                login, password = text.replace('/login ', '').split(':')
                session = requests.Session()
                auth(session, login, password)
                user = User()
                user.telegram_id = chat_id
                user.name = login
                user.hash = secrets.token_bytes(32)
                user.hashed_password = password_encrypt(password.encode(), user.hash)
                session_db.add(user)
                session_db.commit()
                reply_text = 'Успешная авторизация!'
        except Exception as e:
            reply_text = 'Неверный логин или пароль.'
        update.message.reply_text(
            text=reply_text,
            reply_markup=get_base_inline_keyboard(),
        )


def main():
    # путь до бд
    db_session.global_init('E:\\web-server\\db\\users.sqlite')
    # токен от бота
    updater = Updater(
        token=TOKEN,
        use_context=True,
        request_kwargs=REQUEST_KWARGS
    )

    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    message_handler = MessageHandler(Filters.text, echo)
    buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.dispatcher.add_handler(buttons_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
