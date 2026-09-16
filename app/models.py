import uuid
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, JSON, Uuid
from sqlalchemy.orm import relationship
from .database import Base

# ==========================================
# 1. COMPANY TABLE
# ==========================================
class Company(Base):
    """
    Stores the main exhibitor details. 
    Instead of repeating company info 10 times in a CSV, we store it once here.
    """
    __tablename__ = "companies"

    # The Primary Key (PK) is the unique ID for this specific row.
    company_code = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    province_code = Column(String)
    region = Column(String)
    sales_rep = Column(String)

    # Relationships: This tells SQLAlchemy that one Company can have multiple Contacts and Opportunities.
    contacts = relationship("Contact", back_populates="company")
    opportunities = relationship("Opportunity", back_populates="company")
    activities = relationship("ActivityLog", back_populates="company")

# ==========================================
# 2. CONTACT TABLE
# ==========================================
class Contact(Base):
    """
    Stores individual people who work at a company.
    """
    __tablename__ = "contacts"

    contact_code = Column(String, primary_key=True, index=True)
    
    # Foreign Key (FK): This links this Contact back to a specific Company code.
    company_code = Column(String, ForeignKey("companies.company_code"))
    
    first_name = Column(String)
    last_name = Column(String)
    role = Column(String)
    email = Column(String)
    phone = Column(String)

    # Relationship: Tells SQLAlchemy this Contact belongs to the Company above.
    company = relationship("Company", back_populates="contacts")
    opportunities = relationship("Opportunity", back_populates="contact")

# ==========================================
# 3. FAIR EDITION TABLE
# ==========================================
class FairEdition(Base):
    """
    Stores the specific events/fairs where opportunities take place.
    """
    __tablename__ = "fair_editions"

    fair_edition_code = Column(String, primary_key=True, index=True)
    fair_name = Column(String)
    starts_on = Column(Date)
    ends_on = Column(Date)
    max_stand_area_sqm = Column(Float)
    max_stand_height_m = Column(Float)

    opportunities = relationship("Opportunity", back_populates="fair_edition")

# ==========================================
# 4. OPPORTUNITY TABLE
# ==========================================
class Opportunity(Base):
    """
    The core sales record connecting a Company, a Contact, and a Fair.
    """
    __tablename__ = "opportunities"

    opportunity_code = Column(String, primary_key=True, index=True)
    
    # Three Foreign Keys linking to our other tables
    company_code = Column(String, ForeignKey("companies.company_code"))
    contact_code = Column(String, ForeignKey("contacts.contact_code"))
    fair_edition_code = Column(String, ForeignKey("fair_editions.fair_edition_code"))
    
    status = Column(String)
    amount_eur = Column(Float)
    stand_area_sqm = Column(Float)
    requested_height_m = Column(Float)
    client_budget_eur = Column(Float)
    expected_close_on = Column(Date)
    brief_notes = Column(String)

    # Relationships
    company = relationship("Company", back_populates="opportunities")
    contact = relationship("Contact", back_populates="opportunities")
    fair_edition = relationship("FairEdition", back_populates="opportunities")
    activities = relationship("ActivityLog", back_populates="opportunity")
    agent_runs = relationship("AgentRun", back_populates="opportunity")

# ==========================================
# 5. ACTIVITY LOG TABLE
# ==========================================
class ActivityLog(Base):
    """
    Stores tasks, emails, calls, and meeting notes.
    """
    __tablename__ = "activity_logs"

    entry_id = Column(String, primary_key=True, index=True)
    company_code = Column(String, ForeignKey("companies.company_code"))
    opportunity_code = Column(String, ForeignKey("opportunities.opportunity_code"), nullable=True)
    
    activity_type = Column(String) # 'email', 'call', 'task', etc.
    occurred_at = Column(DateTime(timezone=True))
    details = Column(String)
    follow_up_on = Column(Date, nullable=True)
    completion_marker = Column(String, nullable=True) # 'Y' or 'N'
    author = Column(String)

    # Relationships
    company = relationship("Company", back_populates="activities")
    opportunity = relationship("Opportunity", back_populates="activities")

# ==========================================
# 6. AGENT RUN TABLE
# ==========================================
class AgentRun(Base):
    """
    Required by prompt: Saves the inputs and outputs of the Handoff AI Assistant.
    """
    __tablename__ = "agent_runs"

    # We generate a unique UUID for every time the agent runs.
    run_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    opportunity_code = Column(String, ForeignKey("opportunities.opportunity_code"))
    
    # We store the inputs and outputs as raw JSON dictionaries.
    inputs = Column(JSON)
    checker_output = Column(JSON)
    coordinator_decision = Column(String)

    opportunity = relationship("Opportunity", back_populates="agent_runs")
