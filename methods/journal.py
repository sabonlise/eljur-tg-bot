from methods.authorization import auth
from bs4 import BeautifulSoup
import requests
import re
import codecs


def read_file(filename):
    fileObj = codecs.open(filename, "r", "utf_8_sig")
    text = fileObj.read()
    return text


def get_full_journal_week(session: requests.Session, week=None):
    """Получить содержимое дневника за неделю,
       указанную в параметре week (по умолчанию текущая неделя)
       week = -1  дневник за предыдущую неделю
       week = 1   дневник за следующую неделю"""
    # journal_app = read_file('methods/prev_week.txt')
    # soup = BeautifulSoup(journal_app, 'lxml')
    if not week:
        journal_app = session.get('https://gym40.eljur.ru/journal-app')
    else:
        journal_app = session.get(f'https://gym40.eljur.ru/journal-app/week.{-int(week)}')
    soup = BeautifulSoup(journal_app.text, 'lxml')
    journal = soup.find('div', id='dnevnikDays').text.split()
    return journal


def get_week_days(journal: list):
    return re.findall(r'\w+, \d{2}\.\d{2}', ' '.join(journal))


def get_lessons(full_journal: list) -> dict:
    journal = re.split(r'(\w+, \d{2}\.\d{2})', ' '.join(full_journal))
    lessons = {}
    del journal[0]
    journal = [day.strip() for day in journal]
    for day in range(len(journal)):
        try:
            homework = re.split(r'(?= \d\.)', journal[day + 1])
            homework = [hw.strip() for hw in homework]
            lessons[journal[day]] = homework
            journal.pop(day)
            # del journal[day]
        except IndexError as IE:
            pass
    return lessons
