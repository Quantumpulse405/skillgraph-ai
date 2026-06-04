from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    resume: str
    job_description: str

class AnalyzeResponse(BaseModel):
    skills: list[str]
    missing_skills: list[str]
    readiness_score: int
    roadmap: list[str]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    return AnalyzeResponse(
        skills=["Python", "SQL"],
        missing_skills=["Docker", "AWS"],
        readiness_score=60,
        roadmap=["Learn Docker", "Learn AWS"]
    )
