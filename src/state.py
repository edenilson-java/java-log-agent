from typing import Any, Dict, List, Literal, TypedDict


class AgentState(TypedDict, total=False):
    """
    Estado do agente JavaLog, mantendo o contexto de curto prazo durante a execução.
    """

    file_path: str
    log_content: str
    extracted_events: List[str]
    exceptions: List[str]
    category: str
    evidence: List[str]
    diagnostic: Dict[str, Any]
    report_path: str
    status: Literal[
        "success",
        "success_fallback",
        "success_no_errors",
        "invalid_output",
        "error",
    ]
    error: str
    validation_errors: List[str]
