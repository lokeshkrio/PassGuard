from passguard.analysis.pattern.models import (
    PatternFinding,
    PatternSeverity,
    PatternType,
)
from passguard.context import AnalysisContext


class RepeatedCharacterDetector:

    def analyze(self, context: AnalysisContext) -> None:
        password = context.password
        
        if not password:
            return

        current_char = password[0]
        start_index = 0
        length = 1

        for i in range(1, len(password)):
            if password[i] == current_char:
                length += 1
            else:
                self._evaluate_sequence(context, current_char, start_index, i, length)
                
                # Reset for the new character
                current_char = password[i]
                start_index = i
                length = 1

        # Evaluate the final sequence at the end of the string
        self._evaluate_sequence(
            context, current_char, start_index, len(password), length
        )

    def _evaluate_sequence(
        self,
        context: AnalysisContext,
        char: str,
        start_index: int,
        end_index: int,
        length: int,
    ) -> None:
        
        if length > 2:
            if length == 3:
                severity = PatternSeverity.LOW
            elif length == 4:
                severity = PatternSeverity.MEDIUM
            else:
                severity = PatternSeverity.HIGH

            finding = PatternFinding(
                type=PatternType.REPEATED_CHARACTER,
                severity=severity,
                start=start_index,
                end=end_index,
                description=(
                    f"Repeated character '{char}' found {length} times."
                ),
            )
            
            context.patterns.append(finding)
