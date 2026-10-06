from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analytics import forecast

app = FastAPI(title="InsightHub Analytics")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Point(BaseModel):
    period: str   # "YYYY-MM"
    value: float


class ForecastRequest(BaseModel):
    series: List[Point]
    periods: int = 6


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/forecast")
def run_forecast(req: ForecastRequest):
    try:
        return forecast([p.model_dump() for p in req.series], max(1, min(req.periods, 24)))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
