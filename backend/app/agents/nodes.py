"""
Each function is a LangGraph node. Every node takes the shared graph state
(a dict) and returns a partial dict of updates to merge into that state.
"""

from typing import TypedDict, List, Optional

from app.agents.groq_client import call_groq_json, call_groq
from app.config import settings

REQUIRED_FIELDS = [
    "complaint_source",
    "customer_name",
    "product_name",
    "batch_lot_number",
    "complaint_type",
    "detailed_description",
]


class ComplaintState(TypedDict, total=False):
    raw_text: str
    fields: dict
    missing_fields: List[str]
    ai_extraction_confidence: float
    risk_classification: str
    ai_summary: str
    capa_recommendation: str
    possible_duplicate_id: Optional[str]
    existing_complaints: List[dict]  # passed in for duplicate detection


EXTRACTION_SYSTEM = """You are a pharmaceutical QMS data-entry assistant. Extract
structured fields from a customer complaint document (email, letter, or report)
about an API (Active Pharmaceutical Ingredient) or FDF (Finished Dosage Form)
product. Only use information present in the text - never invent values.
If a field is not mentioned, use null. Respond with a single JSON object with
exactly these keys: complaint_source, customer_name, product_name,
product_strength_grade, batch_lot_number, manufacturing_date, expiry_date,
quantity_affected, complaint_type, complaint_date, detailed_description,
initial_severity, priority. Also include a "confidence" key (0.0-1.0) for how
confident you are in this extraction overall."""


def extract_fields_node(state: ComplaintState) -> dict:
    prompt = f"Complaint document:\n\n{state['raw_text']}\n\nExtract the fields now."
    result = call_groq_json(prompt, system=EXTRACTION_SYSTEM, model=settings.GROQ_EXTRACTION_MODEL)
    confidence = float(result.pop("confidence", 0.6) or 0.6)
    return {"fields": result, "ai_extraction_confidence": confidence}


def completeness_check_node(state: ComplaintState) -> dict:
    fields = state.get("fields", {})
    missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]
    return {"missing_fields": missing}


CLASSIFY_SYSTEM = """You are a pharmaceutical QMS risk assessor. Given complaint
details, classify the risk level. Respond with a JSON object:
{"risk_classification": "Critical" | "Major" | "Minor",
 "reasoning": "one short sentence"}
Critical = patient safety impact (e.g. contamination, wrong product, adverse
event). Major = quality defect with no immediate safety impact (e.g. dissolution
failure, packaging defect affecting several units). Minor = cosmetic or
documentation issue."""


def risk_classification_node(state: ComplaintState) -> dict:
    fields = state.get("fields", {})
    prompt = f"Complaint fields:\n{fields}\n\nClassify the risk."
    result = call_groq_json(prompt, system=CLASSIFY_SYSTEM, model=settings.GROQ_REASONING_MODEL)
    return {"risk_classification": result.get("risk_classification", "Minor")}


DUPLICATE_SYSTEM = """You compare a new pharmaceutical complaint against a list of
existing complaints. Respond with JSON: {"duplicate_id": "<id or null>",
"reasoning": "one short sentence"}. Only flag as duplicate if product, batch
number, and complaint type all closely match."""


def duplicate_check_node(state: ComplaintState) -> dict:
    existing = state.get("existing_complaints", [])
    if not existing:
        return {"possible_duplicate_id": None}
    fields = state.get("fields", {})
    prompt = f"New complaint:\n{fields}\n\nExisting complaints:\n{existing}\n\nCheck for a duplicate."
    result = call_groq_json(prompt, system=DUPLICATE_SYSTEM, model=settings.GROQ_REASONING_MODEL)
    return {"possible_duplicate_id": result.get("duplicate_id") or None}


CAPA_SYSTEM = """You are a QMS quality engineer. Given a complaint's details and
risk classification, suggest a brief CAPA (Corrective and Preventive Action)
recommendation in 2-3 sentences. Be specific to what was reported, not generic."""


def capa_recommendation_node(state: ComplaintState) -> dict:
    fields = state.get("fields", {})
    risk = state.get("risk_classification", "Minor")
    prompt = f"Complaint fields:\n{fields}\nRisk classification: {risk}\n\nSuggest a CAPA."
    text = call_groq(prompt, system=CAPA_SYSTEM, model=settings.GROQ_REASONING_MODEL)
    return {"capa_recommendation": text.strip()}


SUMMARY_SYSTEM = """Summarize this pharmaceutical complaint in 2 sentences for a
quality manager skimming a queue. Be factual and concise."""


def summary_node(state: ComplaintState) -> dict:
    fields = state.get("fields", {})
    text = call_groq(f"Complaint fields:\n{fields}", system=SUMMARY_SYSTEM, model=settings.GROQ_EXTRACTION_MODEL)
    return {"ai_summary": text.strip()}


CHAT_SYSTEM = """You are an AI Complaint Intake Assistant embedded in a
pharmaceutical QMS. Answer the user's question using ONLY the complaint context
given. If the answer isn't in the context, say you don't have that information.
Keep answers short and factual."""


def answer_chat_question(context_text: str, question: str) -> str:
    prompt = f"Complaint context:\n{context_text}\n\nQuestion: {question}"
    return call_groq(prompt, system=CHAT_SYSTEM, model=settings.GROQ_REASONING_MODEL, temperature=0.3)
