from fastapi import FastAPI, File, Response, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import shutil
import os
from extract import extract_all_data

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get('/')
def index():
    return Response(content='FastAPI for DARS Visualizer.', status_code=200)

# Define Pydantic models
class Course(BaseModel):
    course_code: str
    credits: float
    status: str
    course_name: str

class InProgressCourse(Course):
    semester: Optional[str] = None

class Credits(BaseModel):
    status: str
    earned_credits: float
    in_progress_credits: float
    needed_credits: float

class Requirement(BaseModel):
    category: str
    earned: Optional[str] = None
    needs: Optional[str] = None
    details: List[str]

class ExtractedData(BaseModel):
    student_name: Optional[str] = None
    preparation_date: Optional[str] = None
    requested_school: Optional[str] = None
    requested_major: Optional[str] = None
    gpa: str
    majors: List[str]
    certificates: List[str]
    credits: Credits
    in_progress_courses: List[InProgressCourse]
    all_courses: List[Course]
    completed_requirements: List[Requirement]
    unfulfilled_requirements: List[Requirement]

@app.post("/extract-data/", response_model=ExtractedData)
async def extract_data(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save the uploaded file temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract data from the PDF
        data = extract_all_data(temp_file_path)
        return data
    except ValueError as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)
