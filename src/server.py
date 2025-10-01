from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

sys.path.append('src')

from app import RAGAssistant

app = FastAPI()

# Setup CORS (optional, for frontend JS calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates directory
templates = Jinja2Templates(directory="src/templates")

# Initialize RAG assistant once
rag_assistant = RAGAssistant()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serve the frontend HTML page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def query_rag(question: str = Form(...)):
    """
    API endpoint to query the RAG assistant.
    """
    try:
        answer = rag_assistant.invoke(question)
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.server:app", host="0.0.0.0", port=port, reload=True)
