from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import base64

from database import get_db, init_db
from models import User, History, CodingProblem, ChallengeAttempt
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ibm_service import ibm_service
from gemini_service import gemini_service
from code_executor import code_executor

app = FastAPI(title="SDLC Assistant Platform")

# Mount static files and templates
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "frontend/static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "frontend/templates"))

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Add sample coding problems
    db = next(get_db())
    if db.query(CodingProblem).count() == 0:
        problems = [
            CodingProblem(
                title="Two Sum",
                description="Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.",
                difficulty="Easy",
                language="Python",
                test_cases=json.dumps([
                    {"input": "[2,7,11,15], 9", "output": "[0,1]"},
                    {"input": "[3,2,4], 6", "output": "[1,2]"}
                ]),
                solution="def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i"
            ),
            CodingProblem(
                title="Reverse String",
                description="Write a function that reverses a string.",
                difficulty="Easy",
                language="Python",
                test_cases=json.dumps([
                    {"input": "hello", "output": "olleh"},
                    {"input": "world", "output": "dlrow"}
                ]),
                solution="def reverse_string(s):\n    return s[::-1]"
            ),
            CodingProblem(
                title="Palindrome Number",
                description="Determine whether an integer is a palindrome.",
                difficulty="Easy",
                language="Java",
                test_cases=json.dumps([
                    {"input": "121", "output": "true"},
                    {"input": "-121", "output": "false"}
                ]),
                solution="public boolean isPalindrome(int x) { ... }"
            )
        ]
        for problem in problems:
            db.add(problem)
        db.commit()
    db.close()

# Authentication endpoints
@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# HTML page routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/sdlc-tools", response_class=HTMLResponse)
async def sdlc_tools(request: Request):
    return templates.TemplateResponse("sdlc-tools.html", {"request": request})

@app.get("/coding-challenge", response_class=HTMLResponse)
async def coding_challenge_page(request: Request):
    return templates.TemplateResponse("coding-challenge.html", {"request": request})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})

# SDLC Tool endpoints
@app.post("/api/generate-code")
async def generate_code(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    prompt = data.get("prompt")
    
    result = ibm_service.generate_code(prompt)
    
    # Save to history
    history = History(
        user_id=current_user.id,
        request_type="code_generation",
        input_text=prompt,
        output_text=result
    )
    db.add(history)
    db.commit()
    
    return {"result": result}

@app.post("/api/generate-test-cases")
async def generate_test_cases(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    code = data.get("code")
    
    result = ibm_service.generate_test_cases(code)
    
    history = History(
        user_id=current_user.id,
        request_type="test_cases",
        input_text=code,
        output_text=result
    )
    db.add(history)
    db.commit()
    
    return {"result": result}

@app.post("/api/fix-bug")
async def fix_bug(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    code = data.get("code")
    bug_description = data.get("bug_description")
    
    result = ibm_service.fix_bug(code, bug_description)
    
    history = History(
        user_id=current_user.id,
        request_type="bug_fix",
        input_text=f"Code: {code}\nBug: {bug_description}",
        output_text=result
    )
    db.add(history)
    db.commit()
    
    return {"result": result}

@app.post("/api/requirements-to-code")
async def requirements_to_code(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    requirements = data.get("requirements")
    
    result = ibm_service.requirements_to_code(requirements)
    
    history = History(
        user_id=current_user.id,
        request_type="requirements_to_code",
        input_text=requirements,
        output_text=json.dumps(result)
    )
    db.add(history)
    db.commit()
    
    return result

@app.post("/api/generate-uml")
async def generate_uml(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    data = await request.json()
    requirements = data.get("requirements")
    
    uml_code = ibm_service.generate_uml(requirements)
    
    return {"uml_code": uml_code}

# Voice assistant endpoint
@app.post("/api/voice-assistant")
async def voice_assistant(request: Request):
    data = await request.json()
    text = data.get("text")
    
    response = gemini_service.get_voice_response(text)
    
    return {"response": response}

# Coding challenge endpoints
@app.get("/api/problems")
async def get_problems(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    problems = db.query(CodingProblem).all()
    return [{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "difficulty": p.difficulty,
        "language": p.language
    } for p in problems]

@app.post("/api/execute-code")
async def execute_code(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    code = data.get("code")
    language = data.get("language")
    problem_id = data.get("problem_id")
    
    # Get problem and test cases
    problem = db.query(CodingProblem).filter(CodingProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    test_cases = json.loads(problem.test_cases)
    results = []
    all_passed = True
    
    for test_case in test_cases:
        result = code_executor.execute_code(code, language, test_case.get("input", ""))
        passed = result["success"] and test_case["output"] in result["output"]
        results.append({
            "input": test_case["input"],
            "expected": test_case["output"],
            "actual": result["output"],
            "passed": passed,
            "error": result.get("error", "")
        })
        if not passed:
            all_passed = False
    
    # Save attempt
    attempt = ChallengeAttempt(
        user_id=current_user.id,
        problem_id=problem_id,
        code=code,
        language=language,
        passed=all_passed
    )
    db.add(attempt)
    db.commit()
    
    return {"results": results, "all_passed": all_passed}

@app.get("/api/user-stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempts = db.query(ChallengeAttempt).filter(
        ChallengeAttempt.user_id == current_user.id
    ).all()
    
    total_attempts = len(attempts)
    passed_attempts = len([a for a in attempts if a.passed])
    failed_attempts = total_attempts - passed_attempts
    
    # Count by difficulty
    difficulty_stats = {"Easy": 0, "Medium": 0, "Hard": 0}
    for attempt in attempts:
        if attempt.passed:
            problem = db.query(CodingProblem).filter(
                CodingProblem.id == attempt.problem_id
            ).first()
            if problem:
                difficulty_stats[problem.difficulty] += 1
    
    return {
        "total_attempts": total_attempts,
        "passed": passed_attempts,
        "failed": failed_attempts,
        "difficulty_stats": difficulty_stats
    }

@app.get("/api/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    histories = db.query(History).filter(
        History.user_id == current_user.id
    ).order_by(History.created_at.desc()).limit(50).all()
    
    return [{
        "id": h.id,
        "type": h.request_type,
        "input": h.input_text[:200] + "..." if len(h.input_text) > 200 else h.input_text,
        "created_at": h.created_at.isoformat()
    } for h in histories]

@app.get("/api/history/{history_id}")
async def get_history_detail(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(History).filter(
        History.id == history_id,
        History.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    
    return {
        "type": history.request_type,
        "input": history.input_text,
        "output": history.output_text,
        "created_at": history.created_at.isoformat()
    }

# PDF Download endpoint
@app.post("/api/download-pdf")
async def download_pdf(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    data = await request.json()
    content = data.get("content")
    title = data.get("title", "SDLC Output")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Content
    content_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=10,
        leftIndent=20,
        rightIndent=20
    )
    
    # Split content into lines and add to PDF
    for line in content.split('\n'):
        story.append(Preformatted(line, content_style))
    
    doc.build(story)
    buffer.seek(0)
    
    return JSONResponse({
        "pdf_data": base64.b64encode(buffer.getvalue()).decode(),
        "filename": f"{title.replace(' ', '_')}.pdf"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)