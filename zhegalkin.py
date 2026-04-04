"""Построение полинома Жегалкина."""

from typing import List, Dict, Tuple
from truth_table import TruthTable


class ZhegalkinPolynomial:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)
        self.values = truth_table.get_function_values()
        self.coefficients: List[int] = []
        self._compute_coefficients()

    def _compute_coefficients(self) -> None:
        self.coefficients = self.values.copy()
        for i in range(self.num_vars):
            for mask in range(1 << self.num_vars):
                if mask & (1 << i):
                    self.coefficients[mask] ^= self.coefficients[mask ^ (1 << i)]

    def _mask_to_monomial(self, mask: int) -> str:
        if mask == 0:
            return "1"
        terms = []
        for i, var in enumerate(self.variables):
            if mask & (1 << (self.num_vars - 1 - i)):
                terms.append(var)
        return "".join(terms)

    def get_polynomial(self) -> str:
        terms = []
        for mask in range(1 << self.num_vars):
            if self.coefficients[mask]:
                terms.append(self._mask_to_monomial(mask))
        if not terms:
            return "0"
        return " ^ ".join(terms)

    def get_coefficients(self) -> List[int]:
        return self.coefficients.copy()

    def get_terms(self) -> List[Tuple[int, str]]:
        terms = []
        for mask in range(1 << self.num_vars):
            if self.coefficients[mask]:
                terms.append((mask, self._mask_to_monomial(mask)))
        return terms

    def display_table(self) -> str:
        lines = ["Коэффициенты полинома Жегалкина:", "-" * 40]
        for mask in range(1 << self.num_vars):
            monomial = self._mask_to_monomial(mask)
            coeff = self.coefficients[mask]
            lines.append(f"  {monomial:>10}: {coeff}")
        return "\n".join(lines)
