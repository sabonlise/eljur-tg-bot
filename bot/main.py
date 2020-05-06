import requests
import secrets

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

from bot.schedule import *
from bot.buttons import get_base_reply_keyboard
from bot.settings import TOKEN, REQUEST_KWARGS

from methods.authorization import auth
from methods.journal import *
from methods.crypto import password_encrypt


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
CALLBACK_BUTTON_PREV_WEEK = 'callback_button_prev_week'
CALLBACK_BUTTON_NEXT_WEEK = 'callback_button_next_week'


TITLES = {
    CALLBACK_BUTTON1_MARKS: "Оценки️",
    CALLBACK_BUTTON2_SKIPS: "Пропуски️",
    CALLBACK_BUTTON3_SCHEDULE: "Дневник ️",
    CALLBACK_BUTTON4_BACK: "Назад ️",
    CALLBACK_BUTTON5_MONDAY: "Понедельник ",
    CALLBACK_BUTTON6_THURSDAY: "Четверг ",
    CALLBACK_BUTTON7_TUESDAY: "Вторник ",
    CALLBACK_BUTTON8_FRIDAY: "Пятница ",
    CALLBACK_BUTTON9_WEDNESDAY: "Среда ",
    CALLBACK_BUTTON10_SATURDAY: "Суббота ",
    CALLBACK_BUTTON_HIDE_KEYBOARD: "Скрыть клавиатуру ",
    CALLBACK_BUTTON_PREV_WEEK: "⬅️",
    CALLBACK_BUTTON_NEXT_WEEK: "➡️"
}


def change_buttons(update: Update, context: CallbackContext):
    schedule = save_schedule(update=update, context=context)
    week_days = list(schedule.keys())
    TITLES[CALLBACK_BUTTON5_MONDAY] = week_days[0]
    TITLES[CALLBACK_BUTTON6_THURSDAY] = week_days[3]
    TITLES[CALLBACK_BUTTON7_TUESDAY] = week_days[1]
    TITLES[CALLBACK_BUTTON8_FRIDAY] = week_days[4]
    TITLES[CALLBACK_BUTTON9_WEDNESDAY] = week_days[2]
    TITLES[CALLBACK_BUTTON10_SATURDAY] = week_days[5]


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


def get_schedule():
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
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PREV_WEEK], callback_data=CALLBACK_BUTTON_PREV_WEEK),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON4_BACK], callback_data=CALLBACK_BUTTON4_BACK),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_NEXT_WEEK], callback_data=CALLBACK_BUTTON_NEXT_WEEK)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def user_exists(update: Update, context: CallbackContext):
    session_db = db_session.create_session()
    chat_id = update.effective_message.chat_id
    user = session_db.query(User).filter(User.telegram_id == chat_id).first()
    if user:
        return True
    return False


def keyboard_callback_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id

    query = update.callback_query
    data = query.data

    current_text = update.effective_message.text

    if data == CALLBACK_BUTTON1_MARKS:
        # тут будет информация об оценках
        context.bot.send_message(
            chat_id=chat_id,
            text="Оценки за текущий период:",
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON2_SKIPS:
        # тут будет информация о пропусках
        context.bot.send_message(
            chat_id=chat_id,
            text="Пропуски за текущий период:",
            reply_markup=get_base_inline_keyboard(),
        )
    elif data == CALLBACK_BUTTON3_SCHEDULE:
        storage[chat_id] = {'week_state': 0}
        change_buttons(update=update, context=context)
        query.edit_message_text(
            text='Расписание за текущую неделю',
            reply_markup=get_schedule(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON4_BACK:
        context.bot.send_message(
            chat_id=chat_id,
            text="Вы вернулись назад",
            reply_markup=get_base_inline_keyboard(),
        )
        # help(update=update, context=context)
    elif data == CALLBACK_BUTTON_NEXT_WEEK:
        storage[chat_id]['week_state'] += 1
        if storage[chat_id]['week_state'] > 1:
            storage[chat_id]['week_state'] = 1
        text = 'Расписание за <i>следующую</i> неделю.' \
            if storage[chat_id]['week_state'] == 1 \
            else 'Расписание за <i>текущую</i> неделю.'
        change_buttons(update=update, context=context)
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_schedule(),
        )
    elif data == CALLBACK_BUTTON_PREV_WEEK:
        storage[chat_id]['week_state'] -= 1
        if storage[chat_id]['week_state'] < -1:
            storage[chat_id]['week_state'] = -1
        text = 'Расписание за <i>предыдущую</i> неделю.' \
            if storage[chat_id]['week_state'] == -1 \
            else 'Расписание за <i>текущую</i> неделю.'
        change_buttons(update=update, context=context)
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_schedule(),
        )
    elif data in (CALLBACK_BUTTON5_MONDAY, CALLBACK_BUTTON6_THURSDAY,
                  CALLBACK_BUTTON7_TUESDAY, CALLBACK_BUTTON8_FRIDAY,
                  CALLBACK_BUTTON9_WEDNESDAY, CALLBACK_BUTTON10_SATURDAY):
        schedule = save_schedule(update=update, context=context)
        output = save_formatted_schedule(data, schedule)

        context.bot.send_message(
            chat_id=chat_id,
            text="\n".join(output),
            reply_markup=get_schedule(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        context.bot.send_message(
            chat_id=chat_id,
            text="Скрыл клавиатуру.\n\nНажмите /start чтобы вернуть её обратно",
            reply_markup=ReplyKeyboardRemove(),
        )


def start(update: Update, context: CallbackContext):
    if user_exists(update=update, context=context):
        help(update=update, context=context)
    else:
        update.message.reply_text(
            text="Вы ещё не авторизованы! Для авторизации введите логин и пароль через команду /login"
                 "в формате\n/login login:password",
            reply_markup=get_base_reply_keyboard()
        )


def help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Здесь будет подробная помощь",
        reply_markup=get_base_inline_keyboard()
    )


def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == 'Помощь':
        return help(update=update, context=context)
    elif text.startswith('/login') and text.count('/login') == 1:
        if user_exists(update=update, context=context):
            reply_text = 'Вы уже авторизованы!'
            keyboard = get_base_reply_keyboard()
        else:
            try:
                login, password = text.replace('/login ', '').split(':')
                session = requests.Session()
                auth(session, login, password)
                user = User()
                user.telegram_id = chat_id
                user.name = login
                user.hash = secrets.token_bytes(32)
                user.hashed_password = password_encrypt(password.encode(), user.hash)
                session_db = db_session.create_session()
                session_db.add(user)
                session_db.commit()
                reply_text = 'Успешная авторизация!'
                keyboard = get_base_inline_keyboard()
            except (ValueError, IndexError):
                keyboard = get_base_reply_keyboard()
                reply_text = 'Неверный логин или пароль.'
        update.message.reply_text(
            text=reply_text,
            reply_markup=keyboard
        )


def main():
    # путь до бд
    db_session.global_init('E:\\web-server\\db\\users.sqlite')
    # токен от бота и прокси сервер из файла settings
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
