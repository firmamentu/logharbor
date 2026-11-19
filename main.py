from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from analyzer import analyze

app = FastAPI(title="LogHarbor", description="日志接入与分析服务")


@app.get("/api/stats")
def stats():
    return analyze("access.log")


app.mount("/static", StaticFiles(directory="static", html=True), name="static")