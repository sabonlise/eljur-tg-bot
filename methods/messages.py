from math import ceil
import requests


def get_all_messages(session: requests.Session, page=1, part=1, msg_type='inbox') -> list:
    """Возвращает сообщения в полном виде
        3 = offset (+20 for next page)
        type = inbox - полученные сообщения
        type = sent - отправленные сообщения"""
    messages = session.get(f'https://gym40.eljur.ru/journal-messages-ajax-action?'
                           f'method=getList&0={msg_type}&1=&2=&3={(page - 1) * 20}&4=0&5=&6=&7=0')
    msg = messages.json()
    return msg['list'][(part - 1) * 10:part * 10]


def get_max_pages(session: requests.Session, msg_type='inbox') -> tuple:
    """Возвращает максимальное количество страниц сообщений пользоваеля"""
    response = session.get(f'https://gym40.eljur.ru/journal-messages-ajax-action?'
                           f'method=getList&0={msg_type}').json()
    pages = response['pager']['total']
    max_part_page, max_page = ceil(int(pages) / 10), ceil(int(pages) / 20)
    return max_part_page, max_page


def get_messages_info(messages: list, msg_type: str) -> list:
    """Возвращает список с краткой информацией
       о сообщениях"""
    assert msg_type == 'sent' or msg_type == 'inbox'
    info = []
    for order, message in enumerate(messages):
        subject = message['subject']
        date = message['messageDateHuman']
        result = ''
        if msg_type == 'inbox':
            sender = message['fromUserHuman']
            result += f'{order + 1}. <b>{subject}</b> (отправлено {date}), \t<i>{sender}</i>'
        elif msg_type == 'sent':
            recipients = message['recipientsHuman']
            if isinstance(recipients, list):
                recipients = 'получатели: ' + ', '.join(recipients)
            else:
                recipients = 'получатель: ' + recipients
            result += f'{order + 1}. <b>{subject}</b> (отправлено {date}), \t<i>{recipients}</i>'
        info.append(result)
    return info


def get_messages_content(messages: list, msg_type: str) -> list:
    """Отправитель: ...
       Дата: ...
       Сообщение: ...

       Файлы"""
    assert msg_type == 'sent' or msg_type == 'inbox'
    content = []
    for message in messages:
        message_files = ''
        if message['hasFiles']:
            files = message['files']
            for file in files:
                message_files += f'📌 <a href=\"{file["url"]}\">' \
                                 f'{file["filename"]}</a>\n'
                # <a href ="url">description</a>
        if msg_type == 'inbox':
            recipients = f"<b>Отправитель:</b> {message['fromUserHuman']}"
        elif msg_type == 'sent':
            recipients = message['recipientsHuman']
            if isinstance(recipients, list):
                recipients = '<b>Получатели:</b> ' + ', '.join(recipients)
            else:
                recipients = '<b>Получатель:</b> ' + recipients
        subject = message['subject']
        full_date = message['msg_date'].split()
        date = full_date[0].split('-')
        date = f'{date[2]}.{date[1]}.{date[0]} {full_date[1]}'
        msg = message['body']
        if message_files:
            content.append(f'<b>Тема:</b> {subject}\n'
                           f'{recipients}\n'
                           f'<b>Дата:</b> {date}\n\n'
                           f'<strong>Сообщение:</strong>\n'
                           f'<code>{msg}</code>\n\n'
                           f'Файлы:\n{message_files}')
        else:
            content.append(f'<b>Тема:</b> {subject}\n'
                           f'{recipients}\n'
                           f'<b>Дата:</b> {date}\n\n'
                           f'<strong>Сообщение:</strong>\n'
                           f'<code>{msg}</code>\n\n')
    return content
