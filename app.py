from fastapi import FastAPI

app = FastAPI(
    title="Q++ Compiler API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "language": "Q++",
        "extension": ".qpp",
        "version": "0.1.0",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
