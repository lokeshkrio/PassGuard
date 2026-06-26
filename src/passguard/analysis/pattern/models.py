from dataclasses import dataclass
from enum import Enum


class PatternSeverity(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PatternType(Enum):
    REPEATED_CHARACTER = "Repeated Character"
    REPEATED_SUBSTRING = "Repeated Substring"
    SEQUENTIAL_DIGITS = "Sequential Digits"
    SEQUENTIAL_LETTERS = "Sequential Letters"
    KEYBOARD_WALK = "Keyboard Walk"


@dataclass(slots=True, frozen=True)
class PatternFinding:
    type: PatternType
    severity: PatternSeverity

    start: int
    end: int

    description: str


@dataclass(slots=True, frozen=True)
class PatternResult:
    findings: list[PatternFinding]

    penalty: float
