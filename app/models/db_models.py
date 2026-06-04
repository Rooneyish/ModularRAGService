from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

Base = declarative_base()

class DocumentMetadata(Base):
    __tablename__ = "document_metadata"
    
    id = Column(String, primary_key=True)
    filename = Column(String)
    chunking_strategy = Column(String)
    created_at = Column(String)

class InterviewBooking(Base):
    __tablename__ = "interview_bookings"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    booking_date = Column(String)
    booking_time = Column(String)
    created_at = Column(String)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()