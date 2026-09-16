from pydantic import BaseModel
from typing import Optional

# This tells FastAPI exactly what JSON data type to expect when someone tries to update an Opportunity
class OpportunityUpdate(BaseModel):
    status: Optional[str] = None
    amount_eur: Optional[float] = None
    stand_area_sqm: Optional[float] = None
    requested_height_m: Optional[float] = None
    client_budget_eur: Optional[float] = None
    brief_notes: Optional[str] = None

from datetime import date, datetime
from typing import List, Dict, Any
from uuid import UUID

class ActivityLogCreate(BaseModel):
    activity_type: str
    details: str
    follow_up_on: Optional[date] = None
    completion_marker: Optional[str] = None
    author: str

class ActivityLogResponse(BaseModel):
    entry_id: str
    opportunity_code: Optional[str]
    company_code: str
    activity_type: str
    occurred_at: datetime
    details: str
    follow_up_on: Optional[date]
    completion_marker: Optional[str]
    author: str

    class Config:
        from_attributes = True

class AgentRunResponse(BaseModel):
    run_id: UUID
    opportunity_code: str
    inputs: Optional[Dict[str, Any]] = None
    checker_output: Optional[Dict[str, Any]] = None
    coordinator_decision: Optional[str] = None

    class Config:
        from_attributes = True

class OpportunityResponse(BaseModel):
    opportunity_code: str
    company_code: str
    contact_code: str
    fair_edition_code: str
    status: Optional[str]
    amount_eur: Optional[float]
    stand_area_sqm: Optional[float]
    requested_height_m: Optional[float]
    client_budget_eur: Optional[float]
    expected_close_on: Optional[date]
    brief_notes: Optional[str]

    class Config:
        from_attributes = True

class CompanySearchResponse(BaseModel):
    company_code: str
    company_name: str
    province_code: Optional[str]
    region: Optional[str]
    sales_rep: Optional[str]
    opportunities: List[OpportunityResponse] = []

    class Config:
        from_attributes = True
