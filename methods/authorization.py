import requests


def auth(session: requests.Session, login: str, password: str):
    authorization = session.post('https://gym40.eljur.ru/ajaxauthorize',
                                 data={'username': login,
                                       'password': password}).json()
    # отправка сообщений в тг в зависмости от результата ниже
    """if authorization['errors']:
        raise Exception('Неверный логин или пароль.')"""
    if authorization['actions'][0]['url'].startswith('/?user='):
        print('Успешная авторизация.')
    """else IndexError"""
