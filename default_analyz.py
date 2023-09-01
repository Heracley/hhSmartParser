import json
from collections import defaultdict
from openpyxl import Workbook


def tag_analyz() -> dict:
    dct = defaultdict(int)

    with open('data.json', "r", encoding='utf-8') as file:
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


if __name__ == "__main__":
    listToExcel = list(tag_analyz().items())
    listToExcel.sort(key=lambda x: x[1], reverse=True)
    wb = Workbook()
    ws = wb.active
    for row in listToExcel:
        ws.append(row)
    wb.save("tag_analyz.xlsx")
