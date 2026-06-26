from .exceptions import InvalidPasswordError
from .models import PasswordReport


class PasswordAnalyzer:

    def analyze(self, password: str) -> PasswordReport:
        if not isinstance(password, str):
            raise InvalidPasswordError("Password must be a string.")

        raise NotImplementedError