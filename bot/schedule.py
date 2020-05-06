import re
import requests

from methods.crypto import password_decrypt, password_encrypt
from methods.journal import *

from telegram.ext import CallbackContext
from telegram import Update
from data import db_session
from data.users import User

storage = {}


def save_schedule(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    state = storage[chat_id]['week_state']
    try:
        return storage[chat_id][state]
    except KeyError:
        session_db = db_session.create_session()
        user = session_db.query(User).filter(User.telegram_id == chat_id).first()
        session = requests.Session()
        login = user.name
        key = user.hash
        password = password_decrypt(user.hashed_password, key).decode()
        auth(session, login, password)
        prev_week = get_full_journal_week(session, -1)
        next_week = get_full_journal_week(session, 1)
        current_week = get_full_journal_week(session)
        storage[chat_id][-1] = get_lessons(prev_week)
        storage[chat_id][1] = get_lessons(next_week)
        storage[chat_id][0] = get_lessons(current_week)
        return storage[chat_id][state]


def save_formatted_schedule(match_day, schedule):
    day = [day for day in schedule.keys() if match_day in day.lower().split(',')[0]][-1]
    output = [f'Задания за <b>{day.lower()}</b>:']
    lessons = schedule[day]
    print(lessons)
    if len(lessons) == 1:
        return output + [f'<b>{lessons[0]}</b>']
    else:
        for lesson in lessons:
            time = re.findall(r'\d\d:\d\d–\d\d:\d\d', lesson)
            # todo: фикс в случае непраивльного парсинга по времени
            time = time[0] if time else 'оп ахах)'
            print(time)
            lesson = lesson.split()
            order = lesson[0]
            subject = lesson[2].capitalize()
            if len(lesson) in [4, 3] and lesson[1] == time:
                output.append(f'{order}\t   {subject}, {time} ⏰:  <b>домашнего задания нет!</b>')
            else:
                homework = ' '.join(lesson[3:])
                output.append(f'{order}\t   {subject}, {time} ⏰:\n'
                              f'\t    📝  {homework}')
        return output
