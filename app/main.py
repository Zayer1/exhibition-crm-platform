from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, importer, schemas
from .database import engine, get_db
from .agent import execute_handoff
import uuid
from datetime import datetime, timezone


# Automatically create all the tables in PostgreSQL
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ONE time when the server starts up. 
    # It grabs the CSV and dumps it into the database.
    db = next(get_db())
    try:
        importer.load_csv_data(db)
    finally:
        db.close()
    yield

app = FastAPI(title="CRM API", lifespan=lifespan)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

os.makedirs("app/static", exist_ok=True)
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="static")

@app.get("/")
def redirect_to_ui():
    return RedirectResponse(url="/ui/index.html")


@app.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    """Fetch all opportunities from the database."""
    return db.query(models.Opportunity).all()


@app.get("/opportunities/{opportunity_code}")
def get_opportunity(opportunity_code: str, db: Session = Depends(get_db)):
    """Fetch a specific opportunity by its ID."""
    opp = db.query(models.Opportunity).filter(models.Opportunity.opportunity_code == opportunity_code).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opp


@app.put("/opportunities/{opportunity_code}")
def update_opportunity(opportunity_code: str, opp_data: schemas.OpportunityUpdate, db: Session = Depends(get_db)):
    """Update specific fields in an opportunity."""
    opp = db.query(models.Opportunity).filter(models.Opportunity.opportunity_code == opportunity_code).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # Update only the fields provided in the request
    update_data = opp_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(opp, key, value)
    
    db.commit()
    db.refresh(opp)
    return opp


# ==========================================
# SEARCH ENDPOINTS
# ==========================================

@app.get("/search", response_model=list[schemas.CompanySearchResponse])
def search_companies(query: str, db: Session = Depends(get_db)):
    """Search companies by name or code and return them with opportunities."""
    companies = db.query(models.Company).filter(
        (models.Company.company_name.ilike(f"%{query}%")) | 
        (models.Company.company_code.ilike(f"%{query}%"))
    ).all()
    return companies


# ==========================================
# ACTIVITY LOG ENDPOINTS
# ==========================================

@app.post("/opportunities/{opportunity_code}/activities", response_model=schemas.ActivityLogResponse)
def add_activity(opportunity_code: str, activity_data: schemas.ActivityLogCreate, db: Session = Depends(get_db)):
    """Record a conversation or schedule a follow-up for an opportunity."""
    opp = db.query(models.Opportunity).filter(models.Opportunity.opportunity_code == opportunity_code).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    new_activity = models.ActivityLog(
        entry_id=str(uuid.uuid4()),
        company_code=opp.company_code,
        opportunity_code=opportunity_code,
        activity_type=activity_data.activity_type,
        occurred_at=datetime.now(timezone.utc),
        details=activity_data.details,
        follow_up_on=activity_data.follow_up_on,
        completion_marker=activity_data.completion_marker,
        author=activity_data.author
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@app.get("/opportunities/{opportunity_code}/activities", response_model=list[schemas.ActivityLogResponse])
def get_activities(opportunity_code: str, db: Session = Depends(get_db)):
    """Fetch all activities for a specific opportunity."""
    return db.query(models.ActivityLog).filter(models.ActivityLog.opportunity_code == opportunity_code).all()

@app.get("/activities/followups", response_model=list[schemas.ActivityLogResponse])
def get_followups(db: Session = Depends(get_db)):
    """Fetch all activities that have a follow-up date scheduled."""
    return db.query(models.ActivityLog).filter(models.ActivityLog.follow_up_on.isnot(None)).order_by(models.ActivityLog.follow_up_on.asc()).all()


# ==========================================
# HANDOFF ASSISTANT ENDPOINT
# ==========================================

@app.post("/opportunities/{opportunity_code}/handoff", response_model=schemas.AgentRunResponse)
def trigger_handoff(opportunity_code: str, db: Session = Depends(get_db)):
    """Trigger the simulated AI Handoff Assistant."""
    run = execute_handoff(db, opportunity_code)
    return run

@app.get("/opportunities/{opportunity_code}/handoffs", response_model=list[schemas.AgentRunResponse])
def get_handoffs(opportunity_code: str, db: Session = Depends(get_db)):
    """Fetch all past agent runs for a specific opportunity."""
    return db.query(models.AgentRun).filter(models.AgentRun.opportunity_code == opportunity_code).order_by(models.AgentRun.run_id).all()
