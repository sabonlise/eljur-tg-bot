from methods.journal import *


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
