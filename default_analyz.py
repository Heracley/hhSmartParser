import json
from collections import defaultdict
from openpyxl import Workbook


def tag_analyz(input_file) -> dict:
    try:
        dct = defaultdict(int)
        with open(input_file, "r", encoding='utf-8') as file:
            for line in file:
                line = file.readline()[:-3] + "}"
                try:
                    vacancy: dict = json.loads(line)
                except:
                    continue
                if vacancy['tags']:
                    for tag in vacancy['tags']:
                        dct[tag.lower().replace('\xa0', ' ')] += 1
        return dct
    except FileNotFoundError:
        raise FileNotFoundError


def taganalyz(input_file: str):
    try:
        listToExcel = list(tag_analyz(input_file).items())
        listToExcel.sort(key=lambda x: x[1], reverse=True)
        wb = Workbook()
        ws = wb.active
        for row in listToExcel:
            ws.append(row)
        try:
            wb.save("tag_analyz.xlsx")
        except PermissionError:
            print("Сначала закройте файл tag_analyz.xlsx")

        print("Успешно сохранена статистика по тэгам в файле tag_analyz.xlsx !")
    except FileNotFoundError:
        print("Файл не найден")

