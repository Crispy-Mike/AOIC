from __future__ import annotations

import circuits


def _print_equations(section_title: str, equation_list, include_sdnf: bool = False) -> None:
    print(section_title)
    for equation in equation_list:
        if include_sdnf:
            print(
                f"{equation.name}:\nSDNF: {equation.sdnf}\nMinimized: {equation.minimized}\n"
            )
        else:
            print(f"{equation.name} = {equation.minimized}")
    print()


def main() -> None:
    _print_equations("ОДВ-3", circuits.get_subtractor_equations(), True)
    _print_equations("8421 BCD -> Двоичный", circuits.get_decoder_8421_equations())
    _print_equations("Сумматор 8421 + 8421 -> двоичная сумма", circuits.get_bcd_adder_equations())
    _print_equations(
        "Двоичный -> 8421 BCD (смещение n=9, десятки/единицы)",
        circuits.get_encoder_8421_equations_offset_n(),
    )
    _print_equations(
        "Двоичный счетчик вычитающего типа на 16 внутренних состояний в базисе НЕ-И ИЛИ и Т-триггер.",
        circuits.get_counter_equations(),
    )


if __name__ == "__main__":
    main()
