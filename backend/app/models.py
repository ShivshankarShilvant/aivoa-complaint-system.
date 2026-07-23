import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Float, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)

    # 1. Origin & customer details
    complaint_source = Column(String(100))
    customer_name = Column(String(255))

    # 2. Product & batch identification
    product_name = Column(String(255))
    product_strength_grade = Column(String(100))
    batch_lot_number = Column(String(100))
    manufacturing_date = Column(String(50))
    expiry_date = Column(String(50))
    quantity_affected = Column(String(50))

    # 3. Complaint details
    complaint_type = Column(String(100))
    complaint_date = Column(String(50))
    detailed_description = Column(Text)

    # 4. Initial assessment & priority
    initial_severity = Column(String(50))
    priority = Column(String(50))

    # AI metadata
    ai_extraction_confidence = Column(Float, nullable=True)
    missing_fields = Column(JSON, nullable=True)  # list of field names AI couldn't fill
    risk_classification = Column(String(50), nullable=True)
    duplicate_of = Column(String(36), nullable=True)  # id of a likely duplicate complaint
    capa_recommendation = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    raw_source_text = Column(Text, nullable=True)  # original uploaded doc/email text
    status = Column(String(50), default="Pending Triage")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
