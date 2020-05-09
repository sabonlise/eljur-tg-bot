from datetime import datetime
from bs4 import BeautifulSoup
import requests


def get_correct_month():
    month = str(datetime.now().month)
    if len(month) == 1:
        month = f'0{month}'
    return month


def get_current_tests(session: requests.Session) -> list:
    testings = session.get(f'https://gym40.eljur.ru/journal-cw-ajax-action'
                           f'?method=getByStudentId&1={get_user_id(session)}'
                           f'&2=2020-01-13&3=2020-05-29&4=').json()
    date = f'{datetime.now().year}-{get_correct_month()}'
    tests = []
    for test in testings['rows']:
        if date in test['date']:
            tests.append(f'{test["date"]}: {test["header"]} по предмету {test["title"]}')

    if not tests:
        tests = ['Контрольных работ за текущий месяц не найдено!']

    return tests


def get_user_id(session: requests.Session) -> int:
    journal = session.get('https://gym40.eljur.ru/journal-app')
    soup = BeautifulSoup(journal.text, 'lxml')
    nav_tabs = soup.find('div', {'id': 'navigation-tabs'})
    buttons = nav_tabs.find_all('a')
    user_id = buttons[0].get('href').split('/')[-1].split('.')[1]
    return int(user_id)
