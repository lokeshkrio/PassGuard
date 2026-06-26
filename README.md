# PassGuard

PassGuard is an experimental password analysis library written in Python.

The goal is to build a modular password strength engine from first principles,
without wrapping existing estimators such as zxcvbn. The project is intended to
show the engineering and security reasoning behind each analyzer: character
classification, entropy estimation, pattern detection, effective entropy,
scoring, and eventually recommendations.

PassGuard is still early-stage. It is useful as a learning and portfolio
project, but it is not yet a complete production password policy system.

## Features

Currently implemented:

- Character analysis
- Theoretical entropy estimation
- Repeated character detection
- Repeated substring detection
- Sequential pattern detection (e.g. 12345, abcde)
- Keyboard walk detection (e.g. qwerty, asdf)
- Dictionary matching (pluggable providers for custom lists)
- Leetspeak normalization for dictionary matches
- Pattern-adjusted effective entropy
- Crack time estimation via configurable attack profiles
- Entropy-based password scoring
- Actionable recommendation engine
- Structured report models using dataclasses
- Strict type checking with mypy
- Tests with pytest

Planned:

- Password policy validation
- Exportable reports
- Breach detection through Have I Been Pwned

## Architecture

The following diagram illustrates how the `AnalysisContext` state is passed through and mutated by each analyzer in the pipeline:

```text
                  ┌─────────────────────┐
                  │    Input Password   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   AnalysisContext   │
                  └──────────┬──────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │ Character       │               │ Entropy         │
   │ Analyzer        │               │ Analyzer        │
   └────────┬────────┘               └────────┬────────┘
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
   ┌──────────────────────────────────────────────────┐
   │ Pattern Analyzer                                 │
   │  ├─ Repeated Characters  ├─ Repeated Substrings   │
   │  ├─ Keyboard Walks       ├─ Sequential Runs      │
   └────────────────────────┬─────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────┐
   │ Dictionary & Mutation Matcher                    │
   │  ├─ Leetspeak Normalization                       │
   │  └─ Pluggable Wordlist Providers                 │
   └────────────────────────┬─────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────┐
   │ Final Estimators                                 │
   │  ├─ Effective Entropy Calculation                │
   │  ├─ Scoring & Strength Tiers                     │
   │  └─ Crack Time Profiler                          │
   └────────────────────────┬─────────────────────────┘
                            │
                            ▼
   ┌──────────────────────────────────────────────────┐
   │ Recommendation Engine                            │
   └────────────────────────┬─────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │   PasswordReport    │
                  └─────────────────────┘
```

## Requirements

- Python 3.13+
- uv

Development tools are managed through `pyproject.toml`:

- pytest
- ruff
- mypy
- hatchling

## Installation

For local development:

```bash
uv sync
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Run type checking:

```bash
uv run mypy src
```

## Usage

```python
from passguard import PasswordAnalyzer

analyzer = PasswordAnalyzer()
report = analyzer.analyze("abcabcabc")

print(report.score)
print(report.strength)
print(report.entropy.theoretical_bits)
print(report.entropy.effective_bits)
```

The analyzer returns a `PasswordReport` containing:

- `score`: numeric score from 0 to 100
- `strength`: human-readable strength label (e.g., "Moderate", "Strong")
- `characters`: character composition stats (`CharacterAnalysis`)
- `entropy`: theoretical and effective entropy (`EntropyResult`)
- `patterns`: detected weakness patterns (`PatternResult`), when present
- `dictionary_matches`: detected dictionary words (`list[DictionaryMatchResult]`)
- `crack_times`: estimated time to crack per attack profile (`dict[str, float]`)
- `recommendations`: actionable list of user warnings and suggestions (`list[Recommendation]`)

### Example Output

When analyzing a password like `Password123!`, the resulting `PasswordReport` object contains structured data:

```python
report = analyzer.analyze("Password123!")

# Example output access:
print(f"Score: {report.score}/100")
print(f"Strength: {report.strength}")
print(f"Effective Entropy: {report.entropy.effective_bits} bits")
print(f"Crack Time (Offline fast hash): {report.crack_times['Offline fast hash']} seconds")
```

Will output:

```text
Score: 40/100
Strength: Moderate
Effective Entropy: 32.55 bits
Crack Time (Offline fast hash): 0.31 seconds

Patterns Detected:
- Dictionary match: 'password' (at 0-8)
- Sequential digits: '123' (at 8-11)

Recommendations:
- Avoid using common dictionary words.
- Avoid using sequences like '123'.
```

## Core Idea

Simple entropy formulas can overestimate weak passwords.

For example, `abcabcabc` is nine lowercase characters. A naive entropy formula
treats it as if all nine characters were independently selected. PassGuard
detects that the password is really a repeated substring and lowers its
effective entropy.

This separation matters:

- `theoretical_bits`: what the password would have if each character were
  independently chosen from the detected character pool
- `effective_bits`: adjusted entropy after known weak patterns are considered

## Project Structure

```text
src/passguard/
    analyzer.py              # Orchestrates the analysis pipeline
    context.py               # Shared mutable analysis context
    models.py                # Public dataclass result models
    constants.py             # Character pools and constants
    exceptions.py            # Library exceptions

    analysis/
        charset.py           # Character composition
        entropy.py           # Theoretical entropy
        effective_entropy.py # Pattern-adjusted entropy
        scoring.py           # Score and strength label
        mutations.py         # Leetspeak normalization
        recommendations.py   # Actionable feedback engine

        pattern/
            engine.py        # Pattern detector orchestration
            models.py        # Pattern result models
            repeated.py      # Repeated character and substring detection
            sequence.py      # Sequential character detection
            keyboard.py      # Spatial keyboard walk detection
        
        dictionary/
            analyzer.py      # Dictionary matching
            models.py        # Dictionary match results
            provider.py      # Pluggable wordlist providers
            
        cracktime/
            analyzer.py      # Time-to-crack estimation
            models.py        # Attack profiles
```

## Documentation

- [Detailed Manual](docs.md)
- [Architecture](ARCHITECTURE.md)
- [Roadmap](ROADMAP.md)

## Design Philosophy

PassGuard was intentionally built from first principles rather than wrapping standard estimators like `zxcvbn`. Here is why:

- **Algorithm Transparency**: Standard estimators like `zxcvbn` run as monolithic, opaque blocks. In contrast, PassGuard is structured as a pipeline of independent, trace-friendly steps where you can examine exactly how and why a specific pattern or dictionary match reduced the effective entropy.
- **Pluggable & Extensible**: Security policies differ across organizations. Instead of using hardcoded English-focused dictionaries or static cracking hardware models, PassGuard allows you to configure your own `DictionaryProvider` (corporate wordlists, user metadata, localized dictionaries) and `AttackProfile` lists directly at initialization.
- **Separation of Concerns**: State is stored in a mutable, decoupled `AnalysisContext` passed through the pipeline. This ensures each step does one thing and makes unit testing individual detectors trivially easy.

## Design Principles

- Build the algorithms directly instead of wrapping an existing estimator
- Keep analyzers small and independently testable
- Use composition over inheritance
- Store analysis state in `AnalysisContext`
- Use dataclasses for public result models
- Keep the public API simple
- Prefer clear, explainable algorithms over clever shortcuts

## License

MIT
