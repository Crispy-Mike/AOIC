"""Минимизация булевых функций: расчетный, расчетно-табличный, карта Карно."""

from typing import List, Dict, Tuple, Set, Optional
from itertools import combinations
from truth_table import TruthTable


class Maxterm:
    def __init__(self, variables: List[str], values: List[Optional[bool]], maxterms: List[int]):
        self.variables = variables
        self.values = values
        self.maxterms = set(maxterms)
        self.used = False

    def __repr__(self) -> str:
        return f"Maxterm({self.to_string()}, {sorted(self.maxterms)})"

    def to_string(self) -> str:
        terms = []
        for var, val in zip(self.variables, self.values):
            if val is None:
                continue
            elif val:
                terms.append(f"!{var}")
            else:
                terms.append(var)
        if not terms:
            return "0"
        return " v ".join(f"({term})" for term in terms)

    def to_pattern(self) -> str:
        pattern = []
        for val in self.values:
            if val is None:
                pattern.append("X")
            elif val:
                pattern.append("1")
            else:
                pattern.append("0")
        return "".join(pattern)

    def covers(self, maxterm: int) -> bool:
        return maxterm in self.maxterms

    def __eq__(self, other) -> bool:
        if not isinstance(other, Maxterm):
            return False
        return self.variables == other.variables and self.values == other.values

    def __hash__(self) -> int:
        return hash(tuple(self.values))


class Implicant:
    def __init__(self, variables: List[str], values: List[Optional[bool]], minterms: List[int]):
        self.variables = variables
        self.values = values
        self.minterms = set(minterms)
        self.used = False

    def __repr__(self) -> str:
        return f"Implicant({self.to_string()}, {sorted(self.minterms)})"

    def to_string(self) -> str:
        terms = []
        for var, val in zip(self.variables, self.values):
            if val is None:
                continue
            elif val:
                terms.append(var)
            else:
                terms.append(f"!{var}")
        if not terms:
            return "1"
        return "".join(terms)

    def to_pattern(self) -> str:
        pattern = []
        for val in self.values:
            if val is None:
                pattern.append("X")
            elif val:
                pattern.append("1")
            else:
                pattern.append("0")
        return "".join(pattern)

    def covers(self, minterm: int) -> bool:
        return minterm in self.minterms

    def __eq__(self, other) -> bool:
        if not isinstance(other, Implicant):
            return False
        return self.variables == other.variables and self.values == other.values

    def __hash__(self) -> int:
        return hash(tuple(self.values))


class Minimization:
    def __init__(self, truth_table: TruthTable):
        self.truth_table = truth_table
        self.variables = truth_table.variables
        self.num_vars = len(self.variables)
        self.true_indices = truth_table.get_true_indices()

    def _create_minterm_implicant(self, index: int) -> Implicant:
        values = []
        for i in range(self.num_vars - 1, -1, -1):
            values.append(bool(index & (1 << i)))
        return Implicant(self.variables, values, [index])

    def _can_combine(self, imp1: Implicant, imp2: Implicant) -> bool:
        diff_count = 0
        for v1, v2 in zip(imp1.values, imp2.values):
            if v1 != v2:
                if v1 is not None and v2 is not None:
                    diff_count += 1
                else:
                    return False
        return diff_count == 1

    def _combine_implicants(self, imp1: Implicant, imp2: Implicant) -> Implicant:
        new_values = []
        for v1, v2 in zip(imp1.values, imp2.values):
            if v1 != v2:
                new_values.append(None)
            else:
                new_values.append(v1)
        new_minterms = list(imp1.minterms | imp2.minterms)
        return Implicant(self.variables, new_values, new_minterms)

    def minimize_calculated(self) -> Tuple[List[Implicant], List[str]]:
        history = []
        current_implicants = [
            self._create_minterm_implicant(idx) for idx in self.true_indices
        ]
        history.append(f"Исходные минтермы: {[imp.to_string() for imp in current_implicants]}")

        # Храним все "простые импликанты" (prime implicants)
        all_prime = set()
        stage = 1
        while True:
            new_implicants = []
            used_indices = set()
            seen_combinations = set()

            for i, imp1 in enumerate(current_implicants):
                for j, imp2 in enumerate(current_implicants):
                    if i >= j:
                        continue
                    pair = (i, j)
                    if pair in seen_combinations:
                        continue
                    if self._can_combine(imp1, imp2):
                        combined = self._combine_implicants(imp1, imp2)
                        # Проверяем уникальность
                        key = tuple(combined.values)
                        if not any(tuple(imp.values) == key for imp in new_implicants):
                            new_implicants.append(combined)
                        used_indices.add(i)
                        used_indices.add(j)
                        seen_combinations.add(pair)

            # Те, что не были использованы — простые импликанты
            for idx, imp in enumerate(current_implicants):
                if idx not in used_indices:
                    all_prime.add(tuple(imp.values))

            if not new_implicants:
                # Все текущие тоже простые
                for imp in current_implicants:
                    all_prime.add(tuple(imp.values))
                break

            history.append(f"\nЭтап склеивания {stage}:")
            for imp in new_implicants:
                history.append(f"  {imp.to_string()} ({imp.to_pattern()})")
            current_implicants = new_implicants
            stage += 1

        # Восстанавливаем Implicant из prime implicants
        prime_implicants = []
        for values_tuple in all_prime:
            # Восстанавливаем minterms
            implicant = Implicant(self.variables, list(values_tuple), [])
            # Определяем какие минтермы покрываются
            minterms = []
            for mi in self.true_indices:
                if self._implicant_covers_minterm(implicant, mi):
                    minterms.append(mi)
            implicant.minterms = set(minterms)
            prime_implicants.append(implicant)

        history.append("\nПроверка на лишние импликанты:")
        final_implicants = self._find_minimal_cover(prime_implicants, history)
        return final_implicants, history

    def _implicant_covers_minterm(self, imp: Implicant, minterm: int) -> bool:
        """Проверяет, покрывает ли импликант данный минтерм."""
        idx = minterm
        for i in range(self.num_vars - 1, -1, -1):
            bit = bool(idx & (1 << i))
            val = imp.values[self.num_vars - 1 - i]
            if val is not None and val != bit:
                return False
        return True

    def _find_minimal_cover(self, prime_implicants: List[Implicant], history: List[str]) -> List[Implicant]:
        """Находит минимальное покрытие с помощью существенных импликант."""
        if not prime_implicants:
            return []

        # Находим существенно необходимые импликанты
        essential = []
        covered_minterms = set()

        # Для каждого минтерма считаем сколько импликант его покрывают
        for minterm in self.true_indices:
            covering = [imp for imp in prime_implicants if minterm in imp.minterms]
            if len(covering) == 1:
                # Существенная импликанта
                ess = covering[0]
                if ess not in essential:
                    essential.append(ess)
                    history.append(f"  {ess.to_string()} - необходимая импликанта")
                    covered_minterms.update(ess.minterms)

        # Отмечаем необязательные
        for imp in prime_implicants:
            if imp not in essential:
                history.append(f"  {imp.to_string()} - лишняя импликанта")

        # Если не все покрыты — жадно добавляем
        uncovered = [m for m in self.true_indices if m not in covered_minterms]
        remaining = [imp for imp in prime_implicants if imp not in essential]

        while uncovered:
            best_imp = max(remaining, key=lambda imp: len(imp.minterms & set(uncovered)))
            essential.append(best_imp)
            covered_minterms.update(best_imp.minterms)
            uncovered = [m for m in self.true_indices if m not in covered_minterms]
            remaining.remove(best_imp)

        return essential

    def minimize_calculated_table(self) -> Tuple[List[Implicant], str, List[str]]:
        history = []
        implicants, calc_history = self.minimize_calculated()
        history.extend(calc_history)

        table_lines = ["\nТаблица покрытия:"]
        header = "Импликанта | " + " ".join(f"{m:>3}" for m in self.true_indices)
        table_lines.append(header)
        table_lines.append("-" * len(header))

        for imp in implicants:
            row = f"{imp.to_string():>10} |"
            for m in self.true_indices:
                row += "  X " if imp.covers(m) else "    "
            table_lines.append(row)

        return implicants, "\n".join(table_lines), history

    def minimize_karnaugh(self) -> Tuple[List[Implicant], str]:
        if self.num_vars < 2 or self.num_vars > 4:
            raise ValueError("Карта Карно поддерживается для 2-4 переменных")
        if self.num_vars == 2:
            return self._karnaugh_2var()
        elif self.num_vars == 3:
            return self._karnaugh_3var()
        else:
            return self._karnaugh_4var()

    def _karnaugh_2var(self) -> Tuple[List[Implicant], str]:
        var_a, var_b = self.variables
        kmap = [[0, 0], [0, 0]]
        for idx in self.true_indices:
            a = (idx >> 1) & 1
            b = idx & 1
            kmap[a][b] = 1

        lines = ["\nКарта Карно:", f"      {var_b}=0  {var_b}=1", "  +-----------+"]
        lines.append(f"{var_a}=0 |  {kmap[0][0]}    {kmap[0][1]}")
        lines.append(f"{var_a}=1 |  {kmap[1][0]}    {kmap[1][1]}")

        implicants = self._find_groups_2var(kmap)
        return implicants, "\n".join(lines)

    def _find_groups_2var(self, kmap: List[List[int]]) -> List[Implicant]:
        implicants = []
        covered = set()

        if all(kmap[i][j] == 1 for i in range(2) for j in range(2)):
            return [Implicant(self.variables, [None, None], [0, 1, 2, 3])]

        for i in range(2):
            for j in range(2):
                if kmap[i][j] == 1 and (i, j) not in covered:
                    group = self._try_group_2var(kmap, i, j, covered)
                    if group:
                        implicants.append(self._group_to_implicant_2var(group))
                        covered.update(group)
        return implicants

    def _try_group_2var(self, kmap, row, col, covered):
        if col == 0 and kmap[row][1] == 1 and (row, 1) not in covered:
            return {(row, 0), (row, 1)}
        if col == 1 and kmap[row][0] == 1 and (row, 0) not in covered:
            return {(row, 0), (row, 1)}
        if row == 0 and kmap[1][col] == 1 and (1, col) not in covered:
            return {(0, col), (1, col)}
        if row == 1 and kmap[0][col] == 1 and (0, col) not in covered:
            return {(0, col), (1, col)}
        return {(row, col)}

    def _group_to_implicant_2var(self, group) -> Implicant:
        values = [None, None]
        rows = list(set(r for r, c in group))
        cols = list(set(c for r, c in group))
        if len(rows) == 1:
            values[0] = bool(rows[0])
        if len(cols) == 1:
            values[1] = bool(cols[0])
        minterms = [(r << 1) | c for r, c in group]
        return Implicant(self.variables, values, minterms)

    def _karnaugh_3var(self) -> Tuple[List[Implicant], str]:
        var_a, var_b, var_c = self.variables
        kmap = [[0, 0, 0, 0], [0, 0, 0, 0]]
        gray_order = [0, 1, 3, 2]

        for idx in self.true_indices:
            a = (idx >> 2) & 1
            bc = idx & 3
            col = gray_order.index(bc)
            kmap[a][col] = 1

        lines = ["\nКарта Карно:", f"       {var_b}{var_c}=00  01  11  10", "   +--------------------+"]
        lines.append(f"{var_a}=0 |  {kmap[0][0]}    {kmap[0][1]}   {kmap[0][2]}   {kmap[0][3]}")
        lines.append(f"{var_a}=1 |  {kmap[1][0]}    {kmap[1][1]}   {kmap[1][2]}   {kmap[1][3]}")

        implicants = self._find_groups_3var(kmap, gray_order)
        return implicants, "\n".join(lines)

    def _find_groups_3var(self, kmap: List[List[int]], gray_order: List[int]) -> List[Implicant]:
        implicants = []
        covered = set()

        # Группы по 4 (вся строка)
        for row in range(2):
            if all(kmap[row][c] == 1 for c in range(4)):
                group = {(row, c) for c in range(4)}
                if not group <= covered:
                    implicants.append(self._group_to_implicant_3var(group, gray_order))
                    covered.update(group)

        # Группы по 4 (квадрат 2x2) - соседние колонки в порядке Грея
        for col in range(4):
            next_col = (col + 1) % 4
            if all(kmap[r][col] == 1 and kmap[r][next_col] == 1 for r in range(2)):
                group = {(r, c) for r in range(2) for c in [col, next_col]}
                if not group <= covered:
                    implicants.append(self._group_to_implicant_3var(group, gray_order))
                    covered.update(group)

        # Группы по 2 и 1
        for row in range(2):
            for col in range(4):
                if (row, col) in covered or kmap[row][col] == 0:
                    continue
                found = False
                # Горизонтальная пара
                next_col = (col + 1) % 4
                if kmap[row][next_col] == 1 and (row, next_col) not in covered:
                    group = {(row, col), (row, next_col)}
                    implicants.append(self._group_to_implicant_3var(group, gray_order))
                    covered.update(group)
                    found = True
                # Вертикальная пара
                elif not found and kmap[1 - row][col] == 1:
                    group = {(row, col), (1 - row, col)}
                    implicants.append(self._group_to_implicant_3var(group, gray_order))
                    covered.update(group)
                    found = True
                # Одиночная
                if not found:
                    group = {(row, col)}
                    implicants.append(self._group_to_implicant_3var(group, gray_order))
                    covered.add((row, col))
        return implicants

    def _group_to_implicant_3var(self, group, gray_order) -> Implicant:
        values = [None, None, None]
        rows = list(set(r for r, c in group))
        cols = list(set(c for r, c in group))

        if len(rows) == 1:
            values[0] = bool(rows[0])

        if len(cols) == 1:
            bc_val = gray_order[cols[0]]
            values[1] = bool(bc_val & 2)
            values[2] = bool(bc_val & 1)
        elif len(cols) == 2:
            col_vals = [gray_order[c] for c in cols]
            if all(v & 2 == col_vals[0] & 2 for v in col_vals):
                values[1] = bool(col_vals[0] & 2)
            if all(v & 1 == col_vals[0] & 1 for v in col_vals):
                values[2] = bool(col_vals[0] & 1)

        minterms = []
        for r, c in group:
            bc_val = gray_order[c]
            idx = (r << 2) | bc_val
            minterms.append(idx)
        return Implicant(self.variables, values, minterms)

    def _karnaugh_4var(self) -> Tuple[List[Implicant], str]:
        var_a, var_b, var_c, var_d = self.variables
        kmap = [[0] * 4 for _ in range(4)]
        gray_order = [0, 1, 3, 2]

        for idx in self.true_indices:
            ab = (idx >> 2) & 3
            cd = idx & 3
            row = gray_order.index(ab)
            col = gray_order.index(cd)
            kmap[row][col] = 1

        lines = ["\nКарта Карно:", f"         {var_c}{var_d}=00  01  11  10", "     +--------------------------+"]
        lines.append(f"{var_a}{var_b}=00 |  {kmap[0][0]}    {kmap[0][1]}   {kmap[0][2]}   {kmap[0][3]}")
        lines.append(f"{var_a}{var_b}=01 |  {kmap[1][0]}    {kmap[1][1]}   {kmap[1][2]}   {kmap[1][3]}")
        lines.append(f"{var_a}{var_b}=11 |  {kmap[2][0]}    {kmap[2][1]}   {kmap[2][2]}   {kmap[2][3]}")
        lines.append(f"{var_a}{var_b}=10 |  {kmap[3][0]}    {kmap[3][1]}   {kmap[3][2]}   {kmap[3][3]}")

        implicants = self._find_groups_4var(kmap, gray_order)
        return implicants, "\n".join(lines)

    def _find_groups_4var(self, kmap: List[List[int]], gray_order: List[int]) -> List[Implicant]:
        implicants = []
        covered = set()

        # Группа 16
        if all(kmap[i][j] == 1 for i in range(4) for j in range(4)):
            return [Implicant(self.variables, [None, None, None, None], list(range(16)))]

        # Группы по 8
        for i in range(3):
            # Две строки
            if all(kmap[i][c] == 1 and kmap[i+1][c] == 1 for c in range(4)):
                group = {(r, c) for r in [i, i+1] for c in range(4)}
                if not group <= covered:
                    implicants.append(self._group_to_implicant_4var(group, gray_order))
                    covered.update(group)
            # Две колонки
            if all(kmap[r][i] == 1 and kmap[r][i+1] == 1 for r in range(4)):
                group = {(r, c) for r in range(4) for c in [i, i+1]}
                if not group <= covered:
                    implicants.append(self._group_to_implicant_4var(group, gray_order))
                    covered.update(group)

        # Группы по 4
        # Квадраты 2x2
        for i in range(3):
            for j in range(3):
                group = {(r, c) for r in [i, i+1] for c in [j, j+1]}
                if all(kmap[r][c] == 1 for r, c in group) and not group <= covered:
                    implicants.append(self._group_to_implicant_4var(group, gray_order))
                    covered.update(group)
        # Строки по 4
        for i in range(4):
            group = {(i, c) for c in range(4)}
            if all(kmap[i][c] == 1 for c in range(4)) and not group <= covered:
                implicants.append(self._group_to_implicant_4var(group, gray_order))
                covered.update(group)
        # Колонки по 4
        for j in range(4):
            group = {(r, j) for r in range(4)}
            if all(kmap[r][j] == 1 for r in range(4)) and not group <= covered:
                implicants.append(self._group_to_implicant_4var(group, gray_order))
                covered.update(group)

        # Группы по 2
        for i in range(4):
            for j in range(4):
                if (i, j) in covered or kmap[i][j] == 0:
                    continue
                found = False
                # Горизонтальная пара
                next_col = (j + 1) % 4
                if kmap[i][next_col] == 1 and (i, next_col) not in covered:
                    group = {(i, j), (i, next_col)}
                    implicants.append(self._group_to_implicant_4var(group, gray_order))
                    covered.update(group)
                    found = True
                # Вертикальная пара
                elif not found:
                    next_row = (i + 1) % 4
                    if kmap[next_row][j] == 1:
                        group = {(i, j), (next_row, j)}
                        implicants.append(self._group_to_implicant_4var(group, gray_order))
                        covered.update(group)
                        found = True
                # Одиночная
                if not found:
                    group = {(i, j)}
                    implicants.append(self._group_to_implicant_4var(group, gray_order))
                    covered.add((i, j))

        return implicants

    def _group_to_implicant_4var(self, group, gray_order) -> Implicant:
        values = [None, None, None, None]
        rows = list(set(r for r, c in group))
        cols = list(set(c for r, c in group))

        if len(rows) == 1:
            ab_val = gray_order[rows[0]]
            values[0] = bool(ab_val & 2)
            values[1] = bool(ab_val & 1)
        elif len(rows) == 2:
            row_vals = [gray_order[r] for r in rows]
            if all(v & 2 == row_vals[0] & 2 for v in row_vals):
                values[0] = bool(row_vals[0] & 2)
            if all(v & 1 == row_vals[0] & 1 for v in row_vals):
                values[1] = bool(row_vals[0] & 1)

        if len(cols) == 1:
            cd_val = gray_order[cols[0]]
            values[2] = bool(cd_val & 2)
            values[3] = bool(cd_val & 1)
        elif len(cols) == 2:
            col_vals = [gray_order[c] for c in cols]
            if all(v & 2 == col_vals[0] & 2 for v in col_vals):
                values[2] = bool(col_vals[0] & 2)
            if all(v & 1 == col_vals[0] & 1 for v in col_vals):
                values[3] = bool(col_vals[0] & 1)

        minterms = []
        for r, c in group:
            ab_val = gray_order[r]
            cd_val = gray_order[c]
            idx = (ab_val << 2) | cd_val
            minterms.append(idx)
        return Implicant(self.variables, values, minterms)

    def get_minimized_dnf(self, implicants: List[Implicant]) -> str:
        if not implicants:
            return "0"
        terms = [imp.to_string() for imp in implicants]
        return " v ".join(terms)

    def get_minimized_cnf(self, maxterms: List[Maxterm]) -> str:
        if not maxterms:
            return "1"
        terms = [mt.to_string() for mt in maxterms]
        return " & ".join(terms)

    def minimize_cnf_calculated(self) -> Tuple[List[Maxterm], List[str]]:
        """Минимизация КНФ расчетным методом (через нулевые наборы)."""
        history = []
        false_indices = self.truth_table.get_false_indices()

        if not false_indices:
            history.append("Функция тождественно истинна, КНФ = 1")
            return [], history

        current_maxterms = [
            self._create_maxterm(idx) for idx in false_indices
        ]
        history.append(f"Исходные макстермы: {[mt.to_string() for mt in current_maxterms]}")

        # Храним все "простые импликанты" для КНФ
        all_prime = set()
        stage = 1
        while True:
            new_maxterms = []
            used_indices = set()
            seen_combinations = set()

            for i, mt1 in enumerate(current_maxterms):
                for j, mt2 in enumerate(current_maxterms):
                    if i >= j:
                        continue
                    pair = (i, j)
                    if pair in seen_combinations:
                        continue
                    if self._can_combine_maxterms(mt1, mt2):
                        combined = self._combine_maxterms(mt1, mt2)
                        key = tuple(combined.values)
                        if not any(tuple(mt.values) == key for mt in new_maxterms):
                            new_maxterms.append(combined)
                        used_indices.add(i)
                        used_indices.add(j)
                        seen_combinations.add(pair)

            for idx, mt in enumerate(current_maxterms):
                if idx not in used_indices:
                    all_prime.add(tuple(mt.values))

            if not new_maxterms:
                for mt in current_maxterms:
                    all_prime.add(tuple(mt.values))
                break

            history.append(f"\nЭтап склеивания {stage}:")
            for mt in new_maxterms:
                history.append(f"  {mt.to_string()} ({mt.to_pattern()})")
            current_maxterms = new_maxterms
            stage += 1

        # Восстанавливаем Maxterm
        prime_maxterms = []
        for values_tuple in all_prime:
            maxterm = Maxterm(self.variables, list(values_tuple), [])
            maxterms_covered = []
            for mi in false_indices:
                if self._maxterm_covers_index(maxterm, mi):
                    maxterms_covered.append(mi)
            maxterm.maxterms = set(maxterms_covered)
            prime_maxterms.append(maxterm)

        history.append("\nПроверка на лишние импликанты:")
        final_maxterms = self._find_minimal_cnf_cover(prime_maxterms, history)
        return final_maxterms, history

    def _create_maxterm(self, index: int) -> Maxterm:
        values = []
        for i in range(self.num_vars - 1, -1, -1):
            values.append(bool(index & (1 << i)))
        return Maxterm(self.variables, values, [index])

    def _can_combine_maxterms(self, mt1: Maxterm, mt2: Maxterm) -> bool:
        diff_count = 0
        for v1, v2 in zip(mt1.values, mt2.values):
            if v1 != v2:
                if v1 is not None and v2 is not None:
                    diff_count += 1
                else:
                    return False
        return diff_count == 1

    def _combine_maxterms(self, mt1: Maxterm, mt2: Maxterm) -> Maxterm:
        new_values = []
        for v1, v2 in zip(mt1.values, mt2.values):
            if v1 != v2:
                new_values.append(None)
            else:
                new_values.append(v1)
        new_maxterms = list(mt1.maxterms | mt2.maxterms)
        return Maxterm(self.variables, new_values, new_maxterms)

    def _maxterm_covers_index(self, mt: Maxterm, index: int) -> bool:
        """Проверяет, покрывает ли макстерм данный индекс."""
        idx = index
        for i in range(self.num_vars - 1, -1, -1):
            bit = bool(idx & (1 << i))
            val = mt.values[self.num_vars - 1 - i]
            if val is not None and val != bit:
                return False
        return True

    def _find_minimal_cnf_cover(self, prime_maxterms: List[Maxterm], history: List[str]) -> List[Maxterm]:
        """Находит минимальное покрытие для КНФ."""
        if not prime_maxterms:
            return []

        false_indices = self.truth_table.get_false_indices()
        essential = []
        covered_indices = set()

        for index in false_indices:
            covering = [mt for mt in prime_maxterms if index in mt.maxterms]
            if len(covering) == 1:
                ess = covering[0]
                if ess not in essential:
                    essential.append(ess)
                    history.append(f"  {ess.to_string()} - необходимая импликанта")
                    covered_indices.update(ess.maxterms)

        for mt in prime_maxterms:
            if mt not in essential:
                history.append(f"  {mt.to_string()} - лишняя импликанта")

        uncovered = [m for m in false_indices if m not in covered_indices]
        remaining = [mt for mt in prime_maxterms if mt not in essential]

        while uncovered:
            best_mt = max(remaining, key=lambda mt: len(mt.maxterms & set(uncovered)))
            essential.append(best_mt)
            covered_indices.update(best_mt.maxterms)
            uncovered = [m for m in false_indices if m not in covered_indices]
            remaining.remove(best_mt)

        return essential

    def minimize_cnf_calculated_table(self) -> Tuple[List[Maxterm], str, List[str]]:
        """Минимизация КНФ с таблицей покрытия."""
        history = []
        maxterms, calc_history = self.minimize_cnf_calculated()
        history.extend(calc_history)

        false_indices = self.truth_table.get_false_indices()
        table_lines = ["\nТаблица покрытия:"]
        header = "Импликанта | " + " ".join(f"{m:>3}" for m in false_indices)
        table_lines.append(header)
        table_lines.append("-" * len(header))

        for mt in maxterms:
            row = f"{mt.to_string():>10} |"
            for m in false_indices:
                row += "  X " if mt.covers(m) else "    "
            table_lines.append(row)

        return maxterms, "\n".join(table_lines), history
