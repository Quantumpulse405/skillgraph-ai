import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Configure the Gemini API globally if the key is present
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

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
    # Ensure the API key is set before making the request
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
    {request.resume}

    Job Description:
    {request.job_description}
    """

    try:
        # Use gemini-1.5-flash and configure response to be JSON
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)

        # Parse the JSON response safely
        result_json = json.loads(response.text)
        return AnalyzeResponse(**result_json)
    except json.JSONDecodeError:
        # Handle cases where Gemini returns invalid JSON
        raise HTTPException(status_code=500, detail="Failed to parse JSON from Gemini API")
    except Exception as e:
        # Handle any other exceptions (e.g., API errors, network issues)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
