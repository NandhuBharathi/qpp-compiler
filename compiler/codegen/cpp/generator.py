"""Q++ C++ code generator."""

from compiler.ast.nodes import (
    Assign,
    Boolean,
    Float,
    Identifier,
    Integer,
    Program,
    Print,
    String,
    BinaryOp,
    If,
    While,
)


class CppGenerator:

    def __init__(self):
        self.lines = []
        self.variables = {}

    def generate(
        self,
        program: Program,
    ) -> str:

        self.lines = [
            "#include <iostream>",
            "#include <string>",
            "",
            "int main() {",
        ]

        for statement in program.statements:
            self.generate_statement(
                statement
            )

        self.lines.extend(
            [
                "    return 0;",
                "}",
            ]
        )

        return "\n".join(
            self.lines
        )

    def generate_statement(
        self,
        statement,
    ):

        if isinstance(
            statement,
            Assign,
        ):
            cpp_value = (
                self.generate_expression(
                    statement.value
                )
            )

            cpp_type = (
                self.infer_cpp_type(
                    statement.value
                )
            )

            if (
                statement.name
                not in self.variables
            ):
                self.variables[
                    statement.name
                ] = cpp_type

                self.lines.append(
                    f"    {cpp_type} "
                    f"{statement.name} = "
                    f"{cpp_value};"
                )
            else:
                self.lines.append(
                    f"    {statement.name} = "
                    f"{cpp_value};"
                )


        elif isinstance(
            statement,
            If,
        ):
            condition = (
                self.generate_expression(
                    statement.condition
                )
            )

            self.lines.append(
                f"    if ({condition}) {{"
            )

            for child in (
                statement.body
            ):
                self.generate_statement(
                    child
                )

            self.lines.append(
                "    }"
            )

            if (
                statement.else_body
                is not None
            ):
                self.lines.append(
                    "    else {"
                )

                for child in (
                    statement.else_body
                ):
                    self.generate_statement(
                        child
                    )

                self.lines.append(
                    "    }"
                )

        elif isinstance(
            statement,
            While,
        ):
            condition = (
                self.generate_expression(
                    statement.condition
                )
            )

            self.lines.append(
                f"    while ({condition}) {{"
            )

            for child in (
                statement.body
            ):
                self.generate_statement(
                    child
                )

            self.lines.append(
                "    }"
            )

        elif isinstance(
            statement,
            Print,
        ):
            self.lines.append(
                "    std::cout << "
                + self.generate_expression(
                    statement.value
                )
                + " << std::endl;"
            )

    def generate_expression(
        self,
        expression,
    ):

        if isinstance(
            expression,
            Integer,
        ):
            return str(
                expression.value
            )

        if isinstance(
            expression,
            Float,
        ):
            return str(
                expression.value
            )

        if isinstance(
            expression,
            String,
        ):
            return (
                '"'
                + expression.value
                + '"'
            )

        if isinstance(
            expression,
            Boolean,
        ):
            return (
                "true"
                if expression.value
                else "false"
            )

        if isinstance(
            expression,
            BinaryOp,
        ):
            return (
                "("
                + self.generate_expression(
                    expression.left
                )
                + f" {expression.operator} "
                + self.generate_expression(
                    expression.right
                )
                + ")"
            )

        if isinstance(
            expression,
            Identifier,
        ):
            return expression.name

        raise ValueError(
            "Unsupported expression"
        )

    def infer_cpp_type(
        self,
        expression,
    ):

        if isinstance(
            expression,
            Integer,
        ):
            return "long long"

        if isinstance(
            expression,
            Float,
        ):
            return "double"

        if isinstance(
            expression,
            String,
        ):
            return "std::string"

        if isinstance(
            expression,
            Boolean,
        ):
            return "bool"

        return "auto"
