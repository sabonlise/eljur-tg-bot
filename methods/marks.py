import requests
import xlrd
import os
import re


def mark_parse(session: requests.Session) -> dict:
    headers = {'user-agent': 'Mozilla/5.0'}
    r = session.get('https://gym40.eljur.ru/journal-app/view.journal/?mode=excel', stream=True, headers=headers)
    with open('table_of_marks.xls', 'wb') as f:
        f.write(r.content)
    rb = xlrd.open_workbook('table_of_marks.xls', formatting_info=True)
    sheet = rb.sheet_by_index(0)
    marks = {}
    for rownum in range(3, sheet.nrows):
        row = sheet.row_values(rownum)
        marks[row[0]] = [i for i in row[1:] if i != '']
        for i in range(len(marks[row[0]])):
            try:
                marks[row[0]][i] = int(marks[row[0]][i])
            except Exception:
                pass
    os.remove('table_of_marks.xls')
    return marks


def get_correct_marks(current_marks) -> dict:
    correct_marks = []
    for marks in current_marks.values():
        for i in range(len(marks)):
            if '✕' in str(marks[i]):
                mark = marks[i].split('✕')[0]
                marks[i] = mark
                marks.insert(i, mark)
        marks = ' '.join(str(i) for i in marks)
        match = re.findall(r'[0-9]', str(marks))
        correct_marks.append(match)
    subjects = list(current_marks.keys())
    return dict(zip(subjects, correct_marks))


def get_average(marks) -> float:
    marks = list(map(int, marks))
    average = sum(marks) / len(marks)
    return float('{0:.2f}'.format(average))
