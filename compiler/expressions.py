"""Q++ expression tokenizer, parser, and type inference."""

from dataclasses import dataclass
from enum import Enum, auto

from .errors import QppSemanticError, QppSyntaxError


class TokenKind(Enum):
    """Expression token kinds."""

    INTEGER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
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
class VariableExpr(Expr):
    """Variable reference."""

    name: str


@dataclass(frozen=True)
class UnaryExpr(Expr):
    """Unary arithmetic expression."""

    operator: str
    operand: Expr


@dataclass(frozen=True)
class BinaryExpr(Expr):
    """Binary arithmetic expression."""

    left: Expr
    operator: str
    right: Expr


def tokenize(expression: str) -> list[Token]:
    """Tokenize a Q++ expression."""
    tokens: list[Token] = []
    index = 0

    while index < len(expression):
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if char.isdigit():
            start = index

            while (
                index < len(expression)
                and expression[index].isdigit()
            ):
                index += 1

            tokens.append(
                Token(
                    TokenKind.INTEGER,
                    expression[start:index],
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

            tokens.append(
                Token(
                    TokenKind.IDENTIFIER,
                    expression[start:index],
                    start,
                )
            )
            continue

        if char == '"':
            start = index
            index += 1
            value: list[str] = []

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
                            "Unsupported string escape "
                            f"'\\\\{escaped}'."
                        )

                    value.append(escape_map[escaped])
                    index += 2
                    continue

                value.append(current)
                index += 1
            else:
                raise QppSyntaxError(
                    f"Unterminated string at position {start}."
                )

            tokens.append(
                Token(
                    TokenKind.STRING,
                    "".join(value),
                    start,
                )
            )
            continue

        single_tokens = {
            "+": TokenKind.PLUS,
            "-": TokenKind.MINUS,
            "*": TokenKind.STAR,
            "/": TokenKind.SLASH,
            "%": TokenKind.PERCENT,
            "(": TokenKind.LPAREN,
            ")": TokenKind.RPAREN,
        }

        kind = single_tokens.get(char)

        if kind is not None:
            tokens.append(
                Token(kind, char, index)
            )
            index += 1
            continue

        raise QppSyntaxError(
            f"Unexpected character '{char}' "
            f"at position {index}."
        )

    tokens.append(
        Token(TokenKind.EOF, "", len(expression))
    )

    return tokens


class ExpressionParser:
    """Parse Q++ expressions with operator precedence."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        """Return the current token."""
        return self.tokens[self.index]

    def advance(self) -> Token:
        """Consume and return the current token."""
        token = self.current

        if token.kind is not TokenKind.EOF:
            self.index += 1

        return token

    def parse(self) -> Expr:
        """Parse a complete expression."""
        expression = self.parse_additive()

        if self.current.kind is not TokenKind.EOF:
            raise QppSyntaxError(
                "Unexpected token "
                f"'{self.current.value}'."
            )

        return expression

    def parse_additive(self) -> Expr:
        """Parse addition and subtraction."""
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
        """Parse multiplication, division, and modulo."""
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
        """Parse unary plus and minus."""
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
        """Parse literals, variables, and parentheses."""
        token = self.current

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
            expression = self.parse_additive()

            if self.current.kind is not TokenKind.RPAREN:
                raise QppSyntaxError(
                    "Expected ')'."
                )

            self.advance()
            return expression

        raise QppSyntaxError(
            "Expected an expression."
        )


def parse_expression(source: str) -> Expr:
    """Parse Q++ expression source."""
    if not source.strip():
        raise QppSyntaxError(
            "Expected an expression."
        )

    return ExpressionParser(
        tokenize(source)
    ).parse()


def infer_type(
    expression: Expr,
    symbols: dict[str, str],
) -> str:
    """Infer and validate an expression type."""
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

        if operand_type != "int":
            raise QppSemanticError(
                f"Unary '{expression.operator}' "
                "requires int."
            )

        return "int"

    if isinstance(expression, BinaryExpr):
        left_type = infer_type(
            expression.left,
            symbols,
        )
        right_type = infer_type(
            expression.right,
            symbols,
        )

        if expression.operator == "+":
            if left_type == right_type == "int":
                return "int"

            if left_type == right_type == "str":
                return "str"

            raise QppSemanticError(
                "Operator '+' requires two ints "
                "or two strings."
            )

        if expression.operator in {
            "-",
            "*",
            "/",
            "%",
        }:
            if left_type != "int" or right_type != "int":
                raise QppSemanticError(
                    f"Operator '{expression.operator}' "
                    "requires int operands."
                )

            return "int"

    raise QppSemanticError(
        "Unable to infer expression type."
    )
