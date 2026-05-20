# -*- coding: utf-8 -*-
"""
Лабораторная работа 1: Представление чисел в памяти компьютера
Вариант C: 5421 BCD

Модуль содержит интерфейс пользователя (меню, ввод/вывод).
"""

import sys
import io

from laba1_functions import (
    bit_array_to_string,
    direct_code_32,
    direct_code_to_decimal,
    reverse_code_32,
    reverse_code_to_decimal,
    additional_code_32,
    additional_code_to_decimal,
    sum_additional_32,
    subtraction_additional_32,
    multiply_direct_32,
    divide_direct_32,
    decimal_to_ieee754,
    ieee754_to_decimal,
    sum_ieee754,
    subtraction_ieee754,
    multiply_ieee754,
    divide_ieee754,
    decimal_to_5421_bcd_32,
    bcd_5421_to_decimal,
    sum_bcd_5421,
    MAX_SIGNED_INT32,
    MIN_SIGNED_INT32,
)

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )


def print_header():
    """Вывести заголовок программы."""
    separator = "=" * 80
    print(separator)
    print("Лабораторная работа №1")
    print("Представление чисел в памяти компьютера")
    print("Вариант C: 5421 BCD")
    print(separator)


def print_menu():
    """Вывести меню операций."""
    print("\nВыберите операцию:")
    print("1. Перевод числа в прямой, обратный, дополнительный код")
    print("2. Сложение двух чисел в дополнительном коде")
    print("3. Вычитание двух чисел в дополнительном коде")
    print("4. Умножение двух чисел в прямом коде")
    print("5. Деление двух чисел в прямом коде")
    print("6. Операции с числами IEEE-754 (сложение)")
    print("7. Операции с числами IEEE-754 (вычитание)")
    print("8. Операции с числами IEEE-754 (умножение)")
    print("9. Операции с числами IEEE-754 (деление)")
    print("10. Сложение чисел в 5421 BCD")
    print("0. Выход")


def print_binary_decimal(name, bit_array, decimal_value=None):
    """Вывести результат в двоичном и десятичном формате."""
    print(f"{name}:")
    print(f"  Двоичный: {bit_array_to_string(bit_array)}")
    if decimal_value is not None:
        print(f"  Десятичный: {decimal_value}")


def get_integer_input(prompt):
    """Получить целое число от пользователя."""
    try:
        return int(input(prompt))
    except ValueError:
        return None


def get_float_input(prompt):
    """Получить число с плавающей точкой от пользователя."""
    try:
        return float(input(prompt))
    except ValueError:
        return None


def run_conversion_task():
    """Выполнить задачу конвертации числа в различные коды."""
    print("\nВведите целое число")
    print(f"Диапазон: от {MIN_SIGNED_INT32} до {MAX_SIGNED_INT32}")

    number = get_integer_input("Ваше число: ")
    if number is None:
        print("Ошибка! Введите целое число.")
        return

    if not (MIN_SIGNED_INT32 <= number <= MAX_SIGNED_INT32):
        print("Число вне диапазона 32-битного представления!")
        return

    print(f"\nЧисло: {number}")

    direct = direct_code_32(number)
    reverse = reverse_code_32(number)
    additional = additional_code_32(number)

    print_binary_decimal("Прямой код", direct)
    print_binary_decimal("Обратный код", reverse)
    print_binary_decimal("Дополнительный код", additional)

    print("\nПроверка:")
    print(f"  Из прямого кода: {direct_code_to_decimal(direct)}")
    print(f"  Из обратного кода: {reverse_code_to_decimal(reverse)}")
    print(f"  Из дополнительного кода: {additional_code_to_decimal(additional)}")


def run_addition_task():
    """Выполнить сложение двух чисел в дополнительном коде."""
    print("\nСложение в дополнительном коде")

    num1 = get_integer_input("Введите первое число: ")
    num2 = get_integer_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите целые числа.")
        return

    result = sum_additional_32(num1, num2)
    result_decimal = additional_code_to_decimal(result)

    print(f"\n{num1} + {num2} = {num1 + num2} (обычное сложение)")
    print_binary_decimal("Результат в дополнительном коде", result, result_decimal)


def run_subtraction_task():
    """Выполнить вычитание двух чисел в дополнительном коде."""
    print("\nВычитание в дополнительном коде")

    minuend = get_integer_input("Введите уменьшаемое: ")
    subtrahend = get_integer_input("Введите вычитаемое: ")

    if minuend is None or subtrahend is None:
        print("Ошибка! Введите целые числа.")
        return

    result = subtraction_additional_32(minuend, subtrahend)
    result_decimal = additional_code_to_decimal(result)

    expected = minuend - subtrahend
    print(f"\n{minuend} - {subtrahend} = {expected} (обычное вычитание)")
    print_binary_decimal("Разность в дополнительном коде", result, result_decimal)


def run_multiplication_task():
    """Выполнить умножение двух чисел в прямом коде."""
    print("\nУмножение в прямом коде")

    multiplicand = get_integer_input("Введите первое число: ")
    multiplier = get_integer_input("Введите второе число: ")

    if multiplicand is None or multiplier is None:
        print("Ошибка! Введите целые числа.")
        return

    result = multiply_direct_32(multiplicand, multiplier)
    result_decimal = direct_code_to_decimal(result)

    expected = multiplicand * multiplier
    print(f"\n{multiplicand} * {multiplier} = {expected} (обычное умножение)")
    print_binary_decimal("Произведение в прямом коде", result, result_decimal)


def run_division_task():
    """Выполнить деление двух чисел в прямом коде."""
    print("\nДеление в прямом коде")

    dividend = get_integer_input("Введите делимое: ")
    divisor = get_integer_input("Введите делитель: ")

    if dividend is None or divisor is None:
        print("Ошибка! Введите целые числа.")
        return

    if divisor == 0:
        print("Ошибка: деление на ноль!")
        return

    quotient, remainder, fractional = divide_direct_32(dividend, divisor, 5)
    quotient_decimal = direct_code_to_decimal(quotient)
    remainder_decimal = direct_code_to_decimal(remainder)

    expected = dividend / divisor
    print(f"\n{dividend} / {divisor} = {expected:.5f} (обычное деление)")
    print_binary_decimal("Частное (целая часть)", quotient, quotient_decimal)
    print_binary_decimal("Остаток", remainder, remainder_decimal)
    print(f"Дробная часть (5 бит): {bit_array_to_string(fractional)}")


def run_ieee754_addition():
    """Выполнить сложение чисел IEEE-754."""
    print("\nСложение IEEE-754")

    num1 = get_float_input("Введите первое число: ")
    num2 = get_float_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите числа с плавающей точкой.")
        return

    result_binary, result_decimal = sum_ieee754(num1, num2)
    expected = num1 + num2

    print(f"\n{num1} + {num2} = {expected} (обычное сложение)")
    print_binary_decimal("Результат IEEE-754", result_binary, result_decimal)


def run_ieee754_subtraction():
    """Выполнить вычитание чисел IEEE-754."""
    print("\nВычитание IEEE-754")

    num1 = get_float_input("Введите первое число: ")
    num2 = get_float_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите числа с плавающей точкой.")
        return

    result_binary, result_decimal = subtraction_ieee754(num1, num2)
    expected = num1 - num2

    print(f"\n{num1} - {num2} = {expected} (обычное вычитание)")
    print_binary_decimal("Результат IEEE-754", result_binary, result_decimal)


def run_ieee754_multiplication():
    """Выполнить умножение чисел IEEE-754."""
    print("\nУмножение IEEE-754")

    num1 = get_float_input("Введите первое число: ")
    num2 = get_float_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите числа с плавающей точкой.")
        return

    result_binary, result_decimal = multiply_ieee754(num1, num2)
    expected = num1 * num2

    print(f"\n{num1} * {num2} = {expected} (обычное умножение)")
    print_binary_decimal("Результат IEEE-754", result_binary, result_decimal)


def run_ieee754_division():
    """Выполнить деление чисел IEEE-754."""
    print("\nДеление IEEE-754")

    num1 = get_float_input("Введите первое число: ")
    num2 = get_float_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите числа с плавающей точкой.")
        return

    if num2 == 0:
        print("Ошибка: деление на ноль!")
        return

    result_binary, result_decimal = divide_ieee754(num1, num2)
    expected = num1 / num2

    print(f"\n{num1} / {num2} = {expected} (обычное деление)")
    print_binary_decimal("Результат IEEE-754", result_binary, result_decimal)


def run_bcd_addition():
    """Выполнить сложение чисел в 5421 BCD."""
    print("\nСложение в 5421 BCD")

    num1 = get_integer_input("Введите первое число: ")
    num2 = get_integer_input("Введите второе число: ")

    if num1 is None or num2 is None:
        print("Ошибка! Введите целые числа.")
        return

    result = sum_bcd_5421(num1, num2)
    result_decimal = bcd_5421_to_decimal(result)

    expected = num1 + num2
    print(f"\n{num1} + {num2} = {expected} (обычное сложение)")
    print_binary_decimal("Результат в 5421 BCD", result, result_decimal)


def main():
    """Основная функция программы."""
    print_header()

    task_handlers = {
        "1": run_conversion_task,
        "2": run_addition_task,
        "3": run_subtraction_task,
        "4": run_multiplication_task,
        "5": run_division_task,
        "6": run_ieee754_addition,
        "7": run_ieee754_subtraction,
        "8": run_ieee754_multiplication,
        "9": run_ieee754_division,
        "10": run_bcd_addition,
    }

    while True:
        print_menu()
        choice = input("\nВаш выбор: ").strip()

        if choice == "0":
            print("Выход из программы.")
            break

        handler = task_handlers.get(choice)
        if handler:
            handler()
        else:
            print("Неверный выбор! Попробуйте снова.")


if __name__ == "__main__":
    main()
