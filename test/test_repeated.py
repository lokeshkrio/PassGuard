import pytest
from passguard.analysis.pattern.models import PatternSeverity, PatternType
from passguard.analysis.pattern.repeated import RepeatedCharacterDetector
from passguard.context import AnalysisContext


@pytest.fixture
def detector():
    return RepeatedCharacterDetector()


def test_empty_password(detector):
    context = AnalysisContext(password="")
    detector.analyze(context)
    assert len(context.patterns) == 0


def test_no_repetitions(detector):
    context = AnalysisContext(password="password123")
    detector.analyze(context)
    assert len(context.patterns) == 0


def test_short_repetition_ignored(detector):
    # Length 2 should be ignored ("oo" in "book")
    context = AnalysisContext(password="book")
    detector.analyze(context)
    assert len(context.patterns) == 0


def test_low_severity_repetition(detector):
    context = AnalysisContext(password="boook")
    detector.analyze(context)
    assert len(context.patterns) == 1

    finding = context.patterns[0]
    assert finding.type == PatternType.REPEATED_CHARACTER
    assert finding.severity == PatternSeverity.LOW
    assert finding.start == 1
    assert finding.end == 4


def test_medium_severity_repetition(detector):
    context = AnalysisContext(
        password="passssssword"
    )  # 's' is repeated 6 times (High Severity)
    detector.analyze(context)
    assert len(context.patterns) == 1

    finding = context.patterns[0]
    assert finding.severity == PatternSeverity.HIGH
    assert finding.start == 2
    assert finding.end == 8


def test_multiple_repetitions(detector):
    context = AnalysisContext(password="111222")
    detector.analyze(context)
    assert len(context.patterns) == 2

    assert context.patterns[0].severity == PatternSeverity.LOW
    assert context.patterns[1].severity == PatternSeverity.LOW


def test_repetition_at_end(detector):
    context = AnalysisContext(password="test1111")
    detector.analyze(context)
    assert len(context.patterns) == 1

    finding = context.patterns[0]
    assert finding.severity == PatternSeverity.MEDIUM
    assert finding.start == 4
    assert finding.end == 8
