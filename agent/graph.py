from langgraph.graph import StateGraph, START, END
from agent.graph_action import *
from langgraph.checkpoint.memory import InMemorySaver
from agent.graph_router import *
from langgraph.checkpoint.memory import InMemorySaver

#Call memory here
checkpointer = InMemorySaver()

builder = StateGraph(AppState)

# NODES
builder.add_node("input_node", user_input)
builder.add_node("planner_node", subagent_plan)
builder.add_node("hitl_review_node", hitl_review)
builder.add_node("architect_node", subagent_architect)
builder.add_node("coder_node", subagent_coder)

# TO BE DONE LATER WITH MORE TIME
# builder.add_node("reviewer_node", subagent_reviewer)
# builder.add_node("fixer_node", subagent_fixer)

# EDGES
builder.add_edge(START, "input_node")
builder.add_edge("input_node", "planner_node")
builder.add_edge("planner_node", "hitl_review_node")
builder.add_conditional_edges(
    "hitl_review_node",
    hitl_router, {
        "APPROVED": "architect_node",
        "REJECTED": "planner_node",
    }
)
builder.add_edge("architect_node", "coder_node")
builder.add_conditional_edges(
    "coder_node",
    coder_router,{
        "END": END,
        "coder_node": "coder_node",
    }
)

graph_agent = builder.compile(
    checkpointer=checkpointer,
)

# TO BE DONE LATER WITH MORE TIME
# builder.add_edge("coder_node", "reviewer_node")
# builder.add_conditional_edges(
#     "reviewer_node",
#     reviewer_router,{
#         "END":END,
#         "FIXING": "fixer_node"
#     }
# )