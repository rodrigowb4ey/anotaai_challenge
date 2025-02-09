from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def read_root() -> dict[str, str]:
    """Root endpoint for the API."""
    return {'Hello': 'World'}
