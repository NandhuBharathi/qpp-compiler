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
    BinaryOp,
    If,
    While,
    Call,
    Return,
    Function,
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

        if self.current.type == TokenType.IF:
            return self.parse_if()

        if self.current.type == TokenType.WHILE:
            return self.parse_while()

        if self.current.type == TokenType.FUNC:
            return self.parse_function()

        if self.current.type == TokenType.RETURN:
            return self.parse_return()

        if (
            self.current.type == TokenType.IDENTIFIER
            and self.peek().type == TokenType.ASSIGN
        ):
            return self.parse_assignment()

        raise SyntaxError(
            f"Unexpected token "
            f"{self.current.type.name}"
        )


    def parse_if(self):

        self.match(
            TokenType.IF
        )

        condition = (
            self.parse_expression()
        )

        self.match(
            TokenType.LBRACE
        )

        body = []

        while (
            self.current.type
            != TokenType.RBRACE
        ):

            if (
                self.current.type
                == TokenType.NEWLINE
            ):
                self.advance()
                continue

            body.append(
                self.parse_statement()
            )

        self.match(
            TokenType.RBRACE
        )

        while (
            self.current.type
            == TokenType.NEWLINE
        ):
            self.advance()

        elif_blocks = []
        else_body = None

        while (
            self.current.type
            == TokenType.ELIF
        ):

            self.advance()

            elif_condition = (
                self.parse_expression()
            )

            self.match(
                TokenType.LBRACE
            )

            elif_body = []

            while (
                self.current.type
                != TokenType.RBRACE
            ):

                if (
                    self.current.type
                    == TokenType.NEWLINE
                ):
                    self.advance()
                    continue

                elif_body.append(
                    self.parse_statement()
                )

            self.match(
                TokenType.RBRACE
            )

            while (
                self.current.type
                == TokenType.NEWLINE
            ):
                self.advance()

            elif_blocks.append(
                (
                    elif_condition,
                    elif_body,
                )
            )

        while (
            self.current.type
            == TokenType.NEWLINE
        ):
            self.advance()

        if (
            self.current.type
            == TokenType.ELSE
        ):

            self.advance()

            self.match(
                TokenType.LBRACE
            )

            else_body = []

            while (
                self.current.type
                != TokenType.RBRACE
            ):

                if (
                    self.current.type
                    == TokenType.NEWLINE
                ):
                    self.advance()
                    continue

                else_body.append(
                    self.parse_statement()
                )

            self.match(
                TokenType.RBRACE
            )

        return If(
            condition=condition,
            body=body,
            elif_blocks=elif_blocks,
            else_body=else_body,
        )

    

    def parse_while(self):

        self.match(
            TokenType.WHILE
        )

        condition = (
            self.parse_expression()
        )

        self.match(
            TokenType.LBRACE
        )

        body = []

        while (
            self.current.type
            != TokenType.RBRACE
        ):

            if (
                self.current.type
                == TokenType.NEWLINE
            ):
                self.advance()
                continue

            body.append(
                self.parse_statement()
            )

        self.match(
            TokenType.RBRACE
        )

        return While(
            condition=condition,
            body=body,
        )

    def parse_assignment(self):

        name = self.match(
            TokenType.IDENTIFIER
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
            TokenType.PRINT
        )

        self.match(
            TokenType.LPAREN
        )

        while (
            self.current.type
            == TokenType.NEWLINE
        ):
            self.advance()

        value = self.parse_expression()

        while (
            self.current.type
            == TokenType.NEWLINE
        ):
            self.advance()

        self.match(
            TokenType.RPAREN
        )

        return Print(
            value=value
        )



    def parse_expression(self):
        left = self.parse_primary()

        while self.current.type in (
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.STAR,
            TokenType.SLASH,
            TokenType.EQ,
            TokenType.NE,
            TokenType.LT,
            TokenType.LE,
            TokenType.GT,
            TokenType.GE,
        ):
            operator = self.advance().value

            right = self.parse_primary()

            left = BinaryOp(
                left=left,
                operator=operator,
                right=right,
            )

        return left

    def parse_primary(self):

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

        if (
            token.type
            == TokenType.IDENTIFIER
            and self.peek().type
            == TokenType.LPAREN
        ):
            return self.parse_call()

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


    def parse_call(self):

        name = self.match(
            TokenType.IDENTIFIER
        ).value

        self.match(
            TokenType.LPAREN
        )

        arguments = []

        while (
            self.current.type
            == TokenType.NEWLINE
        ):
            self.advance()

        while (
            self.current.type
            != TokenType.RPAREN
        ):

            arguments.append(
                self.parse_expression()
            )

            while (
                self.current.type
                == TokenType.NEWLINE
            ):
                self.advance()

            if (
                self.current.type
                == TokenType.COMMA
            ):

                self.advance()

                while (
                    self.current.type
                    == TokenType.NEWLINE
                ):
                    self.advance()

            else:
                break

        self.match(
            TokenType.RPAREN
        )

        return Call(
            name=name,
            arguments=arguments,
        )


    def parse_function(self):

        self.match(
            TokenType.FUNC
        )

        name = self.match(
            TokenType.IDENTIFIER
        ).value

        self.match(
            TokenType.LPAREN
        )

        parameters = []

        while (
            self.current.type
            != TokenType.RPAREN
        ):

            parameters.append(
                self.match(
                    TokenType.IDENTIFIER
                ).value
            )

            if (
                self.current.type
                == TokenType.COMMA
            ):
                self.advance()

        self.match(
            TokenType.RPAREN
        )

        self.match(
            TokenType.LBRACE
        )

        body = []

        while (
            self.current.type
            != TokenType.RBRACE
        ):

            if (
                self.current.type
                == TokenType.NEWLINE
            ):
                self.advance()
                continue

            body.append(
                self.parse_statement()
            )

        self.match(
            TokenType.RBRACE
        )

        return Function(
            name=name,
            parameters=parameters,
            body=body,
        )


    def parse_return(self):

        self.match(
            TokenType.RETURN
        )

        return Return(
            value=self.parse_expression()
        )
