import pytest
from passguard.analyzer import PasswordAnalyzer
from passguard.context import AnalysisContext
from passguard.exceptions import InvalidPasswordError
from passguard.analysis.entropy import EntropyAnalyzer
from passguard.analysis.cracktime.models import AttackProfile
from passguard.analysis.dictionary.provider import FileDictionaryProvider
from passguard.analysis.pattern.keyboard import KeyboardWalkDetector
from passguard.analysis.pattern.repeated import RepeatedSubstringDetector


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
