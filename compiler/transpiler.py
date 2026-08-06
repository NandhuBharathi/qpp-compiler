"""Q++ source-to-C++ transpiler."""

from dataclasses import dataclass
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
    "class",
    "end",
    "print",
    "return",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "and",
    "or",
    "not",
    "True",
    "False",
    "int",
    "str",
    "bool",
}


@dataclass(frozen=True)
class TranspileResult:
    """Generated native C++ source."""

    cpp_source: str


def escape_cpp_string(value: str) -> str:
    """Escape text for a C++ string literal."""
    replacements = {
        "\\": "\\\\",
        '"': '\\"',
        "\n": "\\n",
        "\t": "\\t",
        "\r": "\\r",
    }

    return "".join(
        replacements.get(character, character)
        for character in value
    )


def expression_to_cpp(expression: Expr) -> str:
    """Generate C++ for a Q++ expression."""
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

        operator = {
            "not": "!",
        }.get(
            expression.operator,
            expression.operator,
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


def cpp_type_for(qpp_type: str) -> str:
    """Map a Q++ type to its generated C++ type."""
    cpp_types = {
        "int": "long long",
        "str": "std::string",
        "bool": "bool",
    }

    try:
        return cpp_types[qpp_type]
    except KeyError as error:
        raise QppSemanticError(
            f"Unsupported Q++ type '{qpp_type}'."
        ) from error


def transpile(source: str) -> TranspileResult:
    """Transpile Q++ into a standalone C++ program."""
    if not source.strip():
        raise QppSyntaxError(
            "Source code is empty."
        )

    symbols: dict[str, str] = {}
    body: list[str] = []
    blocks: list[str] = []

    explicit_main = False
    main_closed = False
    executable_statement_found = False

    def emit(code: str) -> None:
        body.append(
            "    " * len(blocks) + code
        )

    def parse_boolean_condition(
        condition_source: str,
        line_number: int,
        statement_name: str,
    ) -> Expr:
        if not condition_source.strip():
            raise QppSyntaxError(
                f"Line {line_number}: "
                f"{statement_name} requires a condition."
            )

        condition = parse_expression(
            condition_source
        )

        if infer_type(condition, symbols) != "bool":
            raise QppSemanticError(
                f"Line {line_number}: "
                f"{statement_name} requires bool."
            )

        return condition

    for number, raw_line in enumerate(
        source.splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if MAIN_PATTERN.fullmatch(line):
            if explicit_main:
                raise QppSyntaxError(
                    f"Line {number}: main() already defined."
                )

            if executable_statement_found:
                raise QppSyntaxError(
                    f"Line {number}: func main() cannot be "
                    "declared after top-level executable code."
                )

            if blocks:
                raise QppSyntaxError(
                    f"Line {number}: func main() cannot "
                    "start inside another block."
                )

            explicit_main = True
            blocks.append("func")
            continue

        if main_closed:
            raise QppSyntaxError(
                f"Line {number}: executable code cannot "
                "appear after func main() has ended."
            )

        if line.startswith("func "):
            raise QppSyntaxError(
                f"Line {number}: user-defined functions "
                "are not implemented yet."
            )

        if line.startswith("class "):
            raise QppSyntaxError(
                f"Line {number}: classes "
                "are not implemented yet."
            )

        executable_statement_found = True

        if line.startswith("while ") and line.endswith(":"):
            condition = parse_boolean_condition(
                line[6:-1],
                number,
                "while",
            )

            emit(
                "while "
                f"({expression_to_cpp(condition)}) {{"
            )

            blocks.append("while")
            continue

        if line.startswith("if ") and line.endswith(":"):
            condition = parse_boolean_condition(
                line[3:-1],
                number,
                "if",
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

            condition = parse_boolean_condition(
                line[5:-1],
                number,
                "elif",
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

            if block in {"if", "while"}:
                emit("}")
                continue

            if block == "func":
                main_closed = True
                continue

            raise QppSyntaxError(
                f"Line {number}: invalid block end."
            )

        print_match = PRINT_PATTERN.fullmatch(line)

        if print_match:
            expression_source = (
                print_match.group(1).strip()
            )

            if not expression_source:
                raise QppSyntaxError(
                    f"Line {number}: print() "
                    "requires an expression."
                )

            expression = parse_expression(
                expression_source
            )

            infer_type(
                expression,
                symbols,
            )

            emit(
                "std::cout << "
                f"{expression_to_cpp(expression)} "
                "<< std::endl;"
            )

            continue

        assignment = ASSIGNMENT_PATTERN.fullmatch(
            line
        )

        if assignment:
            name = assignment.group(1)

            if name in RESERVED_NAMES:
                raise QppSemanticError(
                    f"Line {number}: '{name}' "
                    "is a reserved name."
                )

            expression = parse_expression(
                assignment.group(2)
            )

            value_type = infer_type(
                expression,
                symbols,
            )

            cpp_expression = expression_to_cpp(
                expression
            )

            if name not in symbols:
                symbols[name] = value_type

                emit(
                    f"{cpp_type_for(value_type)} "
                    f"{name} = {cpp_expression};"
                )
            else:
                if symbols[name] != value_type:
                    raise QppSemanticError(
                        f"Line {number}: "
                        f"type mismatch for '{name}'."
                    )

                emit(
                    f"{name} = {cpp_expression};"
                )

            continue

        raise QppSyntaxError(
            f"Line {number}: unsupported statement."
        )

    if blocks:
        raise QppSyntaxError(
            "Missing 'end'."
        )

    if not executable_statement_found:
        raise QppSyntaxError(
            "No executable Q++ statements found."
        )

    cpp_body = "\n".join(body)

    cpp_source = (
        "#include <iostream>\n"
        "#include <string>\n\n"
        "int main() {\n"
        f"{cpp_body}\n"
        "    return 0;\n"
        "}\n"
    )

    return TranspileResult(
        cpp_source=cpp_source
    )
