"""Q++ compilation pipeline."""

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.analysis.validator import Validator
from compiler.codegen.cpp.generator import CppGenerator


COMPILE_TIMEOUT = 10
RUN_TIMEOUT = 3


@dataclass
class CompileResult:
    success: bool
    output: str
    error: str
    cpp_source: str


class QppCompiler:

    def compile(self, source: str):

        tokens = Lexer(
            source
        ).tokenize()

        program = Parser(
            tokens
        ).parse()

        Validator().validate(
            program
        )

        cpp_source = (
            CppGenerator()
            .generate(program)
        )

        return cpp_source

    def compile_and_run(
        self,
        source: str,
    ) -> CompileResult:

        try:
            cpp_source = self.compile(
                source
            )

        except Exception as exc:
            return CompileResult(
                success=False,
                output="",
                error=str(exc),
                cpp_source="",
            )

        with tempfile.TemporaryDirectory(
            prefix="qpp_"
        ) as temp_dir:

            temp_dir = Path(
                temp_dir
            )

            cpp_file = (
                temp_dir / "main.cpp"
            )

            binary_file = (
                temp_dir / "program"
            )

            cpp_file.write_text(
                cpp_source,
                encoding="utf-8",
            )

            try:
                compile_process = (
                    subprocess.run(
                        [
                            "g++",
                            "-std=c++20",
                            str(cpp_file),
                            "-o",
                            str(binary_file),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=COMPILE_TIMEOUT,
                    )
                )

            except Exception as exc:
                return CompileResult(
                    success=False,
                    output="",
                    error=str(exc),
                    cpp_source=cpp_source,
                )

            if (
                compile_process.returncode
                != 0
            ):
                return CompileResult(
                    success=False,
                    output="",
                    error=compile_process.stderr,
                    cpp_source=cpp_source,
                )

            try:
                run_process = (
                    subprocess.run(
                        [str(binary_file)],
                        capture_output=True,
                        text=True,
                        timeout=RUN_TIMEOUT,
                    )
                )

            except Exception as exc:
                return CompileResult(
                    success=False,
                    output="",
                    error=str(exc),
                    cpp_source=cpp_source,
                )

            return CompileResult(
                success=(
                    run_process.returncode
                    == 0
                ),
                output=run_process.stdout,
                error=run_process.stderr,
                cpp_source=cpp_source,
            )
