import requests
from bs4 import BeautifulSoup


def get_misses(session: requests.Session) -> dict:
    r = session.get('https://gym40.eljur.ru/journal-app/view.miss_report')
    soup = BeautifulSoup(r.content, 'lxml')
    miss = {}
    subjects = soup.find_all('td', {'class': 'text-left'})
    del subjects[0]
    illness = soup.find_all('td', {'data-reason': 'b'})
    respectfully = soup.find_all('td', {'data-reason': 'u'})
    disrespectfully = soup.find_all('td', {'data-reason': 'n'})
    for i in range(len(subjects)):
        misses_list = [illness[i].text, respectfully[i].text, disrespectfully[i].text]
        subject = str(subjects[i]).replace('<td class="text-left">', '').replace('</td>', '').strip()
        if not subject:
            subject = '\nВсего:'
        miss[subject] = misses_list
    return miss
