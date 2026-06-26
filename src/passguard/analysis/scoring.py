from passguard.context import AnalysisContext
from passguard.models import ScoreResult, Strength


class ScoreAnalyzer:
    """Convert effective entropy into a numeric score and strength label."""

    _FULL_SCORE_BITS = 80.0

    def analyze(self, context: AnalysisContext) -> None:
        entropy = context.require_entropy()
        effective_bits = entropy.effective_bits

        context.score = ScoreResult(
            score=self._score_for(effective_bits),
            strength=self._strength_for(effective_bits),
        )

    def _score_for(self, effective_bits: float) -> int:
        if effective_bits <= 0:
            return 0

        return min(int((effective_bits / self._FULL_SCORE_BITS) * 100), 100)

    def _strength_for(self, effective_bits: float) -> Strength:
        if effective_bits < 20:
            return Strength.VERY_WEAK

        if effective_bits < 40:
            return Strength.WEAK

        if effective_bits < 60:
            return Strength.MODERATE

        if effective_bits < 80:
            return Strength.STRONG

        return Strength.VERY_STRONG
