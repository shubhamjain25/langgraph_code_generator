from agent.Schema import AppState

def hitl_router(p_state: AppState) -> str:
    """Route based on human review: proceed to architect or back to planner."""
    if p_state["status"] == "PLAN_REJECTED":
        return "REJECTED"
    else:
        return "APPROVED"

def coder_router(p_state: AppState) -> str:
    if p_state["status"]=="DONE":
        return "END"
    else:
        return "coder_node"

def reviewer_router(p_state: AppState) -> str:
    if p_state["status"]=="FIXING":
        return "END"
    else:
        return "coder_node"