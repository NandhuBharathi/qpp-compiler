"""Milestone 1 Q++ to C++ source compiler."""

from dataclasses import dataclass
import re

from .errors import QppSyntaxError


MAIN_PATTERN = re.compile(
    r"^func\s+main\s*\(\s*\)\s*:\s*$"
)

PRINT_PATTERN = re.compile(
    r'^print\s*\(\s*"((?:\\.|[^"\\])*)"\s*\)\s*$'
)


@dataclass(frozen=True)
class TranspileResult:
    """Generated C++ source."""

    cpp_source: str


def validate_string(value: str) -> str:
    """Validate supported Q++ string escapes."""
    index = 0

    while index < len(value):
        if value[index] != "\\":
            index += 1
            continue

        if index + 1 >= len(value):
            raise QppSyntaxError(
                "Invalid trailing backslash in string."
            )

        escaped = value[index + 1]

        if escaped not in {'"', "\\", "n", "t", "r"}:
            raise QppSyntaxError(
                f"Unsupported string escape: \\\\{escaped}"
            )

        index += 2

    return value


def transpile(source: str) -> TranspileResult:
    """Compile Milestone 1 Q++ into valid C++ source."""
    if not source.strip():
        raise QppSyntaxError("Source code is empty.")

    cpp_body: list[str] = []

    inside_main = False
    main_closed = False
    found_main = False

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
                    "code after main() is not supported yet."
                )

            if MAIN_PATTERN.fullmatch(line):
                if found_main:
                    raise QppSyntaxError(
                        f"Line {line_number}: "
                        "main() is already defined."
                    )

                found_main = True
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
            message = validate_string(
                print_match.group(1)
            )

            cpp_body.append(
                f'    std::cout << "{message}" '
                '<< std::endl;'
            )
            continue

        raise QppSyntaxError(
            f"Line {line_number}: "
            'Milestone 1 supports only print("...").'
        )

    if not found_main:
        raise QppSyntaxError(
            "Program must define 'func main():'."
        )

    if inside_main:
        raise QppSyntaxError(
            "main() block is missing 'end'."
        )

    body = "\n".join(cpp_body)

    cpp_source = (
        "#include <iostream>\n"
        "\n"
        "int main() {\n"
        f"{body}\n"
        "    return 0;\n"
        "}\n"
    )

    return TranspileResult(
        cpp_source=cpp_source,
    )
