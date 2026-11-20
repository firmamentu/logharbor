from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles

from analyzer import analyze, parse

app = FastAPI(title="LogHarbor", description="日志接入与分析服务")


@app.get("/api/stats")
def stats():
    return analyze("access.log")


app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.post("/api/upload")
async def create_upload_file(file: UploadFile):
    contents = (await file.read()).decode("utf-8", errors="replace").splitlines()
    rows = parse(contents)
    if not rows:
        raise HTTPException(status_code=400, detail="这不是可解析的 nginx 日志")
    return {"lines": len(contents), "parsed": len(rows)}