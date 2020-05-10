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
    lessons = {}
    del journal[0]
    journal = [day.strip() for day in journal]
    for day in range(len(journal)):
        try:
            homework = re.split(r'(?= \d\.[^\d])', journal[day + 1])
            homework = [hw.strip() for hw in homework]
            lessons[journal[day]] = homework
            del journal[day]
        except IndexError:
            pass
    return lessons


def save_formatted_schedule(match_day: str, schedule: dict) -> list:
    day = [day for day in schedule.keys() if match_day in day.lower().split(',')[0]][-1]
    output = [f'Задания за <b>{day.lower()}</b>:']
    lessons = schedule[day]
    if len(lessons) == 1:
        return output + [f'<b>{lessons[0]}</b>']
    else:
        for lesson in lessons:
            time = re.findall(r'\d\d:\d\d–\d\d:\d\d', lesson)
            # todo: фикс в случае непраивльного парсинга по времени
            time = time[0] if time else ''
            lesson = lesson.replace('\n', '\n\t\t\t\t\t').\
                replace('Онлайн-урок завершен', '').replace('Онлайн-урок', '').split(' ')
            order = lesson[0]
            subject = lesson[2].capitalize()
            if len(lesson) in [4, 3] and lesson[1] == time:
                output.append(f'{order}\t   {subject}, {time}:  <b>домашнего задания нет!</b>')
            else:
                homework = ' '.join(lesson[3:])
                if lesson[3] == 'час' or lesson[3] == 'язык':
                    subject = f'{lesson[2].capitalize()} {lesson[3]}'
                    homework = ' '.join(lesson[4:])
                output.append(f'{order}\t   {subject}, {time}:\n'
                              f'\t    📝  {homework}')
        return output
