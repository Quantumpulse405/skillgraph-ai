import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description_text: str

class AnalyzeResponse(BaseModel):
    skills: list[str]
    missing_skills: list[str]
    readiness_score: int
    roadmap: list[str]

api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")

    prompt = f"""
    Analyze the following resume against the job description.
    Provide the response as a valid JSON object matching this schema EXACTLY:
    {{
        "skills": ["skill1", "skill2"],
        "missing_skills": ["missing1", "missing2"],
        "readiness_score": 85,
        "roadmap": ["step1", "step2"]
    }}

    Resume:
    {request.resume_text}

    Job Description:
    {request.job_description_text}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)

        result_json = json.loads(response.text)
        return AnalyzeResponse(**result_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse JSON from Gemini API")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
