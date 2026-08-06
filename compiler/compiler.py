"""Native Q++ compilation pipeline."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

from .errors import QppError
from .transpiler import transpile


MAX_SOURCE_BYTES = 16_384
COMPILE_TIMEOUT_SECONDS = 10
RUN_TIMEOUT_SECONDS = 3
MAX_OUTPUT_CHARS = 16_384


@dataclass(frozen=True)
class CompileResult:
    """Result returned by the Q++ compiler."""

    success: bool
    output: str
    error: str
    cpp_source: str


class QppCompiler:
    """Compile Q++ source to a native executable."""

    def compile_and_run(self, source: str) -> CompileResult:
        """Compile Q++ through C++ and execute the binary."""
        if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
            return CompileResult(
                success=False,
                output="",
                error="Source exceeds the 16 KB limit.",
                cpp_source="",
            )

        try:
            transpiled = transpile(source)
        except QppError as exc:
            return CompileResult(
                success=False,
                output="",
                error=str(exc),
                cpp_source="",
            )

        with tempfile.TemporaryDirectory(
            prefix="qpp_"
        ) as temp_directory:
            temp_path = Path(temp_directory)
            cpp_path = temp_path / "main.cpp"
            binary_path = temp_path / "program"

            cpp_path.write_text(
                transpiled.cpp_source,
                encoding="utf-8",
            )

            try:
                compile_process = subprocess.run(
                    [
                        "g++",
                        "-std=c++20",
                        "-O2",
                        "-pipe",
                        str(cpp_path),
                        "-o",
                        str(binary_path),
                    ],
                    text=True,
                    capture_output=True,
                    timeout=COMPILE_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return CompileResult(
                    success=False,
                    output="",
                    error="Native compilation timed out.",
                    cpp_source=transpiled.cpp_source,
                )

            if compile_process.returncode != 0:
                return CompileResult(
                    success=False,
                    output="",
                    error=compile_process.stderr[
                        :MAX_OUTPUT_CHARS
                    ],
                    cpp_source=transpiled.cpp_source,
                )

            try:
                run_process = subprocess.run(
                    [str(binary_path)],
                    text=True,
                    capture_output=True,
                    timeout=RUN_TIMEOUT_SECONDS,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return CompileResult(
                    success=False,
                    output="",
                    error="Program execution timed out.",
                    cpp_source=transpiled.cpp_source,
                )

            if run_process.returncode != 0:
                return CompileResult(
                    success=False,
                    output=run_process.stdout[
                        :MAX_OUTPUT_CHARS
                    ],
                    error=(
                        run_process.stderr[
                            :MAX_OUTPUT_CHARS
                        ]
                        or (
                            "Program exited with code "
                            f"{run_process.returncode}."
                        )
                    ),
                    cpp_source=transpiled.cpp_source,
                )

            return CompileResult(
                success=True,
                output=run_process.stdout[
                    :MAX_OUTPUT_CHARS
                ],
                error="",
                cpp_source=transpiled.cpp_source,
            )
