import json
import time
import os
from collections import defaultdict
from openpyxl import Workbook
import openai

from dotenv import load_dotenv
#  Загружаем среду и ее переменные.
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


#  Получаем список с тренировочными данными для ChatGPT из выбранного файла. Необходимо указать количество вакансий,
#  которые используются для тренировки. Важно, чтобы строк в тренировочном файле было четное количество, формата:
#         запрос
#         ответ
def get_train_for_ai(file_name: str = "trainingdata.txt", count_of_trains: int = 3) -> list:
    train_data: list = []

    with open(file_name, "r", encoding='utf-8') as f:
        for i in range(count_of_trains):
            text = {"role": "user", "content": f.readline()}
            answer = {"role": "assistant", "content": f.readline()}
            train_data.extend([text, answer])

    return train_data


#  При помощи специального промпта (sysprompt), а так же используя few-shooting, получаем необходимые
#  для вакансии технологии из текста и добавляем в ключевые навыки из тегов.
def get_all_required_competencies_with_ai(vacancy: str):
    def ai_find_cmptncs_in_text(text, train_data=None, model="gpt-3.5-turbo-16k"):
        if train_data is None:
            train_data = get_train_for_ai()

        sysprompt = """You are part of the task analyzer code with hh.ru . Your main task is to highlight from the 
        vacancy text the technologies and competencies that an employee needs for this vacancy. Your answer should be 
        all the technologies and competencies found in the text. The answer should be short - only the technologies 
        themselves in any convenient order and competencies in lowercase letters, separated by commas, 
        nothing superfluous. If the technology or competence is composite (consisting of several words), then use " " 
        as a separator between words. If you haven't found technologies or competencies, write "None"."""

        #  Сообщение с системным промптом
        messages = [{"role": "system", "content": sysprompt}]
        #  Добавляем тренировочные данные
        messages.extend(train_data)
        #  Добавляем запрос на поиск тегов в тексте
        messages.append(
            {"role": "user", "content": text}
        )
        #  Обращаемся к openai и получаем ответ.
        cmptncs = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        ).choices[0].message["content"].replace('\n', '').split(',')
        return cmptncs

    #  Проверяем, что полученная на вход строка десериализуется
    try:
        vacancy: dict = json.loads(vacancy)
    except:
        return dict()

    #  Если проверка пройдена, создаем множество компетенций и наполняем его тегами из вакансии
    all_required_competencies = set()
    if vacancy["tags"]:
        for tag in vacancy["tags"]:
            all_required_competencies.add(tag.lower().replace(' ', '+'))

    #  А так же добавляем все найденные в тексте компетенции помощи AI.
    cmptncs_from_text = ai_find_cmptncs_in_text(vacancy["text"])
    for cmptncs in cmptncs_from_text:
        all_required_competencies.add(cmptncs)

    return all_required_competencies


#  Проводим подсчет тегов из указанных ключевых навыков и текста вакансий в выборке. Количество обрабатываемых вакансий
#  ограничено, тк.к. это стоит денег и очень долго... (20сек+время ответа ai)*(кол-во вакансий)
def smart_tag_analyz(i_have_money_and_time=False, vacancy_count=10, delay=20) -> dict:
    #  Словарь, ключами которого являются компетенции, а значениями - их число в выборке вакансий.
    dct = defaultdict(int)

    #  Забираем данные
    with open('data.json', "r", encoding='utf-8') as file:
        def cycle():
            #  Отсекаем от строк лишнюю часть
            line = file.readline()[:-3] + "}"
            #  Получаем все компетенции, указанные в вакансии.
            all_required_competencies = get_all_required_competencies_with_ai(line)
            #  Если они обнаружены, то проходимся по ним и увеличиваем значения, соответствующие названиям-ключам
            #  этих компетенций.
            if all_required_competencies:
                for tag in all_required_competencies:
                    dct[tag] += 1
                #  Спим 20 секунд. Именно такая минимальная задержка между запросами к OPENAI API в бесплатной версии.
                #  Если у вас расширенный аккаунт, можно поставить вашу задержку.
                time.sleep(delay)

        #  В зависимости от указанного параметра обрабатываем все вакансии или только часть.
        if i_have_money_and_time:
            for string in file:
                cycle()
        else:
            for i in range(vacancy_count):
                cycle()

    return dct


if __name__ == "__main__":
    listToExcel = list(smart_tag_analyz().items())
    listToExcel.sort(key=lambda x: x[1], reverse=True)
    wb = Workbook()
    ws = wb.active
    for row in listToExcel:
        ws.append(row)
    wb.save("smart_tag_analyz.xlsx")
