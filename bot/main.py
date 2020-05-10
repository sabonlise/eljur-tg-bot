import secrets
import requests
from sqlalchemy            import exc

from telegram              import Update
from telegram              import ParseMode
from telegram.ext          import Filters
from telegram.ext          import Updater
from telegram.ext          import CommandHandler
from telegram.ext          import MessageHandler
from telegram.ext          import CallbackContext
from telegram              import ReplyKeyboardRemove
from telegram.ext          import CallbackQueryHandler

from data                  import db_session
from data.users            import User

from bot.keyboard          import *
from bot.settings          import TOKEN
from bot.settings          import REQUEST_KWARGS

from methods.marks         import mark_parse
from methods.misses        import get_misses
from methods.marks         import get_average
from methods.authorization import auth
from methods.journal       import get_lessons
from methods.messages      import get_max_pages
from methods.crypto        import password_decrypt
from methods.crypto        import password_encrypt
from methods.marks         import get_correct_marks
from methods.messages      import get_all_messages
from methods.messages      import get_messages_info
from methods.testings      import get_current_tests
from methods.journal       import get_full_journal_week
from methods.messages      import get_messages_content
from methods.journal       import save_formatted_schedule


messages_storage = {}
user_storage = {}
tests_storage = {}
storage = {}


def save_misses(update: Update, context: CallbackContext):
    """Вывод пропусков 'в виде таблицы'"""
    session = get_session(update=update, context=context)

    formatted = ''
    misses_dictionary = get_misses(session)

    for subject, misses in misses_dictionary.items():
        misses = '\t\t\t\t '.join(misses)
        if not subject[0].isupper():
            subject = subject.capitalize()
        formatted += "{0:<30} {1}".format(subject.capitalize(), misses) + "\n"

    table = 'Б\t\t\t\t У\t\t\t\t Н'.rjust(44, ' ') + '\n'

    return table + formatted


def get_marks(update: Update, context: CallbackContext):
    """Получение оценок в отформатированном виде"""
    session = get_session(update=update, context=context)

    marks = mark_parse(session)
    current_marks = get_correct_marks(marks)
    subjects = list(current_marks.keys())
    max_subject_len = max(list(map(len, subjects)))
    output = []

    for subject, marks in current_marks.items():
        if marks:
            average = get_average(marks)
            marks = '\t'.join(marks)
            subject = subject.ljust(max_subject_len, ' ')
            output.append(f'<b>{subject.capitalize()}</b> '
                          f'(ср. балл <b>{average}</b>):\n'
                          f'<code>{marks}</code>\n')

    return output


def max_page_user(update: Update, context: CallbackContext) -> tuple:
    """Получение количества страниц сообщений пользователя
       разделённых по частям и с оригинальным оффсетом"""
    chat_id = update.effective_message.chat_id
    msg_type = messages_storage[chat_id]['msg_type']

    try:
        return messages_storage[chat_id]['max_part_page'], messages_storage[chat_id]['max_page']
    except KeyError:
        session = get_session(update=update, context=context)
        max_part_page, max_page = get_max_pages(session, msg_type)
        messages_storage[chat_id]['max_page'] = max_page
        messages_storage[chat_id]['max_part_page'] = max_part_page
        return messages_storage[chat_id]['max_part_page'], messages_storage[chat_id]['max_page']


def get_session(update: Update, context: CallbackContext):
    """Получение текущей пользовательской сессии"""
    chat_id = update.effective_message.chat_id
    try:
        return user_storage[chat_id]['session']
    except KeyError:
        session = requests.Session()
        login, password = get_logpass(update=update, context=context)
        auth(session, login, password)
        user_storage[chat_id]['session'] = session
        return user_storage[chat_id]['session']


def save_schedule(update: Update, context: CallbackContext) -> dict:
    """Сохранение дневника в глобальном словаре"""
    chat_id = update.effective_message.chat_id
    state = storage[chat_id]['week_state']
    try:
        return storage[chat_id][state]
    except KeyError:
        session = get_session(update=update, context=context)

        prev_week = get_full_journal_week(session, -1)
        next_week = get_full_journal_week(session, 1)
        current_week = get_full_journal_week(session)

        storage[chat_id][-1] = get_lessons(prev_week)
        storage[chat_id][1] = get_lessons(next_week)
        storage[chat_id][0] = get_lessons(current_week)

        return storage[chat_id][state]


def save_messages(type: str, update: Update, context: CallbackContext) -> list:
    """Сохранение сообщений на текущей странице в глобальном словаре"""
    # val 0 = message info
    # val 1 = full message
    if type == 'info':
        val = 0
    elif type == 'full':
        val = 1

    chat_id = update.effective_message.chat_id
    page = messages_storage[chat_id]['page']
    part = messages_storage[chat_id]['part']

    session = get_session(update=update, context=context)

    msg_type = messages_storage[chat_id]['msg_type']
    messages = get_all_messages(session, page=page, part=part, msg_type=msg_type)
    info = get_messages_info(messages, msg_type=msg_type)
    content = get_messages_content(messages, msg_type=msg_type)

    messages_storage[chat_id][page] = [info]
    messages_storage[chat_id][page].append(content)

    return messages_storage[chat_id][page][val]


def change_buttons(update: Update, context: CallbackContext) -> None:
    """Смена кнопок дней при открытии дневника"""
    schedule = save_schedule(update=update, context=context)
    week_days = list(schedule.keys())

    TITLES[CALLBACK_BUTTON5_MONDAY] = week_days[0]
    TITLES[CALLBACK_BUTTON6_THURSDAY] = week_days[3]
    TITLES[CALLBACK_BUTTON7_TUESDAY] = week_days[1]
    TITLES[CALLBACK_BUTTON8_FRIDAY] = week_days[4]
    TITLES[CALLBACK_BUTTON9_WEDNESDAY] = week_days[2]
    TITLES[CALLBACK_BUTTON10_SATURDAY] = week_days[5]


def user_exists(update: Update, context: CallbackContext):
    """Проверка на то, существует ли уже юзер в бд"""
    session_db = db_session.create_session()
    chat_id = update.effective_message.chat_id
    user = session_db.query(User).filter(User.telegram_id == chat_id).first()
    return bool(user)


def get_logpass(update: Update, context: CallbackContext) -> tuple:
    chat_id = update.effective_message.chat_id

    session_db = db_session.create_session()
    user = session_db.query(User).filter(User.telegram_id == chat_id).first()
    login = user.name
    key = user.hash
    password = password_decrypt(user.hashed_password, key).decode()
    return login, password


def keyboard_callback_handler(update: Update, context: CallbackContext):
    """Обработка кнопок со всех клавиатур"""
    chat_id = update.effective_message.chat_id

    query = update.callback_query
    data = query.data

    current_text = update.effective_message.text

    if chat_id not in user_storage:
        user_storage[chat_id] = {}

    if data == CALLBACK_BUTTON1_MARKS:
        # получение информации об оценках
        marks = get_marks(update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text="\n".join(marks),
            reply_markup=get_base_inline_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON2_SKIPS:
        # получение информации о пропусках
        misses = save_misses(update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text="```" + misses + "```",
            reply_markup=get_base_inline_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    elif data == CALLBACK_BUTTON_TESTS:
        # получение графика контрольных работ за текущий месяц
        session = get_session(update=update, context=context)
        tests = get_current_tests(session)
        context.bot.send_message(
            chat_id=chat_id,
            text='\n'.join(tests),
            reply_markup=get_base_inline_keyboard()
        )
    elif data == CALLBACK_BUTTON3_SCHEDULE:
        # получение дневника с домашнем заданием
        storage[chat_id] = {'week_state': 0}
        change_buttons(update=update, context=context)
        query.edit_message_text(
            text='Расписание за <i>текущую</i> неделю.',
            reply_markup=get_schedule(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON4_BACK:
        # кнопка возврата на главную клавиатуру
        context.bot.send_message(
            chat_id=chat_id,
            text="Вы вернулись назад.",
            reply_markup=get_base_inline_keyboard()
        )
    elif data == CALLBACK_BUTTON_NEXT_WEEK:
        # предыдущая неделя в дневнике
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
            reply_markup=get_schedule()
        )
    elif data == CALLBACK_BUTTON_PREV_WEEK:
        # следующая неделя в дневнике
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
            reply_markup=get_schedule()
        )
    elif data == CALLBACK_BUTTON_MESSAGES:
        # выбор типа сообщений
        context.bot.send_message(
            chat_id=chat_id,
            text='Выберите тип сообщений',
            reply_markup=get_messages_type_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
    elif data == CALLBACK_BUTTON_INBOX:
        # получение входящих сообщений
        messages_storage[chat_id] = {'page': 1, 'part': 1, 'msg_type': 'inbox'}

        info = save_messages('info', update=update, context=context)
        max_page, _ = max_page_user(update=update, context=context)

        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>1/{max_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_SENT:
        # получение исходящих сообщений
        messages_storage[chat_id] = {'page': 1, 'part': 1, 'msg_type': 'sent'}

        info = save_messages('info', update=update, context=context)
        max_page, _ = max_page_user(update=update, context=context)

        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>1/{max_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_PREV_PAGE:
        # предыдущая страница сообщений
        messages_storage[chat_id]['part'] -= 1
        if messages_storage[chat_id]['part'] < 1:
            messages_storage[chat_id]['part'] = 2
            messages_storage[chat_id]['page'] -= 1

        max_part_page, max_page = max_page_user(update=update, context=context)
        current_page = messages_storage[chat_id]['page'] * 2 + (messages_storage[chat_id]['part'] - 2)
        if current_page < 1:
            messages_storage[chat_id]['page'] = max_page
            if max_part_page % 2:
                messages_storage[chat_id]['part'] = 1
            else:
                messages_storage[chat_id]['part'] = 2
            current_page = max_part_page

        info = save_messages('info', update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>{current_page}/{max_part_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_NEXT_PAGE:
        # следующая страница сообщений
        messages_storage[chat_id]['part'] += 1
        if messages_storage[chat_id]['part'] > 2:
            messages_storage[chat_id]['part'] = 1
            messages_storage[chat_id]['page'] += 1

        max_part_page, max_page = max_page_user(update=update, context=context)
        current_page = messages_storage[chat_id]['page'] * 2 + (messages_storage[chat_id]['part'] - 2)
        if current_page > max_part_page:
            messages_storage[chat_id]['page'] = 1
            messages_storage[chat_id]['part'] = 1
            current_page = 1

        info = save_messages('info', update=update, context=context)
        context.bot.send_message(
            chat_id=chat_id,
            text=f"Страница "
                 f"<b>{current_page}/{max_part_page}</b>\n" + "\n".join(info),
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data in (CALLBACK_BUTTON_PAGE1, CALLBACK_BUTTON_PAGE2,
                  CALLBACK_BUTTON_PAGE3, CALLBACK_BUTTON_PAGE4,
                  CALLBACK_BUTTON_PAGE5, CALLBACK_BUTTON_PAGE6,
                  CALLBACK_BUTTON_PAGE7, CALLBACK_BUTTON_PAGE8,
                  CALLBACK_BUTTON_PAGE9, CALLBACK_BUTTON_PAGE10):
        # получение полной информации о сообщении
        content = save_messages('full', update=update, context=context)

        try:
            output = content[int(data) - 1]
        except IndexError:
            output = 'Сообщение не найдено!'

        context.bot.send_message(
            chat_id=chat_id,
            text=output,
            reply_markup=get_messages_keyboard(),
            parse_mode=ParseMode.HTML
        )

    elif data in (CALLBACK_BUTTON5_MONDAY, CALLBACK_BUTTON6_THURSDAY,
                  CALLBACK_BUTTON7_TUESDAY, CALLBACK_BUTTON8_FRIDAY,
                  CALLBACK_BUTTON9_WEDNESDAY, CALLBACK_BUTTON10_SATURDAY):
        # получение дневника за конкретный день
        schedule = save_schedule(update=update, context=context)
        output = save_formatted_schedule(data, schedule)

        context.bot.send_message(
            chat_id=chat_id,
            text="\n".join(output),
            reply_markup=get_schedule(),
            parse_mode=ParseMode.HTML
        )
    elif data == CALLBACK_BUTTON_HIDE_KEYBOARD:
        # скрытие клавиатуры
        query.edit_message_text(
            parse_mode=ParseMode.HTML,
            reply_markup=get_base2_inline_keyboard(),
            text="Клавиатура скрыта."
        )
        context.bot.send_message(
            chat_id=chat_id,
            text="Клавиатура скрыта.",
            reply_markup=ReplyKeyboardRemove()
        )
    elif data == CALLBACK_BUTTON_RETURN_KEYBOARD:
        # возврат клавиатуры
        query.edit_message_text(
            parse_mode=ParseMode.HTML,
            reply_markup=get_base_inline_keyboard(),
            text="Клавиатура возвращена."
        )
        context.bot.send_message(
            chat_id=chat_id,
            text="Клавиатура возвращена.",
            reply_markup=get_base_reply_keyboard()
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
        text=HELP,
        reply_markup=get_base_inline_keyboard()
    )


def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    if text == 'Помощь':
        return help(update=update,
                    context=context)
    elif text == 'Контакты':
        update.message.reply_text(text='Связь с разработчиками: @millionware и @ZERoN11')
    elif text.startswith('/login'):
        # первичная авторизация пользователя
        if user_exists(update=update,
                       context=context):
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
        # смена пароля в случае если пользователь поменял его в электронном дневнике
        if not user_exists(update=update,
                           context=context):
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
            reply_markup=keyboard,
        )


def main():
    # путь до папки с бд (сама бд создастся автоматически)
    try:
        db_session.global_init('..\\db\\users.sqlite')
    except exc.OperationalError:
        print('Указан неверный путь к папке с базой данных.')
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
