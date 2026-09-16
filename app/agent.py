from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
import uuid

def prepare_brief(opp: models.Opportunity, fair: models.FairEdition, company: models.Company):
    """
    Role 1: Prepares the technical brief by gathering CRM data.
    This is a deterministic local stand-in for an LLM call.
    """
    brief = {
        "company_name": company.company_name,
        "opportunity_status": opp.status,
        "requested_area_sqm": opp.stand_area_sqm,
        "requested_height_m": opp.requested_height_m,
        "budget": opp.client_budget_eur,
        "notes": opp.brief_notes,
        "fair_max_area_sqm": fair.max_stand_area_sqm,
        "fair_max_height_m": fair.max_stand_height_m
    }
    
    # Simulate a generated text brief
    brief["generated_summary"] = f"Client {company.company_name} requested a {opp.stand_area_sqm} sqm stand at {fair.fair_name}."
    return brief


def check_brief(brief: dict):
    """
    Role 2: Checks the prepared brief against constraints.
    Returns a list of issues found.
    """
    issues = []
    
    req_area = brief.get("requested_area_sqm")
    max_area = brief.get("fair_max_area_sqm")
    if req_area is None:
        issues.append("Missing requested stand area.")
    elif max_area is None:
        issues.append("Fair area limit unknown — cannot validate stand area.")
    elif req_area > max_area:
        issues.append(f"Requested area ({req_area}) exceeds fair max ({max_area}).")

    req_height = brief.get("requested_height_m")
    max_height = brief.get("fair_max_height_m")
    if req_height is None:
        issues.append("Missing requested stand height.")
    elif max_height and req_height > max_height:
        issues.append(f"Requested height ({req_height}) exceeds fair max ({max_height}).")

    if not brief.get("budget"):
        issues.append("Missing client budget.")

    return {
        "status": "FAIL" if issues else "PASS",
        "issues": issues
    }


def coordinate_decision(checker_output: dict):
    """
    Coordinator: Decides whether to proceed to technical or stop for more info.
    """
    if checker_output["status"] == "FAIL":
        return "STOP - Fix issues before handoff"
    return "PROCEED - Handoff to technical team approved"


def execute_handoff(db: Session, opportunity_code: str):
    """
    Main orchestration function for the Handoff AI Assistant.
    """
    opp = db.query(models.Opportunity).filter(models.Opportunity.opportunity_code == opportunity_code).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    fair = opp.fair_edition
    company = opp.company
    
    if not fair or not company:
        raise HTTPException(status_code=400, detail="Incomplete opportunity relationships")

    # Step 1: Prepare Brief
    inputs = prepare_brief(opp, fair, company)
    
    # Step 2: Check Brief
    checker_output = check_brief(inputs)
    
    # Step 3: Coordinator Decision
    decision = coordinate_decision(checker_output)
    
    # Save the run
    run = models.AgentRun(
        run_id=uuid.uuid4(),
        opportunity_code=opportunity_code,
        inputs=inputs,
        checker_output=checker_output,
        coordinator_decision=decision
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    return run
