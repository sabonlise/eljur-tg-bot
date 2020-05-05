from methods.authorization import auth
from methods.journal import *
import requests
import re


def main():
    session = requests.Session()
    auth(session, 'login', 'password')
    full_journal = get_full_journal_week(session, -1)
    # week_days = get_week_days(full_journal)
    lessons_dictionary = get_lessons(full_journal)
    day = ''     # день, который введет пользователь
    for days, lessons in lessons_dictionary.items():
        days = days.lower()
        if day in days:
            print(f'Расписание за {days}:')
            for lesson in lessons:
                print(lesson)


if __name__ == '__main__':
    main()
