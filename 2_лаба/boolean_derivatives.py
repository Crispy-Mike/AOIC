"""Булево дифференцирование: частные и смешанные производные."""

from typing import List, Dict, Tuple
from itertools import combinations
from truth_table import TruthTable


class BooleanDerivatives:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)
        self.values = truth_table.get_function_values()

    def partial_derivative(self, var: str) -> List[int]:
        if var not in self.variables:
            raise ValueError(f"Переменная {var} не найдена")
        derivative = []
        for row in self.truth_table.rows:
            inputs_with_0 = row['inputs'].copy()
            inputs_with_0[var] = False
            index_0 = self._find_row_index(inputs_with_0)
            val_0 = self.values[index_0]

            inputs_with_1 = row['inputs'].copy()
            inputs_with_1[var] = True
            index_1 = self._find_row_index(inputs_with_1)
            val_1 = self.values[index_1]

            derivative.append(1 if val_0 != val_1 else 0)
        return derivative

    def mixed_derivative(self, vars_list: List[str]) -> List[int]:
        if len(vars_list) < 2:
            raise ValueError("Смешанная производная требует минимум 2 переменных")
        if len(vars_list) > 4:
            raise ValueError("Смешанная производная поддерживает до 4 переменных")
        for var in vars_list:
            if var not in self.variables:
                raise ValueError(f"Переменная {var} не найдена")

        current_values = self.values.copy()
        for var in vars_list:
            current_values = self._compute_derivative_from_values(current_values, var)
        return current_values

    def _compute_derivative_from_values(self, values: List[int], var: str) -> List[int]:
        derivative = []
        for i, row in enumerate(self.truth_table.rows):
            modified_inputs = row['inputs'].copy()
            modified_inputs[var] = not modified_inputs[var]
            modified_index = self._find_row_index(modified_inputs)
            derivative.append(values[i] ^ values[modified_index])
        return derivative

    def _find_row_index(self, inputs: Dict[str, bool]) -> int:
        for i, row in enumerate(self.truth_table.rows):
            if row['inputs'] == inputs:
                return i
        raise ValueError("Строка не найдена")

    def get_all_partial_derivatives(self) -> Dict[str, List[int]]:
        return {var: self.partial_derivative(var) for var in self.variables}

    def get_all_mixed_derivatives(self, order: int = 2) -> Dict[Tuple[str, ...], List[int]]:
        if order < 2 or order > 4:
            raise ValueError("Порядок смешанной производной должен быть от 2 до 4")
        derivatives = {}
        for vars_combo in combinations(self.variables, order):
            derivatives[vars_combo] = self.mixed_derivative(list(vars_combo))
        return derivatives

    def derivative_to_expression(self, derivative: List[int]) -> str:
        terms = []
        for i, val in enumerate(derivative):
            if val:
                row = self.truth_table.rows[i]
                literals = []
                for var in self.variables:
                    if row['inputs'][var]:
                        literals.append(var)
                    else:
                        literals.append(f"!{var}")
                term = "".join(f"({lit})" for lit in literals)
                terms.append(term)
        if not terms:
            return "0"
        return " ^ ".join(terms)

    def display_partial_derivatives(self) -> str:
        lines = ["Частные производные первого порядка:", "-" * 50]
        derivatives = self.get_all_partial_derivatives()
        for var, values in derivatives.items():
            expression = self.derivative_to_expression(values)
            lines.append(f"  df/d{var} = {expression}")
        return "\n".join(lines)

    def display_mixed_derivatives(self, order: int = 2) -> str:
        lines = [f"Смешанные производные порядка {order}:", "-" * 50]
        derivatives = self.get_all_mixed_derivatives(order)
        for vars_tuple, values in derivatives.items():
            var_str = "".join(vars_tuple)
            expression = self.derivative_to_expression(values)
            lines.append(f"  d^{order}f/d{var_str} = {expression}")
        return "\n".join(lines)
