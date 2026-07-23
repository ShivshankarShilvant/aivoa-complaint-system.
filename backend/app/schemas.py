from typing import Optional, List
from pydantic import BaseModel


class ComplaintExtractRequest(BaseModel):
    raw_text: str


class ComplaintFields(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    detailed_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class ComplaintExtractResponse(BaseModel):
    fields: ComplaintFields
    missing_fields: List[str] = []
    ai_extraction_confidence: float
    risk_classification: Optional[str] = None
    ai_summary: Optional[str] = None
    capa_recommendation: Optional[str] = None
    possible_duplicate_id: Optional[str] = None


class ComplaintCreate(ComplaintFields):
    raw_source_text: Optional[str] = None
    ai_extraction_confidence: Optional[float] = None
    missing_fields: Optional[List[str]] = None
    risk_classification: Optional[str] = None
    capa_recommendation: Optional[str] = None
    ai_summary: Optional[str] = None


class ComplaintOut(ComplaintCreate):
    id: str
    status: str

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    complaint_id: Optional[str] = None
    context_text: Optional[str] = None  # raw doc text if complaint not yet saved
    question: str


class ChatResponse(BaseModel):
    answer: str
