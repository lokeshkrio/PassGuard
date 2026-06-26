from passguard.analysis.pattern.repeated import RepeatedCharacterDetector
from passguard.context import AnalysisContext


class PatternAnalyzer:

    def __init__(self):
        self.repeated = RepeatedCharacterDetector()

    def analyze(self, context: AnalysisContext) -> None:
        self.repeated.analyze(context)