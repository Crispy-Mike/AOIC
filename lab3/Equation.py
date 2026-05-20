from dataclasses import dataclass


@dataclass(frozen=True)
class Equation:
    name: str
    sdnf: str
    minimized: str
