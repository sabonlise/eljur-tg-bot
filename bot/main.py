import secrets

from telegram import ParseMode
from telegram import ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler

from bot.schedule import *
from bot.keyboard import *
from bot.settings import TOKEN, REQUEST_KWARGS

from methods.authorization import auth
from methods.messages import get_inbox_messages, get_max_pages, get_message_info, get_messages_content
from methods.crypto import password_encrypt

messages_storage = {}


def max_page_user(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    try:
        return messages_storage[chat_id]['max_page']
    except KeyError:
        login, password = get_logpass(update=update, context=context)
        session = requests.Session()
        auth(session, login, password)
        max_pages = get_max_pages(session)
        messages_storage[chat_id]['max_page'] = max_pages
        return messages_storage[chat_id]['max_page']


def save_messages(type: str, update: Update, context: CallbackContext):
    # val 0 = message info
    # val 1 = full message
    if type == 'info':
        val = 0
    elif type == 'full':
        val = 1

    chat_id = update.effective_message.chat_id
    page = messages_storage[chat_id]['page']
    try:
        return messages_storage[chat_id][page][val]
    except KeyError:
        session = requests.Session()
        login, password = get_logpass(update=update, context=context)
        auth(session, login, password)
        messages = get_inbox_messages(session, page=page)
        info = get_message_info(messages)
        content = get_messages_content(messages)
        messages_storage[chat_id][page] = [info[:10]]
        messages_storage[chat_id][page].append(content[:10])
        return messages_storage[chat_id][page][val]


def change_buttons(update: Update, context: CallbackContext):
    schedule = save_schedule(update=update, context=context)
    week_days = list(schedule.keys())
    TITLES[CALLBACK_BUTTON5_MONDAY] = week_days[0]
    TITLES[CALLBACK_BUTTON6_THURSDAY] = week_days[3]
    TITLES[CALLBACK_BUTTON7_TUESDAY] = week_days[1]
    TITLES[CALLBACK_BUTTON8_FRIDAY] = week_days[4]
    TITLES[CALLBACK_BUTTON9_WEDNESDAY] = week_days[2]
    TITLES[CALLBACK_BUTTON10_SATURDAY] = week_days[5]


def user_exists(update: Update, context: CallbackContext):
    session_db = db_session.create_session()
    chat_id = update.effective_message.chat_id
    user = session_db.query(User).filter(User.telegram_id == chat_id).first()
    if user:
        return True
    return False


def get_logpass(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    session_db = db_session.create_session()
    user = session_db.query(User).filter(User.telegram_id == chat_id).first()
    login = user.name
    key = user.hash
    password = password_decrypt(user.hashed_password, key).decode()
    return login, password


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
            reply_markup=get_base_inline_keyboard()
        )
    elif data == CALLBACK_BUTTON2_SKIPS:
        # тут будет информация о пропусках
        context.bot.send_message(
            chat_id=chat_id,
            text="Пропуски за текущий период:",
            reply_markup=get_base_inline_keyboard()
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
            reply_markup=get_base_inline_keyboard()
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
            text='\n'.join(text),
            parse_mode=ParseMode.HTML,
            reply_markup=get_schedule()
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
            text='\n'.join(text),
            parse_mode=ParseMode.HTML,
            reply_markup=get_schedule()
        )
    elif data == CALLBACK_BUTTON_MESSAGES:
        messages_storage[chat_id] = {'page': 1}
        info = save_messages('info', update=update, context=context)
        max_page = max_page_user(update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>1/{max_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_PREV_PAGE:
        messages_storage[chat_id]['page'] -= 1
        max_page = max_page_user(update=update, context=context)
        if messages_storage[chat_id]['page'] < 1:
            messages_storage[chat_id]['page'] = 1
        info = save_messages('info', update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>{messages_storage[chat_id]['page']}/{max_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_NEXT_PAGE:
        max_page = max_page_user(update=update, context=context)
        messages_storage[chat_id]['page'] += 1
        if messages_storage[chat_id]['page'] > max_page:
            messages_storage[chat_id]['page'] = max_page
        info = save_messages('info', update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>{messages_storage[chat_id]['page']}/{max_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data in (CALLBACK_BUTTON_PAGE1, CALLBACK_BUTTON_PAGE2,
                  CALLBACK_BUTTON_PAGE3, CALLBACK_BUTTON_PAGE4,
                  CALLBACK_BUTTON_PAGE5, CALLBACK_BUTTON_PAGE6,
                  CALLBACK_BUTTON_PAGE7, CALLBACK_BUTTON_PAGE8,
                  CALLBACK_BUTTON_PAGE9, CALLBACK_BUTTON_PAGE10):
        content = save_messages('full', update=update, context=context)
        output = content[int(data) - 1]
        context.bot.send_message(
            chat_id=chat_id,
            text=output,
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
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
            reply_markup=ReplyKeyboardRemove()
        )


def start(update: Update, context: CallbackContext):
    if user_exists(update=update, context=context):
        help(update=update, context=context)
    else:
        update.message.reply_text(
            text="Вы ещё не авторизованы! Для авторизации введите логин и пароль через команду /login "
                 "в формате\n/login <login> <password>",
            reply_markup=get_base_reply_keyboard()
        )


def help(update: Update, context: CallbackContext):
    update.message.reply_text(
        text="Доступные команды:\n"
             "/login <login> <password> - авторизация.\n"
             "/relogin <password> <password again> - смена пароля в боте если вы сменили пароль в элжуре.\n\n"
             "Кнопки:\n"
             "📩 Сообщения - входящие сообщения.\n"
             "🎓 Оценки - Ваши оценки за текущий период.\n"
             "📖 Дневник - Домашние задания за предыдущую, текущую и следующую неделю по всем предметам.\n"
             "❌ Пропуски - Ваши пропуски за текущий период.",
        reply_markup=get_base_inline_keyboard()
    )


def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == 'Помощь':
        return help(update=update, context=context)
    elif text == 'Контакты':
        update.message.reply_text(text='Связь с разработчиками: @millionware и @ZERoN11')
    elif text.startswith('/login'):
        if user_exists(update=update, context=context):
            reply_text = 'Вы уже авторизованы! Если вы сменили пароль, ты повторите процедуру через ' \
                         'команду /relogin.\n\t\t\t' \
                         '/relogin <password> <password again>'
            keyboard = get_base_reply_keyboard()
        else:
            try:
                logpass = text.split()
                login, password = logpass[1], logpass[2]
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
            reply_markup=keyboard,
        )
    elif text.startswith('/relogin'):
        if not user_exists(update=update, context=context):
            reply_text = 'Вы не можете использовать эту команду, так как не авторизовывались ранее.'
            keyboard = get_base_reply_keyboard()
        else:
            try:
                session_db = db_session.create_session()
                password = text.split()
                password1, password2 = password[1], password[2]
                assert password1 == password2, 'Пароли не совпадают!'
                session = requests.Session()
                user = session_db.query(User).filter(User.telegram_id == chat_id).first()
                old_password = password_decrypt(user.hashed_password, user.hash).decode()
                if old_password == password2:
                    reply_text = 'Новый пароль не отличается от старого :('
                    keyboard = get_base_reply_keyboard()
                else:
                    auth(session, user.name, password1)
                    user.hash = secrets.token_bytes(32)
                    user.hashed_password = password_encrypt(password1.encode(), user.hash)
                    session_db.commit()
                    reply_text = 'Пароль успешно изменен!'
                    keyboard = get_base_inline_keyboard()
            except AssertionError as e:
                keyboard = get_base_reply_keyboard()
                reply_text = e.args[0]
            except (ValueError, IndexError):
                keyboard = get_base_reply_keyboard()
                reply_text = 'Неверный пароль.'
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
