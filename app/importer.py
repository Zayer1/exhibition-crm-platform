import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from . import models

def parse_euro_float(val: str):
    """Converts European format '1.000,50' to Python float 1000.50"""
    if not val:
        return None
    clean_val = val.replace(".", "").replace(",", ".")
    try:
        return float(clean_val)
    except ValueError:
        return None

def parse_date(val: str):
    """Converts DD/MM/YYYY to a Python Date object"""
    if not val:
        return None
    try:
        return datetime.strptime(val.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None

def parse_datetime(val: str):
    """Converts DD/MM/YYYY HH:MM to a Python Datetime object"""
    if not val:
        return None
    try:
        dt = datetime.strptime(val.strip(), "%d/%m/%Y %H:%M")
        return dt.replace(tzinfo=ZoneInfo("Europe/Rome"))
    except ValueError:
        return None

def load_csv_data(db: Session):
    """Reads the 4 CSV files and populates the database safely."""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    
    # Check if we already have data in the database
    if db.query(models.Company).first() is not None:
        print("Data already exists in database. Skipping import to preserve user changes.")
        return

    print("Starting CSV Data Import...")

    seen_companies = set()
    seen_contacts = set()
    seen_fairs = set()
    seen_opps = set()
    seen_acts = set()

    # 1. Load Companies and Contacts
    cc_path = os.path.join(data_dir, "companies_and_contacts.csv")
    if os.path.exists(cc_path):
        with open(cc_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                cc = row["company_code"].strip()
                # Insert Company on first run
                if cc and cc not in seen_companies:
                    seen_companies.add(cc)
                    company = models.Company(
                        company_code=cc,
                        company_name=row["company_name"].strip(),
                        province_code=row["province_code"].strip(),
                        region=row["region"].strip(),
                        sales_rep=row["sales_rep"].strip()
                    )
                    db.add(company)

                c_code = row["contact_code"].strip()
                # Insert Contact on first run
                if c_code and c_code not in seen_contacts:
                    seen_contacts.add(c_code)
                    contact = models.Contact(
                        contact_code=c_code,
                        company_code=cc,
                        first_name=row["contact_first_name"].strip(),
                        last_name=row["contact_last_name"].strip(),
                        role=None, # Role not in CSV
                        email=row["email"].strip(),
                        phone=row["phone"].strip()
                    )
                    db.add(contact)
        db.commit()
        print("Loaded companies and contacts.")

    # 2. Load Fair Editions
    fair_path = os.path.join(data_dir, "fair_editions.csv")
    if os.path.exists(fair_path):
        with open(fair_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                fc = row["fair_edition_code"].strip()
                if fc and fc not in seen_fairs:
                    seen_fairs.add(fc)
                    fair = models.FairEdition(
                        fair_edition_code=fc,
                        fair_name=row["fair_name"].strip(),
                        starts_on=parse_date(row["starts_on"]),
                        ends_on=parse_date(row["ends_on"]),
                        max_stand_area_sqm=None, # Not in CSV
                        max_stand_height_m=parse_euro_float(row["max_stand_height_m"])
                    )
                    db.add(fair)
        db.commit()
        print("Loaded fair editions.")

    # 3. Load Opportunities
    opp_path = os.path.join(data_dir, "opportunities.csv")
    if os.path.exists(opp_path):
        with open(opp_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                oc = row["opportunity_code"].strip()
                if oc and oc not in seen_opps:
                    seen_opps.add(oc)
                    opp = models.Opportunity(
                        opportunity_code=oc,
                        company_code=row["company_code"].strip(),
                        contact_code=row["contact_code"].strip(),
                        fair_edition_code=row["fair_edition_code"].strip(),
                        status=row["legacy_status"].strip() if row["legacy_status"] else None,
                        amount_eur=parse_euro_float(row["amount_eur"]),
                        stand_area_sqm=parse_euro_float(row["stand_area_sqm"]),
                        requested_height_m=parse_euro_float(row["requested_height_m"]),
                        client_budget_eur=parse_euro_float(row["client_budget_eur"]),
                        expected_close_on=parse_date(row["expected_close_on"]),
                        brief_notes=row["brief_notes"].strip()
                    )
                    db.add(opp)
        db.commit()
        print("Loaded opportunities.")

    # 4. Load Activity Log
    act_path = os.path.join(data_dir, "activity_log.csv")
    if os.path.exists(act_path):
        with open(act_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                ac = row["entry_id"].strip()
                if ac and ac not in seen_acts:
                    seen_acts.add(ac)
                    
                    # Fix for foreign keys missing in opportunities
                    opp_c = row["opportunity_code"].strip()
                    if not opp_c:
                        opp_c = None
                        
                    act = models.ActivityLog(
                        entry_id=ac,
                        company_code=row["company_code"].strip(),
                        opportunity_code=opp_c,
                        activity_type=row["activity_type"].strip(),
                        occurred_at=parse_datetime(row["occurred_at"]),
                        details=row["details"].strip(),
                        follow_up_on=parse_date(row["follow_up_on"]),
                        completion_marker=row["completion_marker"].strip(),
                        author=row["legacy_author"].strip()
                    )
                    db.add(act)
        db.commit()
        print("Loaded activity logs.")

    print("CSV Data Import Complete.")
