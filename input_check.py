def positive_number_check(number: int):
    if type(number) != int:
        response = 'Введено не число.'
        return response
    if number <= 0:
        response = 'Число должно быть положительным!'
        return response
    return 200


