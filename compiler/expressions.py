"""Q++ expression parser."""

from dataclasses import dataclass
from enum import Enum, auto

from .errors import QppSemanticError, QppSyntaxError


class TokenKind(Enum):
    """Expression token kinds."""

    INTEGER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()

    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """Expression token."""

    kind: TokenKind
    value: str
    position: int


class Expr:
    """Base expression."""


@dataclass(frozen=True)
class IntegerExpr(Expr):
    """Integer literal."""

    value: int


@dataclass(frozen=True)
class StringExpr(Expr):
    """String literal."""

    value: str


@dataclass(frozen=True)
class BooleanExpr(Expr):
    """Boolean literal."""

    value: bool


@dataclass(frozen=True)
class VariableExpr(Expr):
    """Variable reference."""

    name: str


@dataclass(frozen=True)
class UnaryExpr(Expr):
    """Unary expression."""

    operator: str
    operand: Expr


@dataclass(frozen=True)
class BinaryExpr(Expr):
    """Binary expression."""

    left: Expr
    operator: str
    right: Expr


def tokenize(expression: str) -> list[Token]:
    """Tokenize a Q++ expression."""
    tokens = []
    index = 0

    keywords = {
        "True": TokenKind.TRUE,
        "False": TokenKind.FALSE,
        "and": TokenKind.AND,
        "or": TokenKind.OR,
        "not": TokenKind.NOT,
    }

    two_char_tokens = {
        "==": TokenKind.EQ,
        "!=": TokenKind.NE,
        "<=": TokenKind.LE,
        ">=": TokenKind.GE,
    }

    one_char_tokens = {
        "+": TokenKind.PLUS,
        "-": TokenKind.MINUS,
        "*": TokenKind.STAR,
        "/": TokenKind.SLASH,
        "%": TokenKind.PERCENT,
        "<": TokenKind.LT,
        ">": TokenKind.GT,
        "(": TokenKind.LPAREN,
        ")": TokenKind.RPAREN,
    }

    while index < len(expression):
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        two_char = expression[index:index + 2]

        if two_char in two_char_tokens:
            tokens.append(
                Token(
                    two_char_tokens[two_char],
                    two_char,
                    index,
                )
            )
            index += 2
            continue

        if char in one_char_tokens:
            tokens.append(
                Token(
                    one_char_tokens[char],
                    char,
                    index,
                )
            )
            index += 1
            continue

        if char.isdigit():
            start = index

            while (
                index < len(expression)
                and expression[index].isdigit()
            ):
                index += 1

            value = expression[start:index]

            tokens.append(
                Token(
                    TokenKind.INTEGER,
                    value,
                    start,
                )
            )
            continue

        if char.isalpha() or char == "_":
            start = index

            while (
                index < len(expression)
                and (
                    expression[index].isalnum()
                    or expression[index] == "_"
                )
            ):
                index += 1

            value = expression[start:index]

            tokens.append(
                Token(
                    keywords.get(
                        value,
                        TokenKind.IDENTIFIER,
                    ),
                    value,
                    start,
                )
            )
            continue

        if char == '"':
            start = index
            index += 1
            value = []

            while index < len(expression):
                current = expression[index]

                if current == '"':
                    index += 1
                    break

                if current == "\\":
                    if index + 1 >= len(expression):
                        raise QppSyntaxError(
                            "Unterminated string escape."
                        )

                    escaped = expression[index + 1]

                    escape_map = {
                        "n": "\n",
                        "t": "\t",
                        "r": "\r",
                        '"': '"',
                        "\\": "\\",
                    }

                    if escaped not in escape_map:
                        raise QppSyntaxError(
                            f"Unsupported escape '\\{escaped}'."
                        )

                    value.append(escape_map[escaped])
                    index += 2
                    continue

                value.append(current)
                index += 1
            else:
                raise QppSyntaxError(
                    f"Unterminated string at {start}."
                )

            tokens.append(
                Token(
                    TokenKind.STRING,
                    "".join(value),
                    start,
                )
            )
            continue

        raise QppSyntaxError(
            f"Unexpected character '{char}' at {index}."
        )

    tokens.append(
        Token(
            TokenKind.EOF,
            "",
            len(expression),
        )
    )

    return tokens


class ExpressionParser:
    """Q++ expression parser."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        """Return current token."""
        return self.tokens[self.index]

    def advance(self) -> Token:
        """Consume current token."""
        token = self.current

        if token.kind is not TokenKind.EOF:
            self.index += 1

        return token

    def parse(self) -> Expr:
        """Parse complete expression."""
        expression = self.parse_or()

        if self.current.kind is not TokenKind.EOF:
            raise QppSyntaxError(
                f"Unexpected token '{self.current.value}'."
            )

        return expression

    def parse_or(self) -> Expr:
        """Parse OR."""
        left = self.parse_and()

        while self.current.kind is TokenKind.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryExpr(left, "or", right)

        return left

    def parse_and(self) -> Expr:
        """Parse AND."""
        left = self.parse_not()

        while self.current.kind is TokenKind.AND:
            self.advance()
            right = self.parse_not()
            left = BinaryExpr(left, "and", right)

        return left

    def parse_not(self) -> Expr:
        """Parse NOT."""
        if self.current.kind is TokenKind.NOT:
            self.advance()
            return UnaryExpr(
                "not",
                self.parse_not(),
            )

        return self.parse_comparison()

    def parse_comparison(self) -> Expr:
        """Parse comparison."""
        left = self.parse_additive()

        kinds = {
            TokenKind.EQ,
            TokenKind.NE,
            TokenKind.LT,
            TokenKind.LE,
            TokenKind.GT,
            TokenKind.GE,
        }

        if self.current.kind in kinds:
            operator = self.advance().value
            right = self.parse_additive()

            return BinaryExpr(
                left,
                operator,
                right,
            )

        return left

    def parse_additive(self) -> Expr:
        """Parse + and -."""
        left = self.parse_multiplicative()

        while self.current.kind in {
            TokenKind.PLUS,
            TokenKind.MINUS,
        }:
            operator = self.advance().value
            right = self.parse_multiplicative()

            left = BinaryExpr(
                left,
                operator,
                right,
            )

        return left

    def parse_multiplicative(self) -> Expr:
        """Parse *, / and %."""
        left = self.parse_unary()

        while self.current.kind in {
            TokenKind.STAR,
            TokenKind.SLASH,
            TokenKind.PERCENT,
        }:
            operator = self.advance().value
            right = self.parse_unary()

            left = BinaryExpr(
                left,
                operator,
                right,
            )

        return left

    def parse_unary(self) -> Expr:
        """Parse numeric unary operators."""
        if self.current.kind in {
            TokenKind.PLUS,
            TokenKind.MINUS,
        }:
            operator = self.advance().value

            return UnaryExpr(
                operator,
                self.parse_unary(),
            )

        return self.parse_primary()

    def parse_primary(self) -> Expr:
        """Parse primary expressions."""
        token = self.current

        if token.kind is TokenKind.TRUE:
            self.advance()
            return BooleanExpr(True)

        if token.kind is TokenKind.FALSE:
            self.advance()
            return BooleanExpr(False)

        if token.kind is TokenKind.INTEGER:
            self.advance()
            return IntegerExpr(int(token.value))

        if token.kind is TokenKind.STRING:
            self.advance()
            return StringExpr(token.value)

        if token.kind is TokenKind.IDENTIFIER:
            self.advance()
            return VariableExpr(token.value)

        if token.kind is TokenKind.LPAREN:
            self.advance()
            expression = self.parse_or()

            if self.current.kind is not TokenKind.RPAREN:
                raise QppSyntaxError("Expected ')'.")

            self.advance()
            return expression

        raise QppSyntaxError("Expected expression.")


def parse_expression(source: str) -> Expr:
    """Parse Q++ expression source."""
    if not source.strip():
        raise QppSyntaxError("Expected expression.")

    return ExpressionParser(tokenize(source)).parse()


def infer_type(
    expression: Expr,
    symbols: dict[str, str],
) -> str:
    """Infer expression type."""
    if isinstance(expression, BooleanExpr):
        return "bool"

    if isinstance(expression, IntegerExpr):
        return "int"

    if isinstance(expression, StringExpr):
        return "str"

    if isinstance(expression, VariableExpr):
        if expression.name not in symbols:
            raise QppSemanticError(
                f"Unknown variable '{expression.name}'."
            )

        return symbols[expression.name]

    if isinstance(expression, UnaryExpr):
        operand_type = infer_type(
            expression.operand,
            symbols,
        )

        if expression.operator == "not":
            if operand_type != "bool":
                raise QppSemanticError(
                    "'not' requires bool."
                )

            return "bool"

        if operand_type != "int":
            raise QppSemanticError(
                f"Unary '{expression.operator}' requires int."
            )

        return "int"

    if isinstance(expression, BinaryExpr):
        left = infer_type(expression.left, symbols)
        right = infer_type(expression.right, symbols)

        if expression.operator in {"and", "or"}:
            if left != "bool" or right != "bool":
                raise QppSemanticError(
                    f"'{expression.operator}' requires bool."
                )

            return "bool"

        if expression.operator in {
            "==",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
        }:
            if left != right:
                raise QppSemanticError(
                    "Comparison requires matching types."
                )

            return "bool"

        if expression.operator == "+":
            if left == right == "int":
                return "int"

            if left == right == "str":
                return "str"

            raise QppSemanticError(
                "'+' requires two ints or two strings."
            )

        if expression.operator in {
            "-",
            "*",
            "/",
            "%",
        }:
            if left != "int" or right != "int":
                raise QppSemanticError(
                    f"'{expression.operator}' requires int."
                )

            return "int"

    raise QppSemanticError(
        "Unable to infer expression type."
    )
