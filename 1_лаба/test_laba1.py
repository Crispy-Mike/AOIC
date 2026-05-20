# -*- coding: utf-8 -*-
"""
Unit-тесты для лабораторной работы 1.
Покрытие >90% всех функций из laba1_functions.py
"""

import unittest

from laba1_functions import (
    create_bit_array,
    bit_array_to_string,
    binary_to_decimal,
    decimal_to_binary,
    invert_bits,
    add_one_to_binary,
    direct_code_32,
    direct_code_to_decimal,
    reverse_code_32,
    reverse_code_to_decimal,
    additional_code_32,
    additional_code_to_decimal,
    sum_additional_32,
    negate_additional_code,
    subtraction_additional_32,
    multiply_direct_32,
    divide_direct_32,
    compute_fractional_part,
    decimal_to_ieee754,
    ieee754_to_decimal,
    compute_ieee754_exponent,
    compute_ieee754_mantissa_fraction,
    compute_mantissa_bits,
    compute_mantissa_value,
    sum_ieee754,
    subtraction_ieee754,
    multiply_ieee754,
    divide_ieee754,
    decimal_digit_to_5421_bcd,
    bcd_5421_to_decimal_digit,
    decimal_to_5421_bcd_32,
    bcd_5421_to_decimal,
    sum_bcd_5421,
    get_tetrad_value,
    TOTAL_BITS,
    MAX_SIGNED_INT32,
    MIN_SIGNED_INT32,
)


class TestHelperFunctions(unittest.TestCase):
    """Тесты вспомогательных функций."""

    def test_create_bit_array_default_size(self):
        result = create_bit_array()
        self.assertEqual(len(result), TOTAL_BITS)
        self.assertEqual(result, ["0"] * TOTAL_BITS)

    def test_create_bit_array_custom_size(self):
        result = create_bit_array(8)
        self.assertEqual(len(result), 8)
        self.assertEqual(result, ["0"] * 8)

    def test_bit_array_to_string(self):
        bit_array = ["1", "0", "1", "0"]
        result = bit_array_to_string(bit_array)
        self.assertEqual(result, "1010")

    def test_bit_array_to_string_empty(self):
        result = bit_array_to_string([])
        self.assertEqual(result, "")

    def test_binary_to_decimal_zero(self):
        bit_array = ["0"] * 8
        result = binary_to_decimal(bit_array)
        self.assertEqual(result, 0)

    def test_binary_to_decimal_positive(self):
        bit_array = ["0", "0", "1", "0", "1", "0", "1", "0"]
        result = binary_to_decimal(bit_array)
        self.assertEqual(result, 42)

    def test_binary_to_decimal_all_ones(self):
        bit_array = ["1", "1", "1", "1"]
        result = binary_to_decimal(bit_array)
        self.assertEqual(result, 15)

    def test_decimal_to_binary_zero(self):
        result = decimal_to_binary(0, 8)
        self.assertEqual(result, ["0"] * 8)

    def test_decimal_to_binary_positive(self):
        result = decimal_to_binary(42, 8)
        expected = ["0", "0", "1", "0", "1", "0", "1", "0"]
        self.assertEqual(result, expected)

    def test_decimal_to_binary_negative_clamped(self):
        result = decimal_to_binary(-5, 8)
        self.assertEqual(result, ["0"] * 8)

    def test_decimal_to_binary_overflow(self):
        result = decimal_to_binary(256, 8)
        self.assertEqual(result, ["0"] * 8)

    def test_invert_bits(self):
        bit_array = ["0", "0", "1", "1", "0"]
        result = invert_bits(bit_array, 1, 3)
        expected = ["0", "1", "0", "0", "0"]
        self.assertEqual(result, expected)

    def test_invert_bits_full_range(self):
        bit_array = ["0", "1", "0", "1"]
        result = invert_bits(bit_array, 0, 3)
        expected = ["1", "0", "1", "0"]
        self.assertEqual(result, expected)

    def test_add_one_to_binary_no_carry(self):
        bit_array = ["0", "0", "1", "0"]
        result = add_one_to_binary(bit_array, 0)
        expected = ["0", "0", "1", "1"]
        self.assertEqual(result, expected)

    def test_add_one_to_binary_with_carry(self):
        bit_array = ["0", "0", "1", "1"]
        result = add_one_to_binary(bit_array, 0)
        expected = ["0", "1", "0", "0"]
        self.assertEqual(result, expected)

    def test_add_one_to_binary_all_ones(self):
        bit_array = ["1", "1", "1", "1"]
        result = add_one_to_binary(bit_array, 0)
        expected = ["0", "0", "0", "0"]
        self.assertEqual(result, expected)


class TestDirectCode(unittest.TestCase):
    """Тесты прямого кода."""

    def test_direct_code_zero(self):
        result = direct_code_32(0)
        self.assertEqual(result, ["0"] * TOTAL_BITS)

    def test_direct_code_positive(self):
        result = direct_code_32(42)
        self.assertEqual(direct_code_to_decimal(result), 42)
        self.assertEqual(result[0], "0")

    def test_direct_code_negative(self):
        result = direct_code_32(-42)
        self.assertEqual(direct_code_to_decimal(result), -42)
        self.assertEqual(result[0], "1")

    def test_direct_code_max_positive(self):
        result = direct_code_32(MAX_SIGNED_INT32)
        self.assertEqual(direct_code_to_decimal(result), MAX_SIGNED_INT32)

    def test_direct_code_min_negative(self):
        result = direct_code_32(MIN_SIGNED_INT32)
        self.assertEqual(direct_code_to_decimal(result), MIN_SIGNED_INT32)

    def test_direct_code_roundtrip_positive(self):
        original = 12345
        encoded = direct_code_32(original)
        decoded = direct_code_to_decimal(encoded)
        self.assertEqual(original, decoded)

    def test_direct_code_roundtrip_negative(self):
        original = -12345
        encoded = direct_code_32(original)
        decoded = direct_code_to_decimal(encoded)
        self.assertEqual(original, decoded)


class TestReverseCode(unittest.TestCase):
    """Тесты обратного кода."""

    def test_reverse_code_zero(self):
        result = reverse_code_32(0)
        self.assertEqual(result, ["0"] * TOTAL_BITS)

    def test_reverse_code_positive(self):
        result = reverse_code_32(42)
        self.assertEqual(reverse_code_to_decimal(result), 42)

    def test_reverse_code_negative(self):
        result = reverse_code_32(-42)
        self.assertEqual(reverse_code_to_decimal(result), -42)
        self.assertNotEqual(result, direct_code_32(-42))

    def test_reverse_code_roundtrip(self):
        for value in [100, -100, 1, -1, 255, -255]:
            encoded = reverse_code_32(value)
            decoded = reverse_code_to_decimal(encoded)
            self.assertEqual(value, decoded)


class TestAdditionalCode(unittest.TestCase):
    """Тесты дополнительного кода."""

    def test_additional_code_zero(self):
        result = additional_code_32(0)
        self.assertEqual(result, ["0"] * TOTAL_BITS)

    def test_additional_code_positive(self):
        result = additional_code_32(42)
        self.assertEqual(additional_code_to_decimal(result), 42)

    def test_additional_code_negative(self):
        result = additional_code_32(-42)
        self.assertEqual(additional_code_to_decimal(result), -42)

    def test_additional_code_min_int32(self):
        result = additional_code_32(MIN_SIGNED_INT32)
        self.assertEqual(additional_code_to_decimal(result), MIN_SIGNED_INT32)
        self.assertEqual(result[0], "1")

    def test_additional_code_roundtrip(self):
        for value in [100, -100, MAX_SIGNED_INT32, MIN_SIGNED_INT32]:
            encoded = additional_code_32(value)
            decoded = additional_code_to_decimal(encoded)
            self.assertEqual(value, decoded)


class TestAddition(unittest.TestCase):
    """Тесты сложения в дополнительном коде."""

    def test_sum_positive(self):
        result = sum_additional_32(100, 50)
        self.assertEqual(additional_code_to_decimal(result), 150)

    def test_sum_negative(self):
        result = sum_additional_32(-100, -50)
        self.assertEqual(additional_code_to_decimal(result), -150)

    def test_sum_mixed(self):
        result = sum_additional_32(-100, 50)
        self.assertEqual(additional_code_to_decimal(result), -50)

    def test_sum_with_zero(self):
        result = sum_additional_32(42, 0)
        self.assertEqual(additional_code_to_decimal(result), 42)

    def test_sum_opposite_numbers(self):
        result = sum_additional_32(100, -100)
        self.assertEqual(additional_code_to_decimal(result), 0)


class TestNegateAdditionalCode(unittest.TestCase):
    """Тесты отрицания в дополнительном коде."""

    def test_negate_positive(self):
        original = additional_code_32(42)
        negated = negate_additional_code(original)
        self.assertEqual(additional_code_to_decimal(negated), -42)

    def test_negate_negative(self):
        original = additional_code_32(-42)
        negated = negate_additional_code(original)
        self.assertEqual(additional_code_to_decimal(negated), 42)

    def test_negate_zero(self):
        original = additional_code_32(0)
        negated = negate_additional_code(original)
        self.assertEqual(additional_code_to_decimal(negated), 0)


class TestSubtraction(unittest.TestCase):
    """Тесты вычитания в дополнительном коде."""

    def test_subtraction_positive(self):
        result = subtraction_additional_32(100, 50)
        self.assertEqual(additional_code_to_decimal(result), 50)

    def test_subtraction_negative_result(self):
        result = subtraction_additional_32(50, 100)
        self.assertEqual(additional_code_to_decimal(result), -50)

    def test_subtraction_with_negative(self):
        result = subtraction_additional_32(-50, -30)
        self.assertEqual(additional_code_to_decimal(result), -20)

    def test_subtraction_same_number(self):
        result = subtraction_additional_32(42, 42)
        self.assertEqual(additional_code_to_decimal(result), 0)


class TestMultiplication(unittest.TestCase):
    """Тесты умножения в прямом коде."""

    def test_multiply_positive(self):
        result = multiply_direct_32(10, 5)
        self.assertEqual(direct_code_to_decimal(result), 50)

    def test_multiply_negative(self):
        result = multiply_direct_32(-10, 5)
        self.assertEqual(direct_code_to_decimal(result), -50)

    def test_multiply_both_negative(self):
        result = multiply_direct_32(-10, -5)
        self.assertEqual(direct_code_to_decimal(result), 50)

    def test_multiply_by_zero(self):
        result = multiply_direct_32(100, 0)
        self.assertEqual(direct_code_to_decimal(result), 0)

    def test_multiply_by_one(self):
        result = multiply_direct_32(42, 1)
        self.assertEqual(direct_code_to_decimal(result), 42)


class TestDivision(unittest.TestCase):
    """Тесты деления в прямом коде."""

    def test_division_exact(self):
        quotient, remainder, _ = divide_direct_32(100, 10)
        self.assertEqual(direct_code_to_decimal(quotient), 10)
        self.assertEqual(direct_code_to_decimal(remainder), 0)

    def test_division_with_remainder(self):
        quotient, remainder, _ = divide_direct_32(10, 3)
        self.assertEqual(direct_code_to_decimal(quotient), 3)
        self.assertEqual(direct_code_to_decimal(remainder), 1)

    def test_division_negative(self):
        quotient, _, _ = divide_direct_32(-100, 10)
        self.assertEqual(direct_code_to_decimal(quotient), -10)

    def test_division_by_zero_raises(self):
        with self.assertRaises(ValueError):
            divide_direct_32(100, 0)


class TestFractionalPart(unittest.TestCase):
    """Тесты вычисления дробной части."""

    def test_compute_fractional_part_zero(self):
        result = compute_fractional_part(0, 10, 5)
        self.assertEqual(result, ["0"] * 5)

    def test_compute_fractional_part_half(self):
        result = compute_fractional_part(5, 10, 5)
        self.assertEqual(result, ["1", "0", "0", "0", "0"])


class TestIEEE754(unittest.TestCase):
    """Тесты IEEE-754."""

    def test_ieee754_zero(self):
        result = decimal_to_ieee754(0.0)
        self.assertEqual(result, ["0"] * TOTAL_BITS)

    def test_ieee754_positive(self):
        result = decimal_to_ieee754(3.14)
        decoded = ieee754_to_decimal(result)
        self.assertAlmostEqual(decoded, 3.14, places=2)

    def test_ieee754_negative(self):
        result = decimal_to_ieee754(-2.5)
        decoded = ieee754_to_decimal(result)
        self.assertAlmostEqual(decoded, -2.5, places=5)

    def test_ieee754_integer(self):
        result = decimal_to_ieee754(42.0)
        decoded = ieee754_to_decimal(result)
        self.assertEqual(decoded, 42.0)

    def test_compute_ieee754_exponent(self):
        self.assertEqual(compute_ieee754_exponent(1.5), 0)
        self.assertEqual(compute_ieee754_exponent(4.0), 2)
        self.assertEqual(compute_ieee754_exponent(0.5), -1)

    def test_compute_mantissa_bits(self):
        result = compute_mantissa_bits(0.5)
        self.assertEqual(result[0], "1")

    def test_compute_mantissa_value(self):
        mantissa_bits = ["1"] + ["0"] * 22
        result = compute_mantissa_value(mantissa_bits)
        self.assertAlmostEqual(result, 1.5, places=5)


class TestIEEE754Operations(unittest.TestCase):
    """Тесты операций IEEE-754."""

    def test_sum_ieee754(self):
        _, result = sum_ieee754(1.5, 2.5)
        self.assertAlmostEqual(result, 4.0, places=5)

    def test_subtraction_ieee754(self):
        _, result = subtraction_ieee754(5.0, 2.5)
        self.assertAlmostEqual(result, 2.5, places=5)

    def test_multiply_ieee754(self):
        _, result = multiply_ieee754(2.0, 3.0)
        self.assertAlmostEqual(result, 6.0, places=5)

    def test_divide_ieee754(self):
        _, result = divide_ieee754(10.0, 2.0)
        self.assertAlmostEqual(result, 5.0, places=5)

    def test_divide_ieee754_by_zero(self):
        with self.assertRaises(ValueError):
            divide_ieee754(10.0, 0.0)


class TestBCD5421(unittest.TestCase):
    """Тесты BCD 5421."""

    def test_decimal_digit_to_5421_bcd_zero(self):
        result = decimal_digit_to_5421_bcd(0)
        self.assertEqual(result, "0000")

    def test_decimal_digit_to_5421_bcd_five(self):
        result = decimal_digit_to_5421_bcd(5)
        self.assertEqual(result, "1000")

    def test_decimal_digit_to_5421_bcd_nine(self):
        result = decimal_digit_to_5421_bcd(9)
        self.assertEqual(result, "1100")

    def test_bcd_5421_to_decimal_digit(self):
        self.assertEqual(bcd_5421_to_decimal_digit("0000"), 0)
        self.assertEqual(bcd_5421_to_decimal_digit("1000"), 5)
        self.assertEqual(bcd_5421_to_decimal_digit("1100"), 9)

    def test_decimal_to_5421_bcd_32_zero(self):
        result = decimal_to_5421_bcd_32(0)
        self.assertEqual(bcd_5421_to_decimal(result), 0)

    def test_decimal_to_5421_bcd_32_positive(self):
        result = decimal_to_5421_bcd_32(42)
        self.assertEqual(bcd_5421_to_decimal(result), 42)

    def test_decimal_to_5421_bcd_32_negative(self):
        result = decimal_to_5421_bcd_32(-42)
        self.assertEqual(bcd_5421_to_decimal(result), -42)

    def test_bcd_5421_to_decimal_roundtrip(self):
        for value in [0, 1, 42, 100, 999, -1, -42, -999]:
            encoded = decimal_to_5421_bcd_32(value)
            decoded = bcd_5421_to_decimal(encoded)
            self.assertEqual(value, decoded)

    def test_sum_bcd_5421(self):
        result = sum_bcd_5421(25, 17)
        self.assertEqual(bcd_5421_to_decimal(result), 42)

    def test_sum_bcd_5421_with_zero(self):
        result = sum_bcd_5421(42, 0)
        self.assertEqual(bcd_5421_to_decimal(result), 42)

    def test_get_tetrad_value(self):
        # Тетрада 0 (знаковая): биты [0,1,0,0] с весами [0,0,0,1] = 0
        # Тест проверяет работу функции — веса для тетрады 0 другие
        bit_array = ["0", "1", "0", "0"] + ["0"] * 28
        result = get_tetrad_value(bit_array, 0, 0)
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
