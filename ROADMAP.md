# PassGuard Roadmap

This roadmap separates what exists today from what should be built next.

## Current State

PassGuard currently supports:

- Character analysis
- Theoretical entropy estimation
- Repeated character detection
- Repeated substring detection
- Effective entropy penalties for repeated patterns
- Entropy-based scoring
- Public `PasswordReport` model
- pytest, ruff, and mypy checks

## Near-Term Milestones

### 1. Recommendations

Add a recommendation engine that turns analysis findings into human-readable
advice.

Examples:

- Repeated characters were found.
- Repeated substrings were found.
- Effective entropy is much lower than theoretical entropy.
- Password length is too short.

This should not be a giant `if` block inside `PasswordAnalyzer`. It should be a
separate analyzer or report-building component.

### 2. Sequential Pattern Detection

Detect simple sequences such as:

```text
abc
abcd
1234
9876
```

The first implementation should handle ascending and descending ASCII letters
and digits. More advanced Unicode or keyboard-aware sequence logic can come
later.

### 3. Dictionary Detection

Detect common passwords and common words. The project already includes a data
file under `src/passguard/data/`.

The first version should focus on exact lowercase matching. Later versions can
handle case variants, embedded words, reversed words, and substitutions.

### 4. Leetspeak Normalization

Normalize common substitutions such as:

```text
@ -> a
0 -> o
1 -> l or i
3 -> e
5 -> s
$ -> s
```

This should feed dictionary detection rather than become a standalone scoring
shortcut.

### 5. Keyboard Walk Detection

Detect keyboard patterns such as:

```text
qwerty
asdf
1qaz
zaq1
```

This will likely need keyboard layout maps and path detection logic.

### 6. Crack Time Estimation

Convert effective entropy into rough online and offline crack-time estimates.

This should be clearly documented because crack time depends heavily on the
attacker model.

### 7. Policy Validation

Add optional policy checks, separate from strength analysis.

Examples:

- minimum length
- require digit
- require symbol
- disallow whitespace
- minimum score
- minimum effective entropy

Policy validation should not replace strength estimation. A password can pass a
policy and still be weak.

## Later Milestones

- Exportable JSON reports
- More nuanced scoring model
- Xato password list support
- Have I Been Pwned breach detection
- Benchmarking against zxcvbn for comparison only
- AI-generated explanations

## Development Rules

- Add one feature at a time.
- Explain the algorithm before implementing it.
- Keep analyzers small.
- Update tests with every behavior change.
- Do not hide security logic inside unexplained constants.
- Prefer boring, readable code over clever code.
