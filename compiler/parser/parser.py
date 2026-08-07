"""Q++ parser."""

from compiler.ast.nodes import (
    Print,
    Assign,
    Identifier,
    Integer,
    Float,
    String,
    Boolean,
    Program,
)

from compiler.lexer.tokens import (
    TokenType,
)


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def match(self, token_type):
        if self.current.type != token_type:
            raise SyntaxError(
                f"Expected {token_type.name}, "
                f"got {self.current.type.name}"
            )

        return self.advance()

    def parse(self):
        statements = []

        while self.current.type != TokenType.EOF:

            if self.current.type == TokenType.NEWLINE:
                self.advance()
                continue

            statements.append(
                self.parse_statement()
            )

        return Program(statements)

    def parse_statement(self):

        if self.current.type == TokenType.PRINT:
            return self.parse_print()

        if (
            self.current.type == TokenType.IDENTIFIER
            and self.peek().type == TokenType.ASSIGN
        ):
            return self.parse_assignment()

        raise SyntaxError(
            f"Unexpected token "
            f"{self.current.type.name}"
        )

    def parse_assignment(self):

        name = self.match(
            TokenType.PRINT
        ).value

        self.match(
            TokenType.ASSIGN
        )

        value = self.parse_expression()

        return Assign(
            name=name,
            value=value,
        )

    def parse_print(self):

        self.match(
            TokenType.IDENTIFIER
        )

        self.match(
            TokenType.LPAREN
        )

        value = self.parse_expression()

        self.match(
            TokenType.RPAREN
        )

        return Print(
            value=value
        )


    def parse_expression(self):

        token = self.current

        if token.type == TokenType.INTEGER:
            self.advance()
            return Integer(
                int(token.value)
            )

        if token.type == TokenType.FLOAT:
            self.advance()
            return Float(
                float(token.value)
            )

        if token.type == TokenType.STRING:
            self.advance()
            return String(
                token.value
            )

        if token.type == TokenType.TRUE:
            self.advance()
            return Boolean(True)

        if token.type == TokenType.FALSE:
            self.advance()
            return Boolean(False)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(
                token.value
            )

        raise SyntaxError(
            f"Unexpected token "
            f"{token.type.name}"
        )

    def peek(self):

        index = self.position + 1

        if index >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[index]
