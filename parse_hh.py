import requests
from bs4 import BeautifulSoup
import fake_useragent
import time
import json
import sys

from input_check import positive_number_check


#  Получаем список ссылок на вакансии по заданному запросу (text)
def get_links(text):
    #  Создаем fake user-agent для обхода блокировки hh
    ua = fake_useragent.UserAgent()

    #  Получаем html-страницу, найденную по поиску
    data = requests.get(
        url=f"https://hh.ru/search/vacancy?text={text}&area=1&page=0",
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")

    #  Считываем из нее количество страниц с вакансиями
    try:
        page_count = int(
            soup.find("div", attrs={"class": "pager"}).find_all("span",
                                                                recursive=False)[-1].find("a").find("span").text)
    except:
        return

    #  Проходимся по всем страницам, выданных по запросу (text) и получаем ссылки на вакансии
    try:
        for page in range(page_count):
            data = requests.get(
                url=f"https://hh.ru/search/vacancy?text={text}&area=1&page={page}",
                headers={"user-agent": ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, "lxml")
            for link in soup.find_all("a", attrs={"class": "serp-item__title"}):
                yield link.attrs['href'].split('?')[0]
    except:
        return
    #  Немного спим, чтобы не перезагружать сервера hh и не улететь в бан.
    time.sleep(1)


#  Получаем всю необходимую информацию со страницы вакансии по ссылке (link)
def get_vacancy(link):
    #  Создаем fake user-agent для обхода блокировки hh
    ua = fake_useragent.UserAgent()

    #  Получаем html страницы вакансии
    data = requests.get(
        url=link,
        headers={"user-agent": ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, "lxml")

    #  Получаем "название" вакансии
    try:
        name = soup.find("h1", attrs={"class": "bloko-header-section-1"}).text
    except:
        name = ""
    #  Получаем указанную зарплату, если есть.
    try:
        salary = soup.find("div", attrs={"data-qa": "vacancy-salary"}).text.replace("\xa0", "")
    except:
        salary = ""
    #  Получаем описание вакансии, если есть.
    try:
        text = soup.find("div", attrs={"data-qa": "vacancy-description"}).text
    except:
        text = ""
    #  Получаем ключевые навыки, указанные в вакансии, если есть.
    try:
        tags = [x.text for x in soup.find("div", attrs={"class": "bloko-tag-list"}).find_all("span")]
    except:
        tags = ""

    #  Создаем словарь(json-объект) вакансии
    vacancy = {
        "name": name,
        "salary": salary,
        "text": text,
        "tags": tags,
        "url": link,
    }
    return vacancy


def parsehh(request=None, output_file=None, number_of_vacancies=None):
    if not output_file:
        output_file = "data.json"
    if not request:
        request = "python"

    #  Открываем файл data.json на запись и в удобном для считывания формате записываем все спарсенные вакансии.
    #  Если указано необходимое количество вакансий, заводим счетчик.
    if number_of_vacancies:
        resp = positive_number_check(number_of_vacancies)
        if resp != 200:
            print(resp)
            return
        n = 0
        number_of_vacancies = int(number_of_vacancies)
    else:
        n = -1

    # Если все хорошо, тооо.
    print(f"Начинаем парсинг вакансий c hh.ru по запросу '{request}'...\n")

    with open(output_file, "w", encoding="utf-8") as json_file:
        json_file.write("[\n")
        for link in get_links(request):
            #  Обновляем счетчик
            if n != -1:
                n += 1
                if n > number_of_vacancies:
                    break
                #  Организуем вывод в консоль прогресса
                sys.stdout.write(f'\rВакансий получено... {n}/{number_of_vacancies}   ')
                sys.stdout.flush()
                time.sleep(1)


            item = get_vacancy(link)
            #  Немного спим, чтобы не перезагружать сервера hh и не улететь в бан.
            time.sleep(1)
            json.dump(item, json_file, separators=(',', ':'), ensure_ascii=False)
            json_file.write(",\n")
        json_file.write("]")

    print('\n')
    print(f"Успешно спарсено {number_of_vacancies} вакансий по запросу '{request}'!")
    print(f"Файл с выходными данными: {output_file}")