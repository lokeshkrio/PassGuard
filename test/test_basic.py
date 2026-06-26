from passguard.analysis.charset import CharacterAnalyzer
from passguard.analysis.entropy import EntropyAnalyzer
from passguard.context import AnalysisContext


def test_entropy():
    context = AnalysisContext(password="Password123!")
    CharacterAnalyzer().analyze(context)
    EntropyAnalyzer().analyze(context)

    entropy = context.require_entropy()
    assert entropy.charset_size == 94
    assert entropy.theoretical_bits > 70


def test_lowercase_only():
    context = AnalysisContext(password="password")
    CharacterAnalyzer().analyze(context)
    EntropyAnalyzer().analyze(context)

    entropy = context.require_entropy()
    assert entropy.charset_size == 26


def test_empty_password():
    context = AnalysisContext(password="")
    CharacterAnalyzer().analyze(context)
    EntropyAnalyzer().analyze(context)

    entropy = context.require_entropy()
    assert entropy.theoretical_bits == 0
