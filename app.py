"""Q++ Compiler HTTP API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from compiler import QppCompiler


app = FastAPI(
    title="Q++ Compiler API",
    description=(
        "Native compiler backend for the Q++ language."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

compiler = QppCompiler()


class CompileRequest(BaseModel):
    """Q++ compilation request."""

    source: str = Field(
        min_length=1,
        max_length=16_384,
    )


class CompileResponse(BaseModel):
    """Q++ compilation response."""

    success: bool
    output: str
    error: str
    cpp_source: str


@app.get("/")
def root() -> dict[str, str]:
    """Return compiler service information."""
    return {
        "language": "Q++",
        "extension": ".qpp",
        "version": "0.1.0",
        "milestone": "1",
        "status": "online",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok"}


@app.post("/compile", response_model=CompileResponse)
def compile_qpp(
    request: CompileRequest,
) -> CompileResponse:
    """Compile and execute Q++ source natively."""
    result = compiler.compile_and_run(request.source)

    return CompileResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        cpp_source=result.cpp_source,
    )
