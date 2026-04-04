"""Главный модуль лабораторной работы 2. Построение СКНФ и СДНФ."""

from typing import Dict, Any
from parser import parse_expression, get_all_variables
from truth_table import TruthTable
from normal_forms import NormalForm
from post_classes import PostClasses
from zhegalkin import ZhegalkinPolynomial
from dummy_variables import DummyVariables
from boolean_derivatives import BooleanDerivatives
from minimization import Minimization


class BooleanFunctionAnalyzer:
    def __init__(self, expression: str):
        self.expression = expression
        self.truth_table = TruthTable(expression)
        self.normal_forms = NormalForm(self.truth_table)
        self.post_classes = PostClasses(self.truth_table)
        self.zhegalkin = ZhegalkinPolynomial(self.truth_table)
        self.dummy_vars = DummyVariables(self.truth_table)
        self.derivatives = BooleanDerivatives(self.truth_table)
        self.minimization = Minimization(self.truth_table)

    def analyze(self) -> Dict[str, Any]:
        return {
            'expression': self.expression,
            'variables': self.truth_table.variables,
            'truth_table': self.truth_table.display(),
            'sdnf': self.normal_forms.build_sdnf(),
            'sknf': self.normal_forms.build_sknf(),
            'sdnf_numeric': self.normal_forms.get_sdnf_numeric(),
            'sknf_numeric': self.normal_forms.get_sknf_numeric(),
            'sdnf_index': self.normal_forms.get_sdnf_index_form(),
            'sknf_index': self.normal_forms.get_sknf_index_form(),
            'function_index': self.normal_forms.get_function_index_form(),
            'function_vector_decimal': self.normal_forms.get_function_vector_decimal(),
            'post_classes': self.post_classes.get_all_classes(),
            'post_display': self.post_classes.display(),
            'zhegalkin': self.zhegalkin.get_polynomial(),
            'zhegalkin_table': self.zhegalkin.display_table(),
            'dummy_variables': self.dummy_vars.display(),
            'partial_derivatives': self.derivatives.display_partial_derivatives(),
            'minimized_dnf_calculated': self._minimize_dnf_calculated_full(),
            'minimized_dnf_table': self._minimize_dnf_table_full(),
            'minimized_dnf_karnaugh': self._minimize_dnf_karnaugh_full(),
            'minimized_cnf_calculated': self._minimize_cnf_calculated_full(),
            'minimized_cnf_table': self._minimize_cnf_table_full()
        }

    def _minimize_dnf_calculated_full(self) -> str:
        implicants, history = self.minimization.minimize_calculated()
        lines = history.copy()
        lines.append(f"\nМинимизированная ДНФ: {self.minimization.get_minimized_dnf(implicants)}")
        return "\n".join(lines)

    def _minimize_dnf_table_full(self) -> str:
        implicants, table, history = self.minimization.minimize_calculated_table()
        lines = history.copy()
        lines.append(table)
        lines.append(f"\nМинимизированная ДНФ: {self.minimization.get_minimized_dnf(implicants)}")
        return "\n".join(lines)

    def _minimize_dnf_karnaugh_full(self) -> str:
        try:
            implicants, kmap_display = self.minimization.minimize_karnaugh()
            lines = [kmap_display]
            lines.append(f"\nМинимизированная ДНФ: {self.minimization.get_minimized_dnf(implicants)}")
            return "\n".join(lines)
        except ValueError as e:
            return f"Карта Карно не поддерживается: {e}"

    def _minimize_cnf_calculated_full(self) -> str:
        maxterms, history = self.minimization.minimize_cnf_calculated()
        lines = history.copy()
        lines.append(f"\nМинимизированная КНФ: {self.minimization.get_minimized_cnf(maxterms)}")
        return "\n".join(lines)

    def _minimize_cnf_table_full(self) -> str:
        maxterms, table, history = self.minimization.minimize_cnf_calculated_table()
        lines = history.copy()
        lines.append(table)
        lines.append(f"\nМинимизированная КНФ: {self.minimization.get_minimized_cnf(maxterms)}")
        return "\n".join(lines)

    def _print_final_minimization(self, results: Dict[str, Any]) -> None:
        """Вывод итоговых МДНФ и МКНФ."""
        implicants, _ = self.minimization.minimize_calculated()
        mdnf = self.minimization.get_minimized_dnf(implicants)

        maxterms, _ = self.minimization.minimize_cnf_calculated()
        mknf = self.minimization.get_minimized_cnf(maxterms)

        print(f"МДНФ: {mdnf}")
        print(f"МКНФ: {mknf}")

    def print_full_report(self) -> None:
        results = self.analyze()

        print("=" * 60)
        print("ЛАБОРАТОРНАЯ РАБОТА 2")
        print("Построение СКНФ и СДНФ на основании таблиц истинности")
        print("=" * 60)

        print(f"\n1. Исходное выражение: {results['expression']}")
        print(f"   Переменные: {', '.join(results['variables'])}")

        print(f"\n2. Таблица истинности:")
        print(results['truth_table'])

        print(f"\n3. СДНФ:")
        print(f"   {results['sdnf']}")
        print(f"   Числовая форма: {results['sdnf_numeric']}")
        print(f"   Индексная форма: {results['sdnf_index']}")

        print(f"\n4. СКНФ:")
        print(f"   {results['sknf']}")
        print(f"   Числовая форма: {results['sknf_numeric']}")
        print(f"   Индексная форма: {results['sknf_index']}")

        print(f"\n5. Индексная форма функции:")
        print(f"   {results['function_index']}")
        print(f"   Десятичное значение: {results['function_vector_decimal']}")

        print(f"\n6. {results['post_display']}")

        print(f"\n7. Полином Жегалкина:")
        print(f"   {results['zhegalkin']}")

        print(f"\n8. {results['dummy_variables']}")

        print(f"\n9. Частные производные:")
        print(results['partial_derivatives'])

        print(f"\n10. Минимизация ДНФ расчетным методом:")
        print(results['minimized_dnf_calculated'])

        print(f"\n11. Минимизация ДНФ расчетно-табличным методом:")
        print(results['minimized_dnf_table'])

        print(f"\n12. Минимизация ДНФ картой Карно:")
        print(results['minimized_dnf_karnaugh'])

        print(f"\n13. Минимизация КНФ расчетным методом:")
        print(results['minimized_cnf_calculated'])

        print(f"\n14. Минимизация КНФ расчетно-табличным методом:")
        print(results['minimized_cnf_table'])

        # Итоговые строки МДНФ и МКНФ
        print(f"\n15. Итоговые результаты минимизации:")
        self._print_final_minimization(results)

        print("\n" + "=" * 60)


def main():
    print("Программа для анализа булевых функций")
    print("Поддерживаемые операции: & (AND), | (OR), ! (NOT), -> (IMPLIES), ~ (XOR)")
    print("Переменные: a, b, c, d, e (до 5 переменных)")
    print("Пример: !(!a->!b)|c\n")

    while True:
        try:
            expression = input("Введите логическое выражение (или 'exit' для выхода): ").strip()
            if expression.lower() == 'exit':
                print("Выход из программы.")
                break
            if not expression:
                print("Выражение не может быть пустым.\n")
                continue

            analyzer = BooleanFunctionAnalyzer(expression)
            analyzer.print_full_report()
            print()

        except ValueError as e:
            print(f"Ошибка: {e}\n")
        except KeyboardInterrupt:
            print("\n\nВыход из программы.")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}\n")


if __name__ == "__main__":
    main()
