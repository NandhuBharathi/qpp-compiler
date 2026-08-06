"""Milestone 1 Q++ to C++ source compiler."""

from dataclasses import dataclass
import re

from .errors import QppSyntaxError


MAIN_PATTERN = re.compile(
    r"^func\s+main\s*\(\s*\)\s*:\s*$"
)

PRINT_PATTERN = re.compile(
    r"^print\s*\(\s*"
    r'"((?:\\.|[^"\\])*)"'
    r"\s*\)\s*$"
)


@dataclass(frozen=True)
class TranspileResult:
    """Generated C++ source."""

    cpp_source: str


def escape_cpp_string(value: str) -> str:
    """Preserve supported Q++ string escapes for C++."""
    output: list[str] = []
    index = 0

    while index < len(value):
        char = value[index]

        if char == "\\":
            if index + 1 >= len(value):
                raise QppSyntaxError(
                    "Invalid trailing backslash in string."
                )

            escaped = value[index + 1]

            if escaped not in {'"', "\\", "n", "t", "r"}:
                raise QppSyntaxError(
                    f"Unsupported string escape: \\\\{escaped}"
                )

            output.append("\\")
            output.append(escaped)
            index += 2
            continue

        output.append(char)
        index += 1

    return "".join(output)


def transpile(source: str) -> TranspileResult:
    """Compile Milestone 1 Q++ syntax into C++ source."""
    if not source.strip():
        raise QppSyntaxError("Source code is empty.")

    source_lines = source.splitlines()
    cpp_body: list[str] = []

    inside_main = False
    main_closed = False
    found_main = False

    for line_number, raw_line in enumerate(
        source_lines,
        start=1,
    ):
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("#"):
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
            message = escape_cpp_string(
                print_match.group(1)
            )

            cpp_body.append(
                f'    std::cout << "{message}" '
                '<< std::endl;'
            )
            continue

        raise QppSyntaxError(
            f"Line {line_number}: "
            "Milestone 1 supports only print(\"...\")."
        )

    if not found_main:
        raise QppSyntaxError(
            "Program must define 'func main():'."
        )

    if inside_main:
        raise QppSyntaxError(
            "main() block is missing 'end'."
        )

    body = "\\n".join(cpp_body)

    cpp_source = (
        "#include <iostream>\\n"
        "\\n"
        "int main() {\\n"
        f"{body}\\n"
        "    return 0;\\n"
        "}\\n"
    )

    return TranspileResult(cpp_source=cpp_source)
