"""Q++ semantic validator."""

from compiler.ast.nodes import (
    Assign,
    Identifier,
    Program,
)


class Validator:

    def __init__(self):
        self.symbols = set()

    def validate(self, program: Program):

        for statement in program.statements:
            self.validate_statement(
                statement
            )

    def validate_statement(
        self,
        statement,
    ):

        if isinstance(
            statement,
            Assign,
        ):
            self.validate_expression(
                statement.value
            )

            self.symbols.add(
                statement.name
            )

            return

    def validate_expression(
        self,
        expression,
    ):

        if isinstance(
            expression,
            Identifier,
        ):
            if (
                expression.name
                not in self.symbols
            ):
                raise NameError(
                    f"Undefined variable: "
                    f"{expression.name}"
                )
