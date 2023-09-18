import argparse

from default_analyz import taganalyz
from parse_hh import parsehh

parser = argparse.ArgumentParser(description='Управление функциями в приложении')

subparsers = parser.add_subparsers(dest='command', help='Доступные функции')

#  Парсинг вакансий
parser_parsehh = subparsers.add_parser('parsehh', help='Спарсить все вакансии на hh.ru по запросу')
parser_parsehh.add_argument(
    '-rt', '--request', required=True,
    help='Укажите запрос для поисковой системы hh'
)
parser_parsehh.add_argument(
    '-o', '--output_file', required=False,
    help='Имя файла с выходными данными'
)
parser_parsehh.add_argument(
    '-n', '--number_of_vacancies', required=False,
    help='''Необходимое количество вакансий для парсинга. Если больше, чем существует - будет получено столько, 
    сколько найдено'''
)

parser_taganalyz = subparsers.add_parser("taganalyz", help="Проанализировать тэги вакансий")
parser_taganalyz.add_argument(
    "-i", "--input_file", required=True,
    help="Укажите входной файл с данными в формате JSON"
)

# Обработка аргументов командной строки
args = parser.parse_args()

# Вызов соответствующей функции в зависимости от выбранного аргумента
if args.command == 'parsehh':
    parsehh(request=args.request, output_file=args.output_file, number_of_vacancies=args.number_of_vacancies)
if args.command == "taganalyz":
    taganalyz(input_file=str(args.input_file))
