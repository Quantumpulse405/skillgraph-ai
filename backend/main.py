import os
import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import PyPDF2
from io import BytesIO

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Gemini API globally if the key is present
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class AnalyzeResponse(BaseModel):
    skills: list[str]
    missing_skills: list[str]
    readiness_score: int
    roadmap: list[str]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Ensure the API key is set before making the request
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")

    # Validate file type
    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Read the uploaded PDF file into memory
        file_content = await resume.read()
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))

        # Extract text from all pages
        resume_text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                resume_text += extracted_text + "\n"

        if not resume_text.strip():
             raise HTTPException(status_code=400, detail="Could not extract text from the provided PDF")

    except Exception as e:
         raise HTTPException(status_code=400, detail=f"Error reading PDF file: {str(e)}")

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
    {resume_text}

    Job Description:
    {job_description}
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
