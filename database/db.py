from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id            = Column(Integer, primary_key=True, index=True)
    national_id   = Column(String(14), unique=True, nullable=False, index=True)
    name          = Column(String(100), nullable=False)
    age           = Column(Integer)
    phone         = Column(String(20))
    created_at    = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id              = Column(Integer, primary_key=True, index=True)
    patient_id      = Column(Integer, nullable=False)
    doctor_name     = Column(String(100))
    date            = Column(DateTime, default=datetime.utcnow)
    transcript      = Column(Text)
    diagnosis       = Column(Text)
    medications     = Column(Text)
    follow_up       = Column(Text)
    warnings        = Column(Text)


DATABASE_URL = "sqlite:///./medical_records.db"
engine       = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_session(patient_id, doctor_name, transcript, diagnosis, medications, follow_up, warnings):
    db = SessionLocal()
    new_session = Session(
        patient_id  = patient_id,
        doctor_name = doctor_name,
        transcript  = transcript,
        diagnosis   = diagnosis,
        medications = medications,
        follow_up   = follow_up,
        warnings    = warnings
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    db.close()
    return new_session


def get_patient_history(patient_id):
    db = SessionLocal()
    sessions = db.query(Session).filter(Session.patient_id == patient_id).order_by(Session.date.desc()).all()
    db.close()
    return sessions


def create_patient(national_id, name, age, phone):
    db = SessionLocal()
    existing = db.query(Patient).filter(Patient.national_id == national_id).first()
    if existing:
        db.close()
        return None, "National ID already registered"
    patient = Patient(national_id=national_id, name=name, age=int(age), phone=phone)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()
    return patient, "success"


def get_patient_by_national_id(national_id):
    db = SessionLocal()
    patient = db.query(Patient).filter(Patient.national_id == national_id).first()
    db.close()
    return patient


def get_all_patients():
    db = SessionLocal()
    patients = db.query(Patient).all()
    db.close()
    return patients