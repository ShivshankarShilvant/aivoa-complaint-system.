from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.agents.graph import run_complaint_pipeline

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _extract_text_from_upload(file: UploadFile) -> str:
    """Minimal text extraction. Production-grade OCR/doc parsing is explicitly
    not required by the assignment - plain text/PDF/DOCX text layers are enough."""
    content = file.file.read()
    if file.filename.lower().endswith(".pdf"):
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if file.filename.lower().endswith(".docx"):
        import io
        import docx

        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    # txt, eml, or anything else - treat as plain text
    return content.decode("utf-8", errors="ignore")


@router.post("/extract", response_model=schemas.ComplaintExtractResponse)
def extract_complaint(payload: schemas.ComplaintExtractRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Complaint)
        .order_by(models.Complaint.created_at.desc())
        .limit(50)
        .all()
    )
    existing_dicts = [
        {"id": c.id, "product_name": c.product_name, "batch_lot_number": c.batch_lot_number,
         "complaint_type": c.complaint_type}
        for c in existing
    ]

    result = run_complaint_pipeline(payload.raw_text, existing_complaints=existing_dicts)

    return schemas.ComplaintExtractResponse(
        fields=schemas.ComplaintFields(**result.get("fields", {})),
        missing_fields=result.get("missing_fields", []),
        ai_extraction_confidence=result.get("ai_extraction_confidence", 0.0),
        risk_classification=result.get("risk_classification"),
        ai_summary=result.get("ai_summary"),
        capa_recommendation=result.get("capa_recommendation"),
        possible_duplicate_id=result.get("possible_duplicate_id"),
    )


@router.post("/extract-file", response_model=schemas.ComplaintExtractResponse)
def extract_complaint_from_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = _extract_text_from_upload(file)
    return extract_complaint(schemas.ComplaintExtractRequest(raw_text=text), db)


@router.post("", response_model=schemas.ComplaintOut)
def save_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    complaint = models.Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint
