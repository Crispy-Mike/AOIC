from __future__ import annotations

from typing import List, Tuple

import qm
from Equation import Equation
from constants import (
    COUNTER_INPUTS,
    COUNTER_MAX_STATE,
    DECODER_INPUTS,
    ENCODER_INPUTS,
    OFFSET_N,
    SUBTRACTOR_INPUTS,
)


def get_subtractor_equations() -> List[Equation]:
    input_vars = ["X1", "X2", "X3"]
    difference_minterms = [1, 2, 4, 7]
    borrow_minterms = [1, 2, 3, 7]

    return [
        Equation(
            name="d (Разность)",
            sdnf=qm.generate_sdnf(SUBTRACTOR_INPUTS, difference_minterms, input_vars),
            minimized=qm.minimize(SUBTRACTOR_INPUTS, difference_minterms, None, input_vars),
        ),
        Equation(
            name="b (Заем)",
            sdnf=qm.generate_sdnf(SUBTRACTOR_INPUTS, borrow_minterms, input_vars),
            minimized=qm.minimize(SUBTRACTOR_INPUTS, borrow_minterms, None, input_vars),
        ),
    ]


def decode_8421(value: int) -> Tuple[int, bool]:
    if 0 <= value <= 9:
        return value, True
    return -1, False


def encode_8421(value: int) -> int:
    if 0 <= value <= 9:
        return value
    return 0


def get_decoder_8421_equations() -> List[Equation]:
    input_vars = ["I3", "I2", "I1", "I0"]
    output_minterms: dict[str, List[int]] = {"O3": [], "O2": [], "O1": [], "O0": []}
    dont_care_terms: List[int] = []

    for input_value in range(16):
        decoded_value, is_valid = decode_8421(input_value)
        if not is_valid:
            dont_care_terms.append(input_value)
            continue
        if (decoded_value & 8) != 0:
            output_minterms["O3"].append(input_value)
        if (decoded_value & 4) != 0:
            output_minterms["O2"].append(input_value)
        if (decoded_value & 2) != 0:
            output_minterms["O1"].append(input_value)
        if (decoded_value & 1) != 0:
            output_minterms["O0"].append(input_value)

    output_names = ["O3", "O2", "O1", "O0"]
    equations: List[Equation] = []
    for output_name in output_names:
        equations.append(
            Equation(
                name=output_name,
                sdnf="",
                minimized=qm.minimize(
                    DECODER_INPUTS, output_minterms[output_name], dont_care_terms, input_vars
                ),
            )
        )
    return equations


def get_bcd_adder_equations() -> List[Equation]:
    input_vars = ["A3", "A2", "A1", "A0", "B3", "B2", "B1", "B0"]
    output_minterms: dict[str, List[int]] = {
        "S4": [],
        "S3": [],
        "S2": [],
        "S1": [],
        "S0": [],
    }
    dont_care_terms: List[int] = []

    for left_digit in range(16):
        for right_digit in range(16):
            combined_index = (left_digit << 4) | right_digit
            if left_digit > 9 or right_digit > 9:
                dont_care_terms.append(combined_index)
                continue
            sum_value = left_digit + right_digit
            if (sum_value & 16) != 0:
                output_minterms["S4"].append(combined_index)
            if (sum_value & 8) != 0:
                output_minterms["S3"].append(combined_index)
            if (sum_value & 4) != 0:
                output_minterms["S2"].append(combined_index)
            if (sum_value & 2) != 0:
                output_minterms["S1"].append(combined_index)
            if (sum_value & 1) != 0:
                output_minterms["S0"].append(combined_index)

    output_names = ["S4", "S3", "S2", "S1", "S0"]
    equations: List[Equation] = []
    for output_name in output_names:
        equations.append(
            Equation(
                name=output_name,
                sdnf="",
                minimized=qm.minimize(8, output_minterms[output_name], dont_care_terms, input_vars),
            )
        )
    return equations


def get_encoder_8421_equations(offset_n: int) -> List[Equation]:
    input_vars = ["S4", "S3", "S2", "S1", "S0"]
    output_minterms: dict[str, List[int]] = {
        "T3": [],
        "T2": [],
        "T1": [],
        "T0": [],
        "U3": [],
        "U2": [],
        "U1": [],
        "U0": [],
    }
    dont_care_terms: List[int] = []

    for input_value in range(19, 32):
        dont_care_terms.append(input_value)

    for input_value in range(19):
        shifted_value = input_value + offset_n
        tens = shifted_value // 10
        units = shifted_value % 10
        tens_bcd = encode_8421(tens)
        units_bcd = encode_8421(units)

        if (tens_bcd & 8) != 0:
            output_minterms["T3"].append(input_value)
        if (tens_bcd & 4) != 0:
            output_minterms["T2"].append(input_value)
        if (tens_bcd & 2) != 0:
            output_minterms["T1"].append(input_value)
        if (tens_bcd & 1) != 0:
            output_minterms["T0"].append(input_value)

        if (units_bcd & 8) != 0:
            output_minterms["U3"].append(input_value)
        if (units_bcd & 4) != 0:
            output_minterms["U2"].append(input_value)
        if (units_bcd & 2) != 0:
            output_minterms["U1"].append(input_value)
        if (units_bcd & 1) != 0:
            output_minterms["U0"].append(input_value)

    output_names = ["T3", "T2", "T1", "T0", "U3", "U2", "U1", "U0"]
    equations: List[Equation] = []
    for output_name in output_names:
        equations.append(
            Equation(
                name=output_name,
                sdnf="",
                minimized=qm.minimize(
                    ENCODER_INPUTS, output_minterms[output_name], dont_care_terms, input_vars
                ),
            )
        )
    return equations


def get_encoder_8421_equations_offset_n() -> List[Equation]:
    return get_encoder_8421_equations(OFFSET_N)


def get_counter_equations() -> List[Equation]:
    state_vars = ["Q3", "Q2", "Q1", "Q0"]
    toggle_minterms: List[List[int]] = [[], [], [], []]

    for current_state in range(COUNTER_MAX_STATE):
        next_state = (current_state - 1 + COUNTER_MAX_STATE) % COUNTER_MAX_STATE
        toggle_bits = current_state ^ next_state
        for bit_index in range(4):
            if ((toggle_bits >> (3 - bit_index)) & 1) == 1:
                toggle_minterms[bit_index].append(current_state)

    output_names = ["T3", "T2", "T1", "T0"]
    equations: List[Equation] = []
    for bit_index in range(4):
        equations.append(
            Equation(
                name=output_names[bit_index],
                sdnf="",
                minimized=qm.minimize(
                    COUNTER_INPUTS, toggle_minterms[bit_index], None, state_vars
                ),
            )
        )
    return equations
