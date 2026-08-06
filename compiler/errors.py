"""Q++ compiler errors."""


class QppError(Exception):
    """Base error raised by the Q++ compiler."""


class QppSyntaxError(QppError):
    """Raised when Q++ source contains invalid syntax."""
