from dataclasses import dataclass


@dataclass(frozen=True)
class Implicant:
    value: int
    mask: int

    def is_equal(self, other: "Implicant") -> bool:
        return self.value == other.value and self.mask == other.mask

    def covers(self, minterm_value: int) -> bool:
        return (minterm_value & ~self.mask) == (self.value & ~self.mask)
