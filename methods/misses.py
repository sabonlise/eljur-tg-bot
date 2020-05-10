import requests
from bs4 import BeautifulSoup
from methods.authorization import auth

s = requests.Session()


def misses(session: requests.Session, login, password) -> dict:
    auth(session, login, password)
    r = session.get('https://gym40.eljur.ru/journal-app/view.miss_report/&mode=excel')
    soup = BeautifulSoup(r.content)
    miss = {}
    subjects = soup.find_all('td', {'class': 'text-left'})[1:]
    illness = soup.find_all('td', {'class': 'green miss_detail'})
    respectfully = soup.find_all('td', {'class': 'lblue miss_detail'})
    disrespectfully = soup.find_all('td', {'class': 'red miss_detail'})
    for i in range(len(subjects)):
        mss = [str(illness[i]).replace('<td class="green miss_detail" data-reason="b">', '').replace('</td>', ''),
               str(respectfully[i]).replace('<td class="lblue miss_detail" data-reason="u">', '').replace('</td>', ''),
               str(disrespectfully[i]).replace('<td class="red miss_detail" data-reason="n">', '').replace('</td>', '')]
        miss[str(subjects[i]).replace('<td class="text-left">', '').replace('</td>', '')] = mss
    return miss