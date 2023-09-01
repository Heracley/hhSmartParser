import json
import time
from collections import defaultdict
import matplotlib.pyplot as plt
import openai
import os
from dotenv import load_dotenv
#  Загружаем среду и ее переменные.
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


#  Получаем список с тренировочными данными для ChatGPT из выбранного файла. Необходимо указать количество вакансий,
#  которые используются для тренировки.
def get_train_for_ai(file_name: str = "trainingdata.txt", count_of_trains: int = 3) -> list:
    train_data: list = []

    with open(file_name, "r", encoding='utf-8') as f:
        for i in range(count_of_trains):
            text = {"role": "user", "content": f.readline()}
            answer = {"role": "assistant", "content": f.readline()}
            train_data.extend([text, answer])

    return train_data


#
def get_all_required_competencies(vacancy: str):
    def ai_find_cmptncs_in_text(text, train_data=None, model="gpt-3.5-turbo-16k"):
        if train_data is None:
            train_data = get_train_for_ai()

        sysprompt = """You are part of the task analyzer code with hh.ru . Your main task is to highlight from the 
        vacancy text the technologies and competencies that an employee needs for this vacancy. Your answer should be all 
        the technologies and competencies found in the text. The answer should be short - only the technologies 
        themselves in any convenient order and competencies in lowercase letters, separated by commas, 
        nothing superfluous. If the technology or competence is composite (consisting of several words), then use "+" as 
        a separator between words. If you haven't found technologies or competencies, write "None"."""

        messages = [{"role": "system", "content": sysprompt}]
        messages.extend(train_data)
        messages.append(
            {"role": "user", "content": text}
        )
        cmptncs = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
        ).choices[0].message["content"].replace('\n', '').split(',')
        return cmptncs

    try:
        vacancy: dict = json.loads(vacancy)
    except:
        return dict()

    all_required_competencies = set()
    if vacancy["tags"]:
        for tag in vacancy["tags"]:
            all_required_competencies.add(tag.lower().replace(' ', '+'))

    cmptncs_from_text = ai_find_cmptncs_in_text(vacancy["text"])
    for cmptncs in cmptncs_from_text:
        all_required_competencies.add(cmptncs)

    return all_required_competencies


def smart_tag_analyz():
    with open('data.json', "r", encoding='utf-8') as file:
        for i in range(50):
            line = file.readline()[:-3] + "}"
            all_required_competencies = get_all_required_competencies(line)
            if all_required_competencies:
                print(i, all_required_competencies)
                time.sleep(20)


def tag_analyz(dct=None):
    if dct is None:
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


def get_graphic(dct):


    # Ваш словарь с д   анными
    tech_data = dct

    # Разделение данных на ключи (технологии) и значения (популярность)
    tech_names = list(tech_data.keys())
    popularity = list(tech_data.values())

    # Создание баров на графике
    plt.bar(tech_names, popularity)

    # Добавление подписей к графику
    plt.xlabel('Технологии')
    plt.ylabel('Популярность')
    plt.title('Популярность технологий')

    # Поворот подписей по оси x, если они слишком длинные
    plt.xticks(rotation=45)

    # Отображение графика
    plt.show()


if __name__ == "__main__":
    tag_analyz()


