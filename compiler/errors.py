"""Q++ compiler errors."""


class QppError(Exception):
    """Base Q++ compiler error."""


class QppSyntaxError(QppError):
    """Invalid Q++ syntax."""


class QppSemanticError(QppError):
    """Invalid Q++ program semantics."""
