import requests


def auth(session: requests.Session, login: str, password: str):
    authorization = session.post('https://gym40.eljur.ru/ajaxauthorize',
                                 data={'username': login,
                                       'password': password}).json()
    # вместо принтов ниже оправка сообщений в телеграм
    if authorization['errors']:
        return 'Неверный логин или пароль.'
    elif authorization['actions'][0]['url'].startswith('/?user='):
        return 'Успешная авторизация!'
