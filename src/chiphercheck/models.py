from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CharacterAnalysis:
    length: int
    lowercase: int
    uppercase: int
    digits: int
    symbols: int
    whitespace: int
    unicode: int


@dataclass(slots=True, frozen=True)
class EntropyResult:
    bits: float
    charset_size: int


@dataclass(slots=True, frozen=True)
class Recommendation:
    severity: str
    message: str


@dataclass(slots=True, frozen=True)
class PasswordReport:
    score: int
    strength: str

    characters: CharacterAnalysis
    entropy: EntropyResult

    recommendations: list[Recommendation]
