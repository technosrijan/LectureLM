from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from notes_gen import generate_notes
from mdtopdf import markdown_to_pdf
import uvicorn
import io
import traceback # <--- Add this import

# -------------------------------
# App and Middleware
# -------------------------------

app = FastAPI(
    title="YouTube Notes Generator",
    description="API to generate study-ready Markdown notes and export them as PDF",
    version="1.0.0"
)

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Models
# -------------------------------

class GenerateNotesRequest(BaseModel):
    url: str

class GenerateNotesResponse(BaseModel):
    markdown: str

class GeneratePDFRequest(BaseModel):
    markdown: str

# -------------------------------
# Routes
# -------------------------------

# --- THIS IS THE UPDATED PART ---
# Moved the health check to the root path ("/") to satisfy Azure's health probe.
@app.get("/", tags=["Health"])
async def health_check():
    """Provides a simple health check for the Azure App Service."""
    return {"status": "ok"}
# ---------------------------------

@app.post("/generate-notes", response_model=GenerateNotesResponse, tags=["Notes"])
async def generate_notes_endpoint(req: GenerateNotesRequest):
    """
    Accepts a YouTube URL and returns Markdown notes with clickable timestamps.
    """
    try:
        md_notes = generate_notes(req.url)
        return {"markdown": md_notes}
    except Exception as e:
        # Print the simple error and the full traceback to the server logs
        print(f"An error occurred in /generate-notes: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

@app.post("/generate-pdf", tags=["Notes"])
async def generate_pdf_endpoint(req: GeneratePDFRequest):
    """
    Accepts Markdown text and returns a styled PDF file (streamed from memory).
    """
    try:
        pdf_bytes = io.BytesIO()
        markdown_to_pdf(req.markdown, pdf_bytes)  # write directly to BytesIO
        pdf_bytes.seek(0)

        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=notes.pdf"},
        )
    except Exception as e:
        # Let's add better logging here too for consistency
        print(f"An error occurred in /generate-pdf: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")

# -------------------------------
# Run the server
# -------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)