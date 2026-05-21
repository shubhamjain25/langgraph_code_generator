from agent.Schema import *

def get_planner_prompt(user_prompt: str, hitl_feedback=""):
    planner_prompt = f"""
        You are the PLANNER agent. Convert the user prompt into a COMPLETE engineering project plan.
        User request:
        {user_prompt}
        
        Return strictly in the format{AppPlanner.model_json_schema()} and do not provide any metadata or any other information other than the schema.
    """

    if hitl_feedback and hitl_feedback != "":
        planner_prompt += f"\n\nFeedback to be taken into consideration: {hitl_feedback}"

    return planner_prompt


def get_architect_prompt(f: Files) -> str:
    architect_prompt = f"""
        You are the ARCHITECT agent. 
        For all the files present in {f} provide atleast one or more architecture related decisions so the forthcoming coder node can look at the instructions provided and execute their tasks accordingly.
        Use the best coding practices and appropriate syntax related information to make sure everything is correct & cohesive.
        
        Return strictly in the format{AppArchitecture.model_json_schema()} and do not provide any metadata or any other information other than the schema.
    """
    return architect_prompt


def get_coder_prompt() -> str:
    coder_system_prompt = f"""
        You are the CODER agent.
        You are implementing a specific engineering task.
        You have access to tools to read and write files.

    Always:
    - Review all existing files to maintain compatibility.
    - Implement the FULL file content, integrating with other modules.
    - Maintain consistent naming of variables, functions, and imports.
    - When a module is imported from another file, ensure it exists and is implemented as described.
    
    Return strictly in the format{CodeFile.model_json_schema()} and do not provide any metadata or any other information other than the schema.
    """

    return coder_system_prompt
