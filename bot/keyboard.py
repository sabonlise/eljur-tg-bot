from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from bot.settings import CHAT_URL


BUTTON1_HELP = "Помощь"
BUTTON2_CONTACTS = "Контакты"

CALLBACK_BUTTON_PAGE1 = '1.'
CALLBACK_BUTTON_PAGE2 = '2.'
CALLBACK_BUTTON_PAGE3 = '3.'
CALLBACK_BUTTON_PAGE4 = '4.'
CALLBACK_BUTTON_PAGE5 = '5.'
CALLBACK_BUTTON_PAGE6 = '6.'
CALLBACK_BUTTON_PAGE7 = '7.'
CALLBACK_BUTTON_PAGE8 = '8.'
CALLBACK_BUTTON_PAGE9 = '9.'
CALLBACK_BUTTON_PAGE10 = '10.'
CALLBACK_BUTTON_HIDE_KEYBOARD = "callback_button_hide"
CALLBACK_BUTTON_PREV_WEEK = 'callback_button_prev_week'
CALLBACK_BUTTON_NEXT_WEEK = 'callback_button_next_week'
CALLBACK_BUTTON_PREV_PAGE = 'callback_button_prev_page'
CALLBACK_BUTTON_NEXT_PAGE = 'callback_button_next_page'
CALLBACK_BUTTON_MESSAGES = 'callback_button_messages'
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
    CALLBACK_BUTTON_MESSAGES: "Сообщения ",
    CALLBACK_BUTTON_PREV_WEEK: "⬅️",
    CALLBACK_BUTTON_NEXT_WEEK: "➡️",
}


def get_messages_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE1], callback_data=CALLBACK_BUTTON_PAGE1),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE2], callback_data=CALLBACK_BUTTON_PAGE2),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE3], callback_data=CALLBACK_BUTTON_PAGE3),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE4], callback_data=CALLBACK_BUTTON_PAGE4),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE5], callback_data=CALLBACK_BUTTON_PAGE5),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE6], callback_data=CALLBACK_BUTTON_PAGE6),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE7], callback_data=CALLBACK_BUTTON_PAGE7),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE8], callback_data=CALLBACK_BUTTON_PAGE8),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PREV_WEEK], callback_data=CALLBACK_BUTTON_PREV_PAGE),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE9], callback_data=CALLBACK_BUTTON_PAGE9),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_PAGE10], callback_data=CALLBACK_BUTTON_PAGE10),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_NEXT_WEEK], callback_data=CALLBACK_BUTTON_NEXT_PAGE)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_base_reply_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON1_HELP),
            KeyboardButton(BUTTON2_CONTACTS)
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


def get_base_inline_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON1_MARKS], callback_data=CALLBACK_BUTTON1_MARKS),
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON2_SKIPS], callback_data=CALLBACK_BUTTON2_SKIPS),
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON3_SCHEDULE], callback_data=CALLBACK_BUTTON3_SCHEDULE),
            InlineKeyboardButton('Чат', url=CHAT_URL)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_MESSAGES], callback_data=CALLBACK_BUTTON_MESSAGES)
        ],
        [
            InlineKeyboardButton(TITLES[CALLBACK_BUTTON_HIDE_KEYBOARD], callback_data=CALLBACK_BUTTON_HIDE_KEYBOARD),
        ]
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
