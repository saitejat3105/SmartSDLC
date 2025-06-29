from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from watsonx_utils import query_watsonx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# GET route to serve the input form
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# POST route to handle form submission
@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, prompt: str = Form(...)):
    result = query_watsonx(prompt)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "response": result,
        "prompt": prompt
    })
