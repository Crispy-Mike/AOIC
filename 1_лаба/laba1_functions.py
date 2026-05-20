TOTAL_BITS = 32
SIGN_BIT_INDEX = 0
MAGNITUDE_BITS = 31
IEEE754_EXPONENT_BITS = 8
IEEE754_MANTISSA_BITS = 23
IEEE754_BIAS = 127
BCD_TETRAD_BITS = 4
BCD_DIGITS_COUNT = 7
DIVISION_PRECISION = 5
MAX_SIGNED_INT32 = 2147483647
MIN_SIGNED_INT32 = -2147483648

BCD_5421_WEIGHTS = [5, 4, 2, 1]

BCD_5421_ENCODING = {
    0: "0000",
    1: "0001",
    2: "0010",
    3: "0011",
    4: "0100",
    5: "1000",
    6: "1001",
    7: "1010",
    8: "1011",
    9: "1100",
}


def create_bit_array(size=TOTAL_BITS):
    return ["0"] * size


def bit_array_to_string(bit_array):
    return "".join(bit_array)


def binary_to_decimal(bit_array):
    result = 0
    for index, bit in enumerate(reversed(bit_array)):
        if bit == "1":
            result += 2 ** index
    return result


def decimal_to_binary(number, bits_count):
    if number < 0:
        number = 0
    result = create_bit_array(bits_count)
    index = 0
    while number > 0 and index < bits_count:
        result[bits_count - 1 - index] = str(number % 2)
        number //= 2
        index += 1
    return result


def invert_bits(bit_array, start_index, end_index):
    result = bit_array.copy()
    for index in range(start_index, end_index + 1):
        result[index] = "1" if result[index] == "0" else "0"
    return result


def add_one_to_binary(bit_array, start_index):
    result = bit_array.copy()
    carry = 1
    for index in range(len(result) - 1, start_index - 1, -1):
        if result[index] == "1" and carry == 1:
            result[index] = "0"
        elif result[index] == "0" and carry == 1:
            result[index] = "1"
            carry = 0
        else:
            break
    return result


def direct_code_32(number):
    result = create_bit_array(TOTAL_BITS)

    if number < 0:
        result[SIGN_BIT_INDEX] = "1"
        magnitude = -number
    else:
        result[SIGN_BIT_INDEX] = "0"
        magnitude = number

    if magnitude > MAX_SIGNED_INT32:
        for index in range(1, TOTAL_BITS):
            result[index] = "1"
    else:
        magnitude_bits = decimal_to_binary(magnitude, MAGNITUDE_BITS)
        for index in range(MAGNITUDE_BITS):
            result[index + 1] = magnitude_bits[index]

    return result


def direct_code_to_decimal(bit_array):
    sign = -1 if bit_array[SIGN_BIT_INDEX] == "1" else 1

    if sign == -1 and all(bit == "1" for bit in bit_array[1:]):
        return MIN_SIGNED_INT32

    magnitude = binary_to_decimal(bit_array[1:])
    return sign * magnitude


def reverse_code_32(number):
    if number >= 0:
        return direct_code_32(number)

    direct = direct_code_32(number)
    return invert_bits(direct, 1, TOTAL_BITS - 1)


def reverse_code_to_decimal(bit_array):
    if bit_array[SIGN_BIT_INDEX] == "0":
        return binary_to_decimal(bit_array[1:])

    inverted = invert_bits(bit_array, 1, TOTAL_BITS - 1)
    magnitude = binary_to_decimal(inverted[1:])
    return -magnitude


def additional_code_32(number):
    if number >= 0:
        return direct_code_32(number)

    if number == MIN_SIGNED_INT32:
        result = create_bit_array(TOTAL_BITS)
        result[SIGN_BIT_INDEX] = "1"
        return result

    reverse = reverse_code_32(number)
    return add_one_to_binary(reverse, 1)


def additional_code_to_decimal(bit_array):
    if bit_array[SIGN_BIT_INDEX] == "0":
        return binary_to_decimal(bit_array[1:])

    if all(bit == "0" for bit in bit_array[1:]):
        return MIN_SIGNED_INT32

    inverted = invert_bits(bit_array, 1, TOTAL_BITS - 1)
    magnitude_binary = add_one_to_binary(inverted, 1)
    magnitude = binary_to_decimal(magnitude_binary[1:])
    return -magnitude


def sum_additional_32(number1, number2):
    add1 = additional_code_32(number1)
    add2 = additional_code_32(number2)

    result = create_bit_array(TOTAL_BITS)
    carry = 0

    for index in range(TOTAL_BITS - 1, -1, -1):
        bit_sum = int(add1[index]) + int(add2[index]) + carry
        result[index] = str(bit_sum % 2)
        carry = bit_sum // 2

    return result


def negate_additional_code(bit_array):
    inverted = invert_bits(bit_array, 0, TOTAL_BITS - 1)
    return add_one_to_binary(inverted, 0)


def subtraction_additional_32(minuend, subtrahend):
    add_minuend = additional_code_32(minuend)
    add_subtrahend = additional_code_32(subtrahend)

    negated_subtrahend = negate_additional_code(add_subtrahend)

    result = create_bit_array(TOTAL_BITS)
    carry = 0

    for index in range(TOTAL_BITS - 1, -1, -1):
        bit_sum = int(add_minuend[index]) + int(negated_subtrahend[index]) + carry
        result[index] = str(bit_sum % 2)
        carry = bit_sum // 2

    return result


def multiply_direct_32(multiplicand, multiplier):
    direct1 = direct_code_32(multiplicand)
    direct2 = direct_code_32(multiplier)

    result_sign = "0" if direct1[SIGN_BIT_INDEX] == direct2[SIGN_BIT_INDEX] else "1"

    magnitude1 = binary_to_decimal(direct1[1:])
    magnitude2 = binary_to_decimal(direct2[1:])

    product_magnitude = magnitude1 * magnitude2

    if product_magnitude > MAX_SIGNED_INT32:
        product_magnitude = product_magnitude % (2 ** MAGNITUDE_BITS)

    result = decimal_to_binary(product_magnitude, MAGNITUDE_BITS)
    result[SIGN_BIT_INDEX] = result_sign

    return result


def divide_direct_32(dividend, divisor, precision=DIVISION_PRECISION):
    if divisor == 0:
        raise ValueError("Деление на ноль")

    direct_dividend = direct_code_32(dividend)
    direct_divisor = direct_code_32(divisor)

    result_sign = (
        "0"
        if direct_dividend[SIGN_BIT_INDEX] == direct_divisor[SIGN_BIT_INDEX]
        else "1"
    )

    magnitude_dividend = binary_to_decimal(direct_dividend[1:])
    magnitude_divisor = binary_to_decimal(direct_divisor[1:])

    quotient_int = magnitude_dividend // magnitude_divisor
    remainder = magnitude_dividend % magnitude_divisor

    fractional_binary = compute_fractional_part(remainder, magnitude_divisor, precision)

    quotient_result = decimal_to_binary(quotient_int, MAGNITUDE_BITS)
    quotient_result[SIGN_BIT_INDEX] = result_sign

    remainder_result = decimal_to_binary(remainder, MAGNITUDE_BITS)
    remainder_result[SIGN_BIT_INDEX] = result_sign

    return quotient_result, remainder_result, fractional_binary


def compute_fractional_part(remainder, divisor, precision):
    fractional = 0
    temp_remainder = remainder

    for _ in range(precision):
        temp_remainder *= 2
        if temp_remainder >= divisor:
            fractional = fractional * 2 + 1
            temp_remainder -= divisor
        else:
            fractional = fractional * 2 + 0

    return decimal_to_binary(fractional, precision)


def decimal_to_ieee754(number):
    result = create_bit_array(TOTAL_BITS)

    if number == 0:
        return result

    if number < 0:
        result[SIGN_BIT_INDEX] = "1"
        number = -number

    exponent = compute_ieee754_exponent(number)
    mantissa_fraction = compute_ieee754_mantissa_fraction(number, exponent)

    biased_exponent = exponent + IEEE754_BIAS
    exponent_bits = decimal_to_binary(biased_exponent, IEEE754_EXPONENT_BITS)

    for index in range(IEEE754_EXPONENT_BITS):
        result[index + 1] = exponent_bits[index]

    mantissa_bits = compute_mantissa_bits(mantissa_fraction)
    for index in range(IEEE754_MANTISSA_BITS):
        result[index + 1 + IEEE754_EXPONENT_BITS] = mantissa_bits[index]

    return result


def compute_ieee754_exponent(number):
    exponent = 0
    temp_number = number

    while temp_number >= 2:
        temp_number /= 2
        exponent += 1

    while temp_number < 1:
        temp_number *= 2
        exponent -= 1

    return exponent


def compute_ieee754_mantissa_fraction(number, exponent):
    normalized = number / (2 ** exponent)
    return normalized - 1


def compute_mantissa_bits(mantissa_fraction):
    bits = create_bit_array(IEEE754_MANTISSA_BITS)
    temp_mantissa = mantissa_fraction

    for index in range(IEEE754_MANTISSA_BITS):
        temp_mantissa *= 2
        if temp_mantissa >= 1:
            bits[index] = "1"
            temp_mantissa -= 1
        else:
            bits[index] = "0"

    return bits


def ieee754_to_decimal(bit_array):
    sign = -1 if bit_array[SIGN_BIT_INDEX] == "1" else 1

    exponent_bits = bit_array[1:1 + IEEE754_EXPONENT_BITS]
    biased_exponent = binary_to_decimal(exponent_bits)

    if biased_exponent == 0:
        return 0.0

    exponent = biased_exponent - IEEE754_BIAS

    mantissa_bits = bit_array[1 + IEEE754_EXPONENT_BITS:]
    mantissa = compute_mantissa_value(mantissa_bits)

    return sign * mantissa * (2 ** exponent)


def compute_mantissa_value(mantissa_bits):
    mantissa = 1.0
    for index, bit in enumerate(mantissa_bits):
        if bit == "1":
            mantissa += 2 ** (-(index + 1))
    return mantissa


def sum_ieee754(number1, number2):
    result_decimal = ieee754_to_decimal(decimal_to_ieee754(number1)) + \
                     ieee754_to_decimal(decimal_to_ieee754(number2))
    return decimal_to_ieee754(result_decimal), result_decimal


def subtraction_ieee754(number1, number2):
    result_decimal = ieee754_to_decimal(decimal_to_ieee754(number1)) - \
                     ieee754_to_decimal(decimal_to_ieee754(number2))
    return decimal_to_ieee754(result_decimal), result_decimal


def multiply_ieee754(number1, number2):
    result_decimal = ieee754_to_decimal(decimal_to_ieee754(number1)) * \
                     ieee754_to_decimal(decimal_to_ieee754(number2))
    return decimal_to_ieee754(result_decimal), result_decimal


def divide_ieee754(number1, number2):
    if number2 == 0:
        raise ValueError("Деление на ноль")

    result_decimal = ieee754_to_decimal(decimal_to_ieee754(number1)) / \
                     ieee754_to_decimal(decimal_to_ieee754(number2))
    return decimal_to_ieee754(result_decimal), result_decimal


def decimal_digit_to_5421_bcd(digit):
    return BCD_5421_ENCODING.get(digit, "0000")


def bcd_5421_to_decimal_digit(bcd_bits):
    value = 0
    for index, bit in enumerate(bcd_bits):
        if bit == "1":
            value += BCD_5421_WEIGHTS[index]
    return value


def decimal_to_5421_bcd_32(number):
    result = create_bit_array(TOTAL_BITS)

    if number < 0:
        sign_bcd = "0001"
        number = -number
    else:
        sign_bcd = "0000"

    for index in range(BCD_TETRAD_BITS):
        result[index] = sign_bcd[index]

    number_str = str(number)
    digit_index = 0

    for str_index in range(len(number_str) - 1, -1, -1):
        if digit_index >= BCD_DIGITS_COUNT:
            break

        digit = int(number_str[str_index])
        bcd = decimal_digit_to_5421_bcd(digit)

        position = BCD_TETRAD_BITS + (BCD_DIGITS_COUNT - 1 - digit_index) * BCD_TETRAD_BITS
        for bit_index in range(BCD_TETRAD_BITS):
            if position + bit_index < TOTAL_BITS:
                result[position + bit_index] = bcd[bit_index]

        digit_index += 1

    return result


def bcd_5421_to_decimal(bit_array):
    sign_bits = bit_array[0:BCD_TETRAD_BITS]
    sign_value = bcd_5421_to_decimal_digit(sign_bits)
    sign = -1 if sign_value > 0 else 1

    result = 0
    for digit_index in range(BCD_DIGITS_COUNT):
        position = BCD_TETRAD_BITS + digit_index * BCD_TETRAD_BITS
        digit_bits = bit_array[position:position + BCD_TETRAD_BITS]
        digit = bcd_5421_to_decimal_digit(digit_bits)
        result = result * 10 + digit

    return sign * result


def sum_bcd_5421(number1, number2):
    bcd1 = decimal_to_5421_bcd_32(number1)
    bcd2 = decimal_to_5421_bcd_32(number2)

    result = create_bit_array(TOTAL_BITS)
    carry = 0

    for tetrad_index in range(BCD_DIGITS_COUNT, -1, -1):
        position_start = tetrad_index * BCD_TETRAD_BITS

        value1 = get_tetrad_value(bcd1, position_start, tetrad_index)
        value2 = get_tetrad_value(bcd2, position_start, tetrad_index)

        tetrad_sum = value1 + value2 + carry

        if tetrad_index == 0:
            if tetrad_sum > 0:
                for bit_index in range(BCD_TETRAD_BITS):
                    result[position_start + bit_index] = "0001"[bit_index]
            carry = 0
        else:
            if tetrad_sum > 9:
                tetrad_sum -= 10
                carry = 1
            else:
                carry = 0

            bcd_result = decimal_digit_to_5421_bcd(tetrad_sum)
            for bit_index in range(BCD_TETRAD_BITS):
                result[position_start + bit_index] = bcd_result[bit_index]

    return result


def get_tetrad_value(bit_array, position_start, tetrad_index):
    value = 0
    weights = BCD_5421_WEIGHTS if tetrad_index > 0 else [0, 0, 0, 1]
    for bit_index in range(BCD_TETRAD_BITS):
        if position_start + bit_index < TOTAL_BITS:
            value += int(bit_array[position_start + bit_index]) * weights[bit_index]
    return value
