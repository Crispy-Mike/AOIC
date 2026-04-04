"""Поиск фиктивных переменных."""

from typing import List, Dict
from truth_table import TruthTable


class DummyVariables:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)
        self.values = truth_table.get_function_values()

    def is_dummy(self, var: str) -> bool:
        for i, row in enumerate(self.truth_table.rows):
            modified_inputs = row['inputs'].copy()
            modified_inputs[var] = not modified_inputs[var]
            modified_index = self._find_row_index(modified_inputs)
            if self.values[i] != self.values[modified_index]:
                return False
        return True

    def _find_row_index(self, inputs: Dict[str, bool]) -> int:
        for i, row in enumerate(self.truth_table.rows):
            if row['inputs'] == inputs:
                return i
        raise ValueError("Строка не найдена")

    def get_dummy_variables(self) -> List[str]:
        return [var for var in self.variables if self.is_dummy(var)]

    def get_essential_variables(self) -> List[str]:
        return [var for var in self.variables if not self.is_dummy(var)]

    def display(self) -> str:
        dummy = self.get_dummy_variables()
        essential = self.get_essential_variables()
        lines = ["Информация о переменных:"]
        if dummy:
            lines.append(f"  Фиктивные переменные: {', '.join(dummy)}")
        else:
            lines.append("  Фиктивные переменные: отсутствуют")
        if essential:
            lines.append(f"  Существенные переменные: {', '.join(essential)}")
        else:
            lines.append("  Существенные переменные: отсутствуют")
        return "\n".join(lines)
