from __future__ import annotations

from typing import Iterable, List, Tuple

from Implicant import Implicant


def differ_by_one_bit(first: Implicant, second: Implicant) -> Tuple[bool, Implicant]:
    if first.mask != second.mask:
        return False, Implicant(0, 0)
    difference = first.value ^ second.value
    if difference != 0 and (difference & (difference - 1)) == 0:
        merged = Implicant(value=first.value & ~difference, mask=first.mask | difference)
        return True, merged
    return False, Implicant(0, 0)


def generate_sdnf(variable_count: int, minterms: Iterable[int], variable_names: List[str]) -> str:
    minterm_list = list(minterms)
    if not minterm_list:
        return "0"
    parts = [
        _format_implicant(Implicant(value=minterm, mask=0), variable_count, variable_names)
        for minterm in minterm_list
    ]
    return " | ".join(parts)


def minimize(
    variable_count: int,
    minterms: Iterable[int],
    dont_cares: Iterable[int] | None,
    variable_names: List[str],
) -> str:
    minterm_list = list(minterms)
    if not minterm_list:
        return "0"
    dont_care_list = list(dont_cares or [])
    prime_implicants = _find_prime_implicants(minterm_list, dont_care_list)
    essentials, remaining_minterms = _find_essential_primes(prime_implicants, minterm_list)
    solution = _cover_remaining(remaining_minterms, prime_implicants, essentials)
    return _format_solution(solution, variable_count, variable_names)


def _find_prime_implicants(
    minterms: List[int], dont_cares: List[int]
) -> List[Implicant]:
    current_level = _init_implicants(minterms, dont_cares)
    prime_map: dict[Implicant, bool] = {}

    while current_level:
        next_level: dict[Implicant, bool] = {}
        used_map: dict[Implicant, bool] = {}

        for left_index, left_implicant in enumerate(current_level):
            for right_index in range(left_index + 1, len(current_level)):
                right_implicant = current_level[right_index]
                can_merge, merged = differ_by_one_bit(left_implicant, right_implicant)
                if can_merge:
                    next_level[merged] = True
                    used_map[left_implicant] = True
                    used_map[right_implicant] = True

        for implicant in current_level:
            if not used_map.get(implicant, False):
                prime_map[implicant] = True

        current_level = list(next_level.keys())

    return list(prime_map.keys())


def _init_implicants(minterms: List[int], dont_cares: List[int]) -> List[Implicant]:
    implicants = [Implicant(value=minterm, mask=0) for minterm in minterms]
    implicants.extend(Implicant(value=term, mask=0) for term in dont_cares)
    return implicants


def _find_essential_primes(
    primes: List[Implicant], minterms: List[int]
) -> Tuple[List[Implicant], List[int]]:
    essentials: List[Implicant] = []
    covered_map: dict[int, bool] = {}

    for minterm in minterms:
        covering = _get_covers(primes, minterm)
        if len(covering) == 1:
            essentials = _append_unique(essentials, covering[0])

    for essential in essentials:
        for minterm in minterms:
            if essential.covers(minterm):
                covered_map[minterm] = True

    remaining = [minterm for minterm in minterms if not covered_map.get(minterm, False)]
    return essentials, remaining


def _get_covers(primes: List[Implicant], minterm: int) -> List[Implicant]:
    return [prime for prime in primes if prime.covers(minterm)]


def _append_unique(items: List[Implicant], item: Implicant) -> List[Implicant]:
    if any(existing.is_equal(item) for existing in items):
        return items
    return items + [item]


def _cover_remaining(
    remaining: List[int],
    primes: List[Implicant],
    essentials: List[Implicant],
) -> List[Implicant]:
    solution = list(essentials)
    uncovered = list(remaining)

    while uncovered:
        best_prime = _find_best_prime(primes, uncovered)
        solution.append(best_prime)
        uncovered = [minterm for minterm in uncovered if not best_prime.covers(minterm)]

    return solution


def _find_best_prime(primes: List[Implicant], uncovered: List[int]) -> Implicant:
    best_count = -1
    best_prime = primes[0]
    for prime in primes:
        covered_count = sum(1 for minterm in uncovered if prime.covers(minterm))
        if covered_count > best_count:
            best_count = covered_count
            best_prime = prime
    return best_prime


def _format_solution(
    solution: List[Implicant], variable_count: int, variable_names: List[str]
) -> str:
    parts: List[str] = []
    full_mask = (1 << variable_count) - 1
    for implicant in solution:
        if implicant.mask == full_mask:
            return "1"
        parts.append(_format_implicant(implicant, variable_count, variable_names))
    return " | ".join(parts)


def _format_implicant(
    implicant: Implicant, variable_count: int, variable_names: List[str]
) -> str:
    parts: List[str] = []
    for var_index in range(variable_count):
        bit_position = variable_count - 1 - var_index
        if ((implicant.mask >> bit_position) & 1) == 0:
            if ((implicant.value >> bit_position) & 1) == 1:
                parts.append(variable_names[var_index])
            else:
                parts.append("!" + variable_names[var_index])
    return "(" + " & ".join(parts) + ")"
