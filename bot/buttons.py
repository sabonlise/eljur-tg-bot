from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup


BUTTON1_HELP = "Помощь"
BUTTON2 = "Кнопка"


def get_base_reply_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON1_HELP),
            KeyboardButton(BUTTON2),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
