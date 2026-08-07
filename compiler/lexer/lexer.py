"""Q++ lexer."""

from .tokens import Token, TokenType, KEYWORDS


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    @property
    def current(self) -> str:
        if self.position >= len(self.source):
            return "\0"
        return self.source[self.position]

    def advance(self) -> str:
        char = self.current

        self.position += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def peek(self) -> str:
        index = self.position + 1

        if index >= len(self.source):
            return "\0"

        return self.source[index]

    def tokenize(self) -> list[Token]:
        tokens = []

        while self.current != "\0":

            if self.current in " \t\r":
                self.advance()
                continue

            if self.current == "\n":
                tokens.append(
                    Token(
                        TokenType.NEWLINE,
                        "\n",
                        self.line,
                        self.column,
                    )
                )
                self.advance()
                continue

            if self.current.isalpha() or self.current == "_":
                tokens.append(self.identifier())
                continue

            if self.current.isdigit():
                tokens.append(self.number())
                continue

            if self.current == '"':
                tokens.append(self.string())
                continue

            token = self.operator()

            if token:
                tokens.append(token)
                continue

            raise SyntaxError(
                f"Unexpected character '{self.current}' "
                f"at {self.line}:{self.column}"
            )

        tokens.append(
            Token(
                TokenType.EOF,
                "",
                self.line,
                self.column,
            )
        )

        return tokens

    def identifier(self) -> Token:
        line = self.line
        column = self.column

        value = []

        while (
            self.current.isalnum()
            or self.current == "_"
        ):
            value.append(self.advance())

        text = "".join(value)

        return Token(
            KEYWORDS.get(
                text,
                TokenType.IDENTIFIER,
            ),
            text,
            line,
            column,
        )

    def number(self) -> Token:
        line = self.line
        column = self.column

        value = []
        is_float = False

        while (
            self.current.isdigit()
            or self.current == "."
        ):
            if self.current == ".":
                if is_float:
                    break
                is_float = True

            value.append(self.advance())

        text = "".join(value)

        return Token(
            TokenType.FLOAT
            if is_float
            else TokenType.INTEGER,
            text,
            line,
            column,
        )

    def string(self) -> Token:
        line = self.line
        column = self.column

        self.advance()

        value = []

        while (
            self.current != '"'
            and self.current != "\0"
        ):
            value.append(self.advance())

        if self.current != '"':
            raise SyntaxError(
                "Unterminated string literal"
            )

        self.advance()

        return Token(
            TokenType.STRING,
            "".join(value),
            line,
            column,
        )

    def operator(self):
        line = self.line
        column = self.column

        operators = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            ":": TokenType.COLON,
            "=": TokenType.ASSIGN,
            "<": TokenType.LT,
            ">": TokenType.GT,
        }

        two_char = self.current + self.peek()

        special = {
            "==": TokenType.EQ,
            "!=": TokenType.NE,
            "<=": TokenType.LE,
            ">=": TokenType.GE,
        }

        if two_char in special:
            self.advance()
            self.advance()

            return Token(
                special[two_char],
                two_char,
                line,
                column,
            )

        if self.current in operators:
            char = self.advance()

            return Token(
                operators[char],
                char,
                line,
                column,
            )

        return None
