"""
BUILDER Web & Desktop GUI Server (FastAPI).
Serves business plan generator, venture dashboard, canvas visualizer, and pitch deck exporter.
"""

import os
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn

import db
import ai_engine

app = FastAPI(title="BUILDER GUI", version="1.0.0")

STATIC_DIR = Path(__file__).parent / "web"
STATIC_DIR.mkdir(exist_ok=True)

# Models
class VentureCreate(BaseModel):
    name: str
    tagline: Optional[str] = ""
    industry: str
    target_market: str
    business_model: Optional[str] = "SaaS"
    stage: Optional[str] = "Idea"
    summary: Optional[str] = ""

class GenerateRequest(BaseModel):
    venture_id: int
    module_type: str # 'canvas', 'pitch_deck', 'gtm'

# API Endpoints
@app.get("/api/ventures")
def list_ventures():
    return db.get_ventures()

@app.get("/api/ventures/{vid}")
def get_venture(vid: int):
    v = db.get_venture_by_id(vid)
    if not v:
        raise HTTPException(status_code=404, detail="Venture not found")
    return v

@app.post("/api/ventures")
def create_venture(data: VentureCreate):
    vid = db.create_venture(
        name=data.name,
        tagline=data.tagline or "",
        industry=data.industry,
        target_market=data.target_market,
        business_model=data.business_model or "SaaS",
        stage=data.stage or "Idea",
        summary=data.summary or ""
    )
    return {"success": True, "id": vid}

@app.delete("/api/ventures/{vid}")
def delete_venture(vid: int):
    success = db.delete_venture(vid)
    if not success:
        raise HTTPException(status_code=404, detail="Venture not found")
    return {"success": True}

@app.post("/api/generate")
def generate_venture_module(data: GenerateRequest):
    v = db.get_venture_by_id(data.venture_id)
    if not v:
        raise HTTPException(status_code=404, detail="Venture not found")
        
    res_text = ""
    title = ""
    
    if data.module_type == "canvas":
        title = "9-Box Business Model Canvas"
        res_text = ai_engine.generate_business_canvas(v["name"], v["industry"], v["target_market"], v["business_model"], v["summary"])
    elif data.module_type == "pitch_deck":
        title = "10-Slide Investor Pitch Deck"
        res_text = ai_engine.generate_pitch_deck(v["name"], v["industry"], v["target_market"], v["summary"])
    elif data.module_type == "gtm":
        title = "90-Day Go-To-Market Roadmap"
        res_text = ai_engine.generate_gtm_roadmap(v["name"], v["industry"], v["target_market"], v["summary"])
    else:
        raise HTTPException(status_code=400, detail="Invalid module type")
        
    db.save_venture_module(data.venture_id, data.module_type, title, {"markdown": res_text})
    return {"success": True, "title": title, "content": res_text}

@app.get("/api/config")
def get_config():
    return ai_engine.load_config()

@app.post("/api/config")
def save_config(cfg: Dict[str, Any]):
    ai_engine.save_config(cfg)
    return {"success": True}

@app.get("/healthz")
def health():
    return {"status": "healthy", "engine": "BUILDER-v1.0.0"}

# Serve Frontend
@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def launch_server(port: int = 8700, open_browser: bool = True):
    db.init_db()
    url = f"http://localhost:{port}"
    print(f"\n🚀 BUILDER GUI launched at: {url}\n")
    if open_browser:
        webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    launch_server()
