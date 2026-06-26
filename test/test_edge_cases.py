import pytest

from passguard.analysis.cracktime.models import AttackProfile
from passguard.analysis.dictionary.provider import FileDictionaryProvider
from passguard.analysis.entropy import EntropyAnalyzer
from passguard.analysis.pattern.keyboard import KeyboardWalkDetector
from passguard.analysis.pattern.models import PatternSeverity, PatternType
from passguard.analysis.pattern.repeated import RepeatedSubstringDetector
from passguard.analyzer import PasswordAnalyzer
from passguard.context import AnalysisContext
from passguard.exceptions import InvalidPasswordError


def test_invalid_password_type() -> None:
    analyzer = PasswordAnalyzer()
    with pytest.raises(InvalidPasswordError):
        analyzer.analyze(12345)  # type: ignore


def test_context_assertions() -> None:
    context = AnalysisContext(password="pass")

    # Asserting RuntimeError is raised when accessing fields before run
    with pytest.raises(RuntimeError):
        context.require_characters()
    with pytest.raises(RuntimeError):
        context.require_entropy()
    with pytest.raises(RuntimeError):
        context.require_score()

    # Asserting ValueError is raised when EntropyAnalyzer is run before CharacterAnalyzer
    with pytest.raises(ValueError):
        EntropyAnalyzer().analyze(context)


def test_zero_speed_attack_profile() -> None:
    profile = AttackProfile("Zero Guesses Speed", 0)
    analyzer = PasswordAnalyzer(attack_profiles=[profile])
    report = analyzer.analyze("mypassword")
    assert report.crack_times["Zero Guesses Speed"] == float("inf")


def test_nonexistent_dictionary_file() -> None:
    provider = FileDictionaryProvider("nonexistent_file_path_123.txt")
    assert not provider.words()


def test_unicode_and_whitespace_coverage() -> None:
    analyzer = PasswordAnalyzer()

    # Unicode emoji and whitespaces (tabs, spaces, newlines)
    report = analyzer.analyze("🔑\t \n")
    assert report.characters.unicode == 1
    assert report.characters.whitespace == 3
    assert report.entropy.charset_size > 256


def test_keyboard_walk_chars_not_in_map() -> None:
    # Test containing characters outside standard keyboard walks/ASCII map
    context = AnalysisContext(password="αβγ🔑")
    detector = KeyboardWalkDetector()
    detector.analyze(context)
    assert not context.patterns


def test_repeated_substring_comparisons() -> None:
    # Test case to cover tie-breaking and comparison branches in RepeatedSubstringDetector
    detector = RepeatedSubstringDetector()

    # 1. candidate repeats != current repeats
    # 2. candidate span != current span
    # 3. candidate unit length vs current unit length
    context1 = AnalysisContext(
        password="abababab"
    )  # repeat unit 'ab' length 2 repeats 4 times
    detector.analyze(context1)
    assert len(context1.patterns) == 1
    assert "ab" in context1.patterns[0].description


def test_empty_password_mutations_and_recs() -> None:
    from passguard.analysis.mutations import LeetspeakNormalizer
    from passguard.analysis.recommendations import RecommendationEngine

    context = AnalysisContext(password="")
    LeetspeakNormalizer().analyze(context)
    RecommendationEngine().analyze(context)
    assert not context.normalized_passwords
    assert not context.recommendations


def test_keyboard_walk_short_and_medium() -> None:
    detector = KeyboardWalkDetector()

    # Less than min_length
    context_short = AnalysisContext(password="qw")
    detector.analyze(context_short)
    assert not context_short.patterns

    # Length == 4 (medium severity)
    context_medium = AnalysisContext(password="qwer")
    detector.analyze(context_medium)
    assert len(context_medium.patterns) == 1
    assert context_medium.patterns[0].severity.value == "Medium"


def test_dictionary_analyzer_empty_words() -> None:
    from passguard.analysis.dictionary.analyzer import DictionaryAnalyzer

    provider = FileDictionaryProvider("nonexistent_file_path_123.txt")
    analyzer = DictionaryAnalyzer(provider=provider)
    context = AnalysisContext(password="password")
    analyzer.analyze(context)
    assert not context.dictionary_matches


def test_walk_and_sequence_reduces_entropy() -> None:
    analyzer = PasswordAnalyzer()
    report = analyzer.analyze("qwerty12345")
    assert report.entropy.effective_bits < report.entropy.theoretical_bits
    assert report.patterns is not None
    assert report.patterns.penalty > 0


def test_effective_entropy_edge_cases() -> None:
    from passguard.analysis.effective_entropy import EffectiveEntropyAnalyzer
    from passguard.analysis.pattern.models import (
        PatternFinding,
        PatternSeverity,
    )

    analyzer = EffectiveEntropyAnalyzer()

    # 1. Empty span in finding (start == end)
    context_empty = AnalysisContext(password="abc")
    finding_empty = PatternFinding(
        type=PatternType.REPEATED_CHARACTER,
        severity=PatternSeverity.LOW,
        start=1,
        end=1,
        description="Empty",
    )
    context_empty.patterns.append(finding_empty)
    # Mock entropy to run the analyzer
    from passguard.models import EntropyResult

    context_empty.entropy = EntropyResult(10.0, 10.0, 26)
    analyzer.analyze(context_empty)
    assert context_empty.entropy.effective_bits == 10.0

    # 2. Match fallthrough for unhandled pattern type (e.g. None)
    context_fallthrough = AnalysisContext(password="abc")
    finding_fall = PatternFinding(
        type=None,  # type: ignore
        severity=PatternSeverity.LOW,
        start=0,
        end=3,
        description="Fallthrough",
    )
    context_fallthrough.patterns.append(finding_fall)
    context_fallthrough.entropy = EntropyResult(10.0, 10.0, 26)
    analyzer.analyze(context_fallthrough)
    assert context_fallthrough.entropy.effective_bits == 10.0

    # 3. Direct call to _repeated_substring_bits with no unit
    bits = analyzer._repeated_substring_bits(span="abcdef", bits_per_character=5.0)
    assert bits == 30.0  # 6 * 5.0


def test_sequence_detector_edge_cases() -> None:
    from passguard.analysis.pattern.sequence import SequenceDetector

    detector = SequenceDetector()

    # 1. Password shorter than min_length
    context_short = AnalysisContext(password="12")
    detector.analyze(context_short)
    assert not context_short.patterns

    # 2. Sequence direction change (e.g. "abcba")
    context_direction = AnalysisContext(password="abcba")
    detector.analyze(context_direction)
    # "abc" (length 3, 0-3) and "cba" (length 3, 2-5)
    assert len(context_direction.patterns) >= 2

    # 3. Sequence of length == 4 (medium severity)
    context_medium = AnalysisContext(password="1234")
    detector.analyze(context_medium)
    assert len(context_medium.patterns) == 1
    assert context_medium.patterns[0].severity == PatternSeverity.MEDIUM


def test_repeated_substring_detector_better_match_branches() -> None:
    detector = RepeatedSubstringDetector()

    # candidate repeats == current repeats, but candidate span != current span
    cand1 = ("abc", 2, 6)  # repeats=2, span=6
    curr1 = ("ab", 2, 4)  # repeats=2, span=4
    assert detector._is_better_match(cand1, curr1) is True

    # repeats and span are equal, compare unit length
    cand2 = ("abcabc", 2, 12)  # unit len 6, repeats 2, span 12
    curr2 = ("abcdef", 2, 12)  # unit len 6, repeats 2, span 12 (same, will compare len)
    # len(candidate_unit) < len(current_unit) is False because both are 6
    assert detector._is_better_match(cand2, curr2) is False
