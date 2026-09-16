import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. DEFINE THE CONNECTION URL
# We look for a DATABASE_URL environment variable. 
# If it doesn't exist, we fallback to a local SQLite database file so you don't need Docker.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./crm.db"
)

# 2. CREATE THE ENGINE
# The engine manages the actual physical network connection to the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# 3. CREATE THE SESSION FACTORY
# A 'Session' is a temporary workspace where we queue up changes (like adding a row).
# It only saves permanently to the database when we call `db.commit()`.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. CREATE THE BASE MODEL
# Every database table we create later will inherit from this Base class.
# It tells SQLAlchemy, "Hey, map this Python class to a real SQL table."
Base = declarative_base()

# 5. DEPENDENCY INJECTION FUNCTION
# This function creates a fresh database session for a web request and automatically closes it when done.
def get_db():
    """
    Creates a new database session for an API request and ensures it closes after use, 
    preventing memory leaks or locking up the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
