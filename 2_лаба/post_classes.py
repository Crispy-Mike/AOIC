"""Классы Поста: T0, T1, S, M, L."""

from typing import Dict, List
from truth_table import TruthTable


class PostClasses:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)
        self.values = truth_table.get_function_values()

    def belongs_to_t0(self) -> bool:
        return self.values[0] == 0

    def belongs_to_t1(self) -> bool:
        return self.values[-1] == 1

    def belongs_to_s(self) -> bool:
        num_rows = len(self.values)
        for i in range(num_rows):
            inverted_index = num_rows - 1 - i
            if self.values[i] == self.values[inverted_index]:
                return False
        return True

    def belongs_to_m(self) -> bool:
        num_rows = len(self.values)
        for i in range(num_rows):
            for j in range(i + 1, num_rows):
                if self._is_less_or_equal(i, j):
                    if self.values[i] > self.values[j]:
                        return False
        return True

    def _is_less_or_equal(self, idx1: int, idx2: int) -> bool:
        row1 = self.truth_table.rows[idx1]
        row2 = self.truth_table.rows[idx2]
        for var in self.variables:
            if row1['inputs'][var] and not row2['inputs'][var]:
                return False
        return True

    def belongs_to_l(self) -> bool:
        coefficients = self._compute_zhegalkin_coefficients()
        for mask in range(1, 1 << self.num_vars):
            degree = bin(mask).count('1')
            if degree > 1 and coefficients[mask]:
                return False
        return True

    def _compute_zhegalkin_coefficients(self) -> List[int]:
        coeffs = self.values.copy()
        for i in range(self.num_vars):
            for mask in range(1 << self.num_vars):
                if mask & (1 << i):
                    coeffs[mask] ^= coeffs[mask ^ (1 << i)]
        return coeffs

    def get_all_classes(self) -> Dict[str, bool]:
        return {
            'T0': self.belongs_to_t0(),
            'T1': self.belongs_to_t1(),
            'S': self.belongs_to_s(),
            'M': self.belongs_to_m(),
            'L': self.belongs_to_l()
        }

    def is_complete(self) -> bool:
        classes = self.get_all_classes()
        return not any(classes.values())

    def display(self) -> str:
        classes = self.get_all_classes()
        lines = ["Принадлежность к классам Поста:"]
        class_descriptions = {
            'T0': 'Сохраняющие ноль',
            'T1': 'Сохраняющие единицу',
            'S': 'Самодвойственные',
            'M': 'Монотонные',
            'L': 'Линейные'
        }
        for class_name, belongs in classes.items():
            status = "Принадлежит" if belongs else "Не принадлежит"
            desc = class_descriptions[class_name]
            lines.append(f"  {class_name} ({desc}): {status}")
        completeness = "Полная" if self.is_complete() else "Неполная"
        lines.append(f"\nСистема: {completeness}")
        return "\n".join(lines)
