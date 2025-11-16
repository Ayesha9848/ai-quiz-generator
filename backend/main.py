from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import database, models, scraper, llm_quiz_generator
import json
import os
from dotenv import load_dotenv

load_dotenv()
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="DeepKlarity - AI Wiki Quiz Generator")

origins = [o.strip() for o in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins or ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/generate_quiz")
def generate_quiz(payload: dict, db: Session = Depends(get_db)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing url")
    try:
        scraped = scraper.scrape_wikipedia(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scrape failed: {e}")
    title = scraped.get("title", url)
    article_text = scraped.get("clean_text", "")
    sections = scraped.get("sections", [])
    quiz_data = llm_quiz_generator.generate_quiz_from_text(article_text, title, sections)
    record = models.QuizRecord(
        url=url, title=title, scraped_content=article_text,
        raw_html=scraped.get("raw_html"), full_quiz_data=json.dumps(quiz_data)
    )
    db.add(record); db.commit(); db.refresh(record)
    response = {"id": record.id, "url": record.url, "title": record.title, "date_generated": str(record.date_generated), **quiz_data}
    return response

@app.get("/history")
def history(db: Session = Depends(get_db)):
    items = db.query(models.QuizRecord).order_by(models.QuizRecord.date_generated.desc()).all()
    return [{"id": r.id, "url": r.url, "title": r.title, "date_generated": str(r.date_generated)} for r in items]

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    r = db.query(models.QuizRecord).filter(models.QuizRecord.id == quiz_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    try:
        data = json.loads(r.full_quiz_data)
    except Exception:
        data = {"error": "Failed to parse stored quiz JSON"}
    response = {"id": r.id, "url": r.url, "title": r.title, "date_generated": str(r.date_generated), **data}
    return response
