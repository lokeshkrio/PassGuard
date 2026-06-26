import pytest

from passguard.analysis.scoring import ScoreAnalyzer
from passguard.analyzer import PasswordAnalyzer
from passguard.context import AnalysisContext
from passguard.models import EntropyResult, Strength


@pytest.fixture
def analyzer() -> ScoreAnalyzer:
    return ScoreAnalyzer()


def test_scoring_requires_entropy(analyzer: ScoreAnalyzer) -> None:
    context = AnalysisContext(password="password")

    with pytest.raises(RuntimeError, match="Entropy analysis has not been run"):
        analyzer.analyze(context)


@pytest.mark.parametrize(
    ("effective_bits", "expected_score", "expected_strength"),
    [
        (0.0, 0, Strength.VERY_WEAK),
        (19.99, 24, Strength.VERY_WEAK),
        (20.0, 25, Strength.WEAK),
        (40.0, 50, Strength.MODERATE),
        (60.0, 75, Strength.STRONG),
        (80.0, 100, Strength.VERY_STRONG),
        (120.0, 100, Strength.VERY_STRONG),
    ],
)
def test_score_and_strength_are_based_on_effective_entropy(
    analyzer: ScoreAnalyzer,
    effective_bits: float,
    expected_score: int,
    expected_strength: Strength,
) -> None:
    context = AnalysisContext(
        password="password",
        entropy=EntropyResult(
            theoretical_bits=effective_bits,
            effective_bits=effective_bits,
            charset_size=26,
        ),
    )

    analyzer.analyze(context)

    score = context.require_score()
    assert score.score == expected_score
    assert score.strength == expected_strength


def test_password_report_uses_score_analyzer() -> None:
    report = PasswordAnalyzer().analyze("abcabcabc")

    assert report.score == 19
    assert report.strength == "Very Weak"
