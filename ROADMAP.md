# PassGuard Roadmap

This roadmap separates what exists today from what should be built next.

## Current State

PassGuard currently supports:

- Character analysis
- Theoretical entropy estimation
- Repeated character detection
- Repeated substring detection
- Sequential pattern detection (e.g. 1234, abcd)
- Keyboard walk detection (e.g. qwerty, asdf)
- Dictionary matching (with pluggable data providers)
- Leetspeak normalization (for dictionary matching)
- Crack time estimation (with Attack Profiles)
- Effective entropy penalties for repeated patterns
- Entropy-based scoring
- Actionable Recommendation Engine
- Public `PasswordReport` model
- pytest, ruff, and mypy checks

## Near-Term Milestones

### 1. Policy Validation

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
