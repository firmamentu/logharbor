from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from analyzer import analyze, analyze_rows, parse
from llm import explain

app = FastAPI(title="LogHarbor", description="日志接入与分析服务")


@app.get("/api/stats")
def stats():
    return analyze("access.log")


@app.post("/api/upload")
async def create_upload_file(file: UploadFile):
    contents = (await file.read()).decode("utf-8", errors="replace").splitlines()
    rows = parse(contents)
    if not rows:
        raise HTTPException(status_code=400, detail="这不是可解析的 nginx 日志")
    return analyze_rows(rows)


app.mount("/static", StaticFiles(directory="static", html=True), name="static")
