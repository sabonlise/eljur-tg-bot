from methods.authorization import auth
from bs4 import BeautifulSoup
import requests
import re


def get_full_journal_week(session: requests.Session):
    journal_app = session.get('https://gym40.eljur.ru/journal-app')
    soup = BeautifulSoup(journal_app.text, 'lxml')
    journal = soup.find('div', id='dnevnikDays').text.split()
    return journal


def get_week_days(journal: list):
    days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']
    week_days = []
    for lesson_day in range(len(journal)):
        for day in days:
            if journal[lesson_day].lower().startswith(day):
                week_days.append(f'{journal[lesson_day]} {journal[lesson_day + 1]}')
    return week_days


# testing regexp
def get_journal(journal: list) -> list:
    return re.split(r' [1-9][.]', ' '.join(journal))
