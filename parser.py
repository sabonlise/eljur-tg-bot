from methods.authorization import auth
from methods.journal import *
import requests


def main():
    session = requests.Session()
    auth(session, login, password)
    full_journal = get_full_journal_week(session)
    week_days = get_week_days(full_journal)
    journal = get_journal(full_journal)
    print(full_journal, week_days, journal, sep='\n')


if __name__ == '__main__':
    main()
