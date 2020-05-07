from math import ceil
import requests


def get_inbox_messages(session: requests.Session, page=1) -> list:
    """Возвращает сообщения в полном виде"""
    # 3 = offset (+20 for next page)
    messages = session.get(f'https://gym40.eljur.ru/journal-messages-ajax-action?'
                           f'method=getList&0=inbox&1=&2=&3={(page - 1) * 20}&4=0&5=&6=&7=0')
    msg = messages.json()
    return msg['list']


def get_max_pages(session: requests.Session) -> int:
    """Возвращает максимальное количество страниц сообщений пользоваеля"""
    response = session.get('https://gym40.eljur.ru/journal-messages-ajax-action?'
                           'method=getList&0=inbox').json()
    pages = response['pager']['total']
    max_pages = ceil(pages / 20)
    return max_pages


def get_message_info(messages: list) -> list:
    """Возвращает список с краткой информацией
       о сообщении"""
    info = []
    for order, message in enumerate(messages):
        subject = message['subject']
        date = message['messageDateHuman']
        sender = message['fromUserHuman']
        result = f'{order + 1}. {subject} (отправлено {date}),' \
                 f'\n\tот {sender}'
        info.append(result)
    return info


def get_messages_content(messages: list) -> list:
    """Отправитель: ...
       Дата: ...
       Сообщение: ...

       Файлы"""
    content = []
    for message in messages:
        message_files = ''
        if message['hasFiles']:
            files = message['files']
            for file in files:
                message_files += f'📌 <a href=\"{file["url"]}\">' \
                                 f'{file["filename"]}</a>'
                # message_files += f'Файл: {file["filename"]}. Ссылка: {file["url"]}\n'
        sender = message['fromUserHuman']
        subject = message['subject']
        full_date = message['msg_date'].split()
        date = full_date[0].split('-')
        date = f'{date[2]}.{date[1]}.{date[0]} {full_date[1]}'
        msg = message['body']
        content.append(f'<b>Тема:</b> {subject}\n'
                       f'<b>Отправитель:</b> {sender}\n'
                       f'<b>Дата:</b> {date}\n\n'
                       f'<strong>Сообщение:</strong>\n'
                       f'<code>{msg}</code>\n'
                       f'{message_files}\n')
    return content
