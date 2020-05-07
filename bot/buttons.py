from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup


BUTTON1_HELP = "Помощь"


def get_base_reply_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON1_HELP),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
