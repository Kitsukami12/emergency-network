from fastapi import FastAPI

app = FastAPI(title="AI Emergency Response Network")

@app.get("/health")
def health():
    return {"status": "ok"}