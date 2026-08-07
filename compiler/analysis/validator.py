"""Q++ semantic validator."""

from compiler.ast.nodes import (
    Assign,
    Print,
    If,
    Function,
    Return,
    Call,
    Boolean,
    Integer,
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

        if isinstance(
            statement,
            Print,
        ):
            self.validate_expression(
                statement.value
            )

            return

        if isinstance(
            statement,
            If,
        ):
            self.validate_expression(
                statement.condition
            )

            for item in statement.body:
                self.validate_statement(
                    item
                )

            for (
                elif_condition,
                elif_body,
            ) in (
                statement.elif_blocks
            ):

                self.validate_expression(
                    elif_condition
                )

                for item in elif_body:
                    self.validate_statement(
                        item
                    )

            for item in (
                statement.else_body or []
            ):
                self.validate_statement(
                    item
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


        if isinstance(
            expression,
            Boolean,
        ):
            return

        if isinstance(
            expression,
            Integer,
        ):
            return
