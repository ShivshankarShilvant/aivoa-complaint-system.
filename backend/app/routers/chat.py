from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.agents.nodes import answer_chat_question

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    context_text = payload.context_text

    if payload.complaint_id:
        complaint = db.query(models.Complaint).filter(models.Complaint.id == payload.complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        context_text = complaint.raw_source_text or str(complaint.__dict__)

    if not context_text:
        raise HTTPException(status_code=400, detail="No complaint context available")

    answer = answer_chat_question(context_text, payload.question)
    return schemas.ChatResponse(answer=answer)
