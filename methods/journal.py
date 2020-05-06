from bs4 import BeautifulSoup
import requests
import re


def get_full_journal_week(session: requests.Session, week=0) -> list:
    """Получить содержимое дневника за неделю,
       указанную в параметре week (по умолчанию текущая неделя)
       week = -1  дневник за предыдущую неделю
       week = 1   дневник за следующую неделю"""
    if not week:
        journal_app = session.get('https://gym40.eljur.ru/journal-app')
    else:
        journal_app = session.get(f'https://gym40.eljur.ru/journal-app/week.{-int(week)}')
    soup = BeautifulSoup(journal_app.text, 'lxml')
    for br in soup.find_all('br'):
        br.replace_with('breakline_key')
    journal = soup.find('div', id='dnevnikDays').text.split()
    journal = [element.replace('breakline_key', '\n') for element in journal]
    return journal


def get_week_days(journal: list) -> list:
    return re.findall(r'\w+, \d{2}\.\d{2}', ' '.join(journal))


def get_lessons(full_journal: list) -> dict:
    journal = re.split(r'(\w+, \d{2}\.\d{2})', ' '.join(full_journal))
    print(1, journal)
    lessons = {}
    del journal[0]
    journal = [day.strip() for day in journal]
    for day in range(len(journal)):
        try:
            homework = re.split(r'(?= \d\.[^\d])', journal[day + 1])
            homework = [hw.strip() for hw in homework]
            lessons[journal[day]] = homework
            del journal[day]
        except IndexError as IE:
            pass
    return lessons
