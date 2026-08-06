"""Q++ Milestone 2 C++ code generation."""

import re

from .errors import QppSemanticError, QppSyntaxError
from .expressions import (
    BinaryExpr,
    BooleanExpr,
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
    if isinstance(expression, BooleanExpr):
        return "true" if expression.value else "false"

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

        operator = (
            "!"
            if expression.operator == "not"
            else expression.operator
        )

        return f"({operator}{operand})"

    if isinstance(expression, BinaryExpr):
        left = expression_to_cpp(expression.left)
        right = expression_to_cpp(expression.right)

        operator = {
            "and": "&&",
            "or": "||",
        }.get(
            expression.operator,
            expression.operator,
        )

        return f"({left} {operator} {right})"

    raise QppSemanticError(
        "Unsupported expression."
    )


def transpile(source: str):
    """Compile Q++ Milestone 3 into C++."""
    if not source.strip():
        raise QppSyntaxError("Source code is empty.")

    symbols: dict[str, str] = {}
    body: list[str] = []
    blocks: list[str] = []

    main_found = False

    def emit(code: str) -> None:
        body.append("    " * len(blocks) + code)

    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if MAIN_PATTERN.fullmatch(line):
            if main_found:
                raise QppSyntaxError("main() already defined.")

            main_found = True
            blocks.append("func")
            continue

        if not main_found:
            raise QppSyntaxError(
                f"Line {number}: expected 'func main():'."
            )

        if line.startswith("if ") and line.endswith(":"):
            condition = parse_expression(line[3:-1])
            condition_type = infer_type(condition, symbols)

            if condition_type != "bool":
                raise QppSemanticError(
                    f"Line {number}: if requires bool."
                )

            emit(
                f"if ({expression_to_cpp(condition)}) {{"
            )
            blocks.append("if")
            continue

        if line.startswith("elif ") and line.endswith(":"):
            if not blocks or blocks[-1] != "if":
                raise QppSyntaxError(
                    f"Line {number}: unexpected elif."
                )

            condition = parse_expression(line[5:-1])

            if infer_type(condition, symbols) != "bool":
                raise QppSemanticError(
                    f"Line {number}: elif requires bool."
                )

            blocks.pop()
            emit(
                "} else if "
                f"({expression_to_cpp(condition)}) {{"
            )
            blocks.append("if")
            continue

        if line == "else:":
            if not blocks or blocks[-1] != "if":
                raise QppSyntaxError(
                    f"Line {number}: unexpected else."
                )

            blocks.pop()
            emit("} else {")
            blocks.append("if")
            continue

        if line == "end":
            if not blocks:
                raise QppSyntaxError(
                    f"Line {number}: unexpected end."
                )

            block = blocks.pop()

            if block == "if":
                emit("}")

            continue

        print_match = PRINT_PATTERN.fullmatch(line)

        if print_match:
            expression = parse_expression(
                print_match.group(1).strip()
            )
            infer_type(expression, symbols)

            emit(
                "std::cout << "
                f"{expression_to_cpp(expression)} "
                "<< std::endl;"
            )
            continue

        assignment = ASSIGNMENT_PATTERN.fullmatch(line)

        if assignment:
            name = assignment.group(1)
            expression = parse_expression(
                assignment.group(2)
            )
            value_type = infer_type(expression, symbols)
            cpp = expression_to_cpp(expression)

            if name not in symbols:
                symbols[name] = value_type

                cpp_type = {
                    "int": "long long",
                    "str": "std::string",
                    "bool": "bool",
                }[value_type]

                emit(f"{cpp_type} {name} = {cpp};")
            else:
                if symbols[name] != value_type:
                    raise QppSemanticError(
                        f"Line {number}: type mismatch."
                    )

                emit(f"{name} = {cpp};")

            continue

        raise QppSyntaxError(
            f"Line {number}: unsupported statement."
        )

    if not main_found:
        raise QppSyntaxError("main() not found.")

    if blocks:
        raise QppSyntaxError("Missing 'end'.")

    cpp_body = "\n".join(body)

    cpp_source = (
        "#include <iostream>\n"
        "#include <string>\n\n"
        "int main() {\n"
        f"{cpp_body}\n"
        "    return 0;\n"
        "}\n"
    )

    class Result:
        def __init__(self, source: str):
            self.cpp_source = source

    return Result(cpp_source)
