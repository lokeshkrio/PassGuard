# PassGuard Architecture

This document explains how PassGuard is organized and why the current design
looks the way it does.

## Goals

PassGuard is designed as a modular password analysis engine. It should be easy
to add new analyzers without turning the project into one large function.

The design goals are:

- Clear data flow
- Small analyzers
- Testable algorithms
- Typed public models
- No dependency on an external password strength estimator
- A pipeline that can grow from simple entropy to richer security analysis

## High-Level Flow

```text
Password
  |
  v
AnalysisContext
  |
  v
CharacterAnalyzer
  |
  v
EntropyAnalyzer
  |
  v
PatternAnalyzer
  |
  v
EffectiveEntropyAnalyzer
  |
  v
ScoreAnalyzer
  |
  v
PasswordReport
```

The central idea is that each analyzer receives the same `AnalysisContext`.
Analyzers do not return separate values. Instead, each analyzer updates the
part of the context it owns.

## AnalysisContext

`AnalysisContext` is the shared state object for one password analysis run.

It currently stores:

- `password`: the original password string
- `characters`: result from character analysis
- `entropy`: theoretical and effective entropy
- `score`: numeric score and strength label
- `patterns`: detected pattern findings
- `pattern_penalty_bits`: entropy reduction caused by patterns

The context also exposes guard methods such as `require_entropy()` and
`require_score()`. These make pipeline ordering failures explicit. For example,
`ScoreAnalyzer` cannot run before entropy exists.

## Analyzer Pipeline

`PasswordAnalyzer` is the orchestrator. It owns the pipeline order:

1. `CharacterAnalyzer`
2. `EntropyAnalyzer`
3. `PatternAnalyzer` (includes Sequence & Keyboard Walk detection)
4. `LeetspeakNormalizer` & `DictionaryAnalyzer`
5. `EffectiveEntropyAnalyzer`
6. `ScoreAnalyzer`
7. `CrackTimeAnalyzer`
8. `RecommendationEngine`

This order matters because later analyzers depend on earlier analysis.

Character analysis must run before entropy because entropy needs the detected
character pools.

Pattern analysis must run before effective entropy because effective entropy
needs pattern findings.

Scoring must run after effective entropy because the score is based on adjusted
entropy, not theoretical entropy.

## Character Analysis

`CharacterAnalyzer` counts the character classes present in the password:

- lowercase
- uppercase
- digits
- symbols
- whitespace
- unicode or other non-ASCII characters

This result is stored as `CharacterAnalysis`.

## Theoretical Entropy

`EntropyAnalyzer` estimates theoretical entropy using:

```text
entropy_bits = length * log2(charset_size)
```

The character set size is inferred from the character analysis. For example:

- lowercase adds 26
- uppercase adds 26
- digits add 10
- symbols add 32
- unicode uses an estimated pool size

This is intentionally simple. It is useful as a baseline, but it overestimates
passwords with obvious structure.

## Pattern Analysis

`PatternAnalyzer` coordinates individual pattern detectors.

Currently implemented detectors:

- `RepeatedCharacterDetector`
- `RepeatedSubstringDetector`

Pattern detectors append `PatternFinding` objects to `context.patterns`.

Each finding contains:

- pattern type
- severity
- start index
- end index
- description

Indexes use Python slice semantics: `start` is inclusive and `end` is
exclusive.

## Repeated Character Detection

Repeated character detection finds runs such as:

```text
aaa
1111
$$$$$
```

Runs of length 1 or 2 are ignored for now. This avoids flagging ordinary
English words such as `book`.

Severity is currently based on run length:

- 3 repeated characters: low
- 4 repeated characters: medium
- 5 or more repeated characters: high

## Repeated Substring Detection

Repeated substring detection finds consecutive repeated multi-character units:

```text
abcabc
abcabcabc
20242024
passpass
```

The detector scans the password from left to right. At each position, it tries
candidate substring lengths of 2 or more and counts how many times the unit
repeats consecutively.

Single-character repeats are ignored by this detector because they belong to
`RepeatedCharacterDetector`.

## Effective Entropy

`EffectiveEntropyAnalyzer` reduces theoretical entropy when a known weak
pattern is detected.

For a repeated pattern, it compares:

```text
independent cost = span_length * log2(charset_size)
pattern cost     = cost of choosing the repeated unit + cost of choosing repeat count
```

The difference becomes the pattern penalty.

Then:

```text
effective_bits = theoretical_bits - pattern_penalty_bits
```

Effective entropy is capped at a minimum of zero.

## Scoring

`ScoreAnalyzer` converts effective entropy into:

- `score`: integer from 0 to 100
- `strength`: enum value from `Strength`

Current thresholds:

```text
< 20 bits   Very Weak
< 40 bits   Weak
< 60 bits   Moderate
< 80 bits   Strong
>= 80 bits  Very Strong
```

The score is currently linear, with 80 effective bits treated as 100 points.
Scores are floored instead of rounded so they do not cross a strength boundary
early.

## Public Report

The final public result is `PasswordReport`.

It contains:

- `score`
- `strength`
- `characters`
- `entropy`
- `recommendations`
- `patterns`

The report is intentionally simple. Internal analyzers can evolve without
forcing users to know about every pipeline detail.

## Extension Strategy

New analyzers should follow this pattern:

1. Add a focused model if the result needs structured data.
2. Add a small analyzer class with an `analyze(context)` method.
3. Store results in `AnalysisContext`.
4. Wire the analyzer into `PasswordAnalyzer` in the correct order.
5. Add unit tests for the analyzer.
6. Add an end-to-end test if the public report changes.

## Current Limitations

PassGuard is not yet a complete estimator.

Important missing pieces include:

- Breach lookup
- Password policy validation
- Xato password list integration out of the box (though it can be injected via provider)

These should be added incrementally, with tests and documented algorithms.
