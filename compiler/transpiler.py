"""Q++ Milestone 2 C++ code generation."""

import re

from .errors import QppSemanticError, QppSyntaxError
from .expressions import (
    BinaryExpr,
    Expr,
    IntegerExpr,
    StringExpr,
    UnaryExpr,
    VariableExpr,
    infer_type,
    parse_expression,
)


MAIN_PATTERN = re.compile(
    r"^func\s+main\s*\(\s*\)\s*:\s*$"
)

ASSIGNMENT_PATTERN = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$"
)

PRINT_PATTERN = re.compile(
    r"^print\s*\((.*)\)\s*$"
)

RESERVED_NAMES = {
    "func",
    "end",
    "print",
    "return",
    "if",
    "else",
    "for",
    "while",
    "int",
    "str",
}


def escape_cpp_string(value: str) -> str:
    """Escape a Q++ string for a C++ string literal."""
    replacements = {
        "\\": "\\\\",
        '"': '\\"',
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
    }

    return "".join(
        replacements.get(char, char)
        for char in value
    )


def expression_to_cpp(expression: Expr) -> str:
    """Generate C++ for an expression."""
    if isinstance(expression, IntegerExpr):
        return str(expression.value)

    if isinstance(expression, StringExpr):
        return (
            '"'
            + escape_cpp_string(expression.value)
            + '"'
        )

    if isinstance(expression, VariableExpr):
        return expression.name

    if isinstance(expression, UnaryExpr):
        operand = expression_to_cpp(
            expression.operand
        )
        return f"({expression.operator}{operand})"

    if isinstance(expression, BinaryExpr):
        left = expression_to_cpp(expression.left)
        right = expression_to_cpp(expression.right)

        return (
            f"({left} {expression.operator} {right})"
        )

    raise QppSemanticError(
        "Unsupported expression."
    )


def transpile(source: str):
    """Compile Q++ Milestone 2 into C++."""
    if not source.strip():
        raise QppSyntaxError("Source code is empty.")

    symbols: dict[str, str] = {}
    body: list[str] = []

    inside_main = False
    main_found = False
    main_closed = False

    for line_number, raw_line in enumerate(
        source.splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if not inside_main:
            if main_closed:
                raise QppSyntaxError(
                    f"Line {line_number}: "
                    "code after main() is not supported."
                )

            if MAIN_PATTERN.fullmatch(line):
                if main_found:
                    raise QppSyntaxError(
                        "main() is already defined."
                    )

                main_found = True
                inside_main = True
                continue

            raise QppSyntaxError(
                f"Line {line_number}: "
                "expected 'func main():'."
            )

        if line == "end":
            inside_main = False
            main_closed = True
            continue

        print_match = PRINT_PATTERN.fullmatch(line)

        if print_match:
            expression_source = (
                print_match.group(1).strip()
            )

            expression = parse_expression(
                expression_source
            )

            infer_type(expression, symbols)

            body.append(
                "    std::cout << "
                f"{expression_to_cpp(expression)} "
                "<< std::endl;"
            )
            continue

        assignment = ASSIGNMENT_PATTERN.fullmatch(
            line
        )

        if assignment:
            variable_name = assignment.group(1)
            expression_source = assignment.group(2)

            if variable_name in RESERVED_NAMES:
                raise QppSemanticError(
                    f"Line {line_number}: "
                    f"'{variable_name}' is reserved."
                )

            expression = parse_expression(
                expression_source
            )

            expression_type = infer_type(
                expression,
                symbols,
            )

            cpp_expression = expression_to_cpp(
                expression
            )

            if variable_name not in symbols:
                symbols[variable_name] = expression_type

                cpp_type = {
                    "int": "long long",
                    "str": "std::string",
                }[expression_type]

                body.append(
                    f"    {cpp_type} "
                    f"{variable_name} = "
                    f"{cpp_expression};"
                )
                continue

            current_type = symbols[variable_name]

            if current_type != expression_type:
                raise QppSemanticError(
                    f"Line {line_number}: "
                    f"cannot assign {expression_type} "
                    f"to '{variable_name}' "
                    f"of type {current_type}."
                )

            body.append(
                f"    {variable_name} = "
                f"{cpp_expression};"
            )
            continue

        raise QppSyntaxError(
            f"Line {line_number}: "
            f"unsupported statement '{line}'."
        )

    if not main_found:
        raise QppSyntaxError(
            "Program must define 'func main():'."
        )

    if inside_main:
        raise QppSyntaxError(
            "main() block is missing 'end'."
        )

    cpp_body = "\n".join(body)

    cpp_source = (
        "#include <iostream>\n"
        "#include <string>\n"
        "\n"
        "int main() {\n"
        f"{cpp_body}\n"
        "    return 0;\n"
        "}\n"
    )

    class Result:
        def __init__(self, cpp_source: str) -> None:
            self.cpp_source = cpp_source

    return Result(cpp_source)
