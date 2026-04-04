"""Построение СДНФ и СКНФ."""

from typing import List, Dict
from truth_table import TruthTable


class NormalForm:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)

    def _literal_to_string(self, var: str, value: bool) -> str:
        return var if value else f"!{var}"

    def _minterm_to_string(self, row: Dict) -> str:
        literals = [self._literal_to_string(var, row['inputs'][var]) for var in self.variables]
        return "".join(f"({lit})" for lit in literals)

    def _maxterm_to_string(self, row: Dict) -> str:
        literals = [self._literal_to_string(var, not row['inputs'][var]) for var in self.variables]
        return "".join(f"({lit})" for lit in literals)

    def build_sdnf(self) -> str:
        true_rows = self.truth_table.get_true_rows()
        if not true_rows:
            return "0"
        minterms = [self._minterm_to_string(row) for row in true_rows]
        return " v ".join(minterms)

    def build_sknf(self) -> str:
        false_rows = self.truth_table.get_false_rows()
        if not false_rows:
            return "1"
        maxterms = [self._maxterm_to_string(row) for row in false_rows]
        return " & ".join(maxterms)

    def get_sdnf_numeric(self) -> List[int]:
        return self.truth_table.get_true_indices()

    def get_sknf_numeric(self) -> List[int]:
        return self.truth_table.get_false_indices()

    def get_sdnf_index_form(self) -> str:
        """Индексная форма СДНФ - номера наборов, где F=1."""
        indices = self.truth_table.get_true_indices()
        return f"sum({', '.join(map(str, indices))})"

    def get_sknf_index_form(self) -> str:
        """Индексная форма СКНФ - номера наборов, где F=0."""
        indices = self.truth_table.get_false_indices()
        return f"prod({', '.join(map(str, indices))})"

    def get_function_index_form(self) -> str:
        """Индексная форма функции - просто столбец значений."""
        function_values = self.truth_table.get_function_values()
        return f"F = ({', '.join(map(str, function_values))})"

    def get_function_vector_decimal(self) -> int:
        """Десятичное представление вектора функции."""
        function_values = self.truth_table.get_function_values()
        binary_str = ''.join(map(str, function_values))
        return int(binary_str, 2)
