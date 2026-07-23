from langgraph.graph import StateGraph, END

from app.agents.nodes import (
    ComplaintState,
    extract_fields_node,
    completeness_check_node,
    risk_classification_node,
    duplicate_check_node,
    capa_recommendation_node,
    summary_node,
)


def route_after_completeness(state: ComplaintState) -> str:
    """If extraction confidence is very low, skip straight to summary so the
    user gets something back quickly and can fix fields manually instead of
    letting downstream nodes reason over garbage data."""
    if state.get("ai_extraction_confidence", 1.0) < 0.3:
        return "low_confidence"
    return "continue"


def build_complaint_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node("extract", extract_fields_node)
    graph.add_node("completeness_check", completeness_check_node)
    graph.add_node("classify_risk", risk_classification_node)
    graph.add_node("duplicate_check", duplicate_check_node)
    graph.add_node("recommend_capa", capa_recommendation_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "completeness_check")

    graph.add_conditional_edges(
        "completeness_check",
        route_after_completeness,
        {"continue": "classify_risk", "low_confidence": "summary"},
    )

    graph.add_edge("classify_risk", "duplicate_check")
    graph.add_edge("duplicate_check", "recommend_capa")
    graph.add_edge("recommend_capa", "summary")
    graph.add_edge("summary", END)

    return graph.compile()


# Compiled once at import time and reused across requests.
complaint_graph = build_complaint_graph()


def run_complaint_pipeline(raw_text: str, existing_complaints: list | None = None) -> dict:
    initial_state: ComplaintState = {
        "raw_text": raw_text,
        "existing_complaints": existing_complaints or [],
    }
    return complaint_graph.invoke(initial_state)
