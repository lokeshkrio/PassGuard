import math

from passguard.analysis.pattern.models import PatternFinding, PatternType
from passguard.context import AnalysisContext
from passguard.models import EntropyResult


class EffectiveEntropyAnalyzer:
    """Apply pattern-based reductions to theoretical entropy."""

    def analyze(self, context: AnalysisContext) -> None:
        entropy = context.require_entropy()

        if entropy.charset_size == 0 or not context.patterns:
            return

        bits_per_character = math.log2(entropy.charset_size)
        penalty = 0.0

        # Sort patterns by span length descending to process larger patterns first
        sorted_patterns = sorted(
            context.patterns, key=lambda p: p.end - p.start, reverse=True
        )
        covered_indices: set[int] = set()

        for finding in sorted_patterns:
            finding_indices = set(range(finding.start, finding.end))
            # If the finding overlaps with already covered indices, skip it to avoid double-penalizing
            if finding_indices & covered_indices:
                continue

            p = self._penalty_for_finding(
                password=context.password,
                finding=finding,
                bits_per_character=bits_per_character,
            )
            if p > 0.0:
                penalty += p
                covered_indices.update(finding_indices)

        context.pattern_penalty_bits = round(penalty, 2)
        context.entropy = EntropyResult(
            theoretical_bits=entropy.theoretical_bits,
            effective_bits=round(max(entropy.theoretical_bits - penalty, 0.0), 2),
            charset_size=entropy.charset_size,
        )

    def _penalty_for_finding(
        self,
        password: str,
        finding: PatternFinding,
        bits_per_character: float,
    ) -> float:
        span = password[finding.start : finding.end]

        if not span:
            return 0.0

        independent_bits = len(span) * bits_per_character
        estimated_bits = independent_bits
        match finding.type:
            case PatternType.REPEATED_CHARACTER:
                estimated_bits = self._repeated_character_bits(
                    span,
                    bits_per_character,
                )
            case PatternType.REPEATED_SUBSTRING:
                estimated_bits = self._repeated_substring_bits(
                    span,
                    bits_per_character,
                )
            case PatternType.KEYBOARD_WALK:
                estimated_bits = self._keyboard_walk_bits(
                    span,
                    bits_per_character,
                )
            case PatternType.SEQUENTIAL_DIGITS | PatternType.SEQUENTIAL_LETTERS:
                estimated_bits = self._sequential_bits(
                    span,
                    bits_per_character,
                )

        return max(independent_bits - estimated_bits, 0.0)

    def _keyboard_walk_bits(
        self,
        span: str,
        bits_per_character: float,
    ) -> float:
        # Keyboard walk: 1 starting character + (~1.5 bits transition choice per step)
        return bits_per_character + (len(span) - 1) * 1.5

    def _sequential_bits(
        self,
        _span: str,
        bits_per_character: float,
    ) -> float:
        # Sequence: 1 starting character + 1 bit for direction (ascending/descending)
        return bits_per_character + 1.0

    def _repeated_character_bits(
        self,
        span: str,
        bits_per_character: float,
    ) -> float:
        return bits_per_character + math.log2(len(span))

    def _repeated_substring_bits(
        self,
        span: str,
        bits_per_character: float,
    ) -> float:
        unit = self._smallest_repeating_unit(span)

        if unit is None:
            return len(span) * bits_per_character

        repeat_count = len(span) // len(unit)
        return (len(unit) * bits_per_character) + math.log2(repeat_count)

    def _smallest_repeating_unit(self, span: str) -> str | None:
        for unit_length in range(1, (len(span) // 2) + 1):
            if len(span) % unit_length != 0:
                continue

            unit = span[:unit_length]

            if unit * (len(span) // unit_length) == span:
                return unit

        return None
