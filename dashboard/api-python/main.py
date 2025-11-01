from fastapi import FastAPI

app = FastAPI(title="MamboLite API (Placeholder)")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

