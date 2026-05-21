import json
from asyncio import current_task

from agent.Schema import *
from agent.prompts import *
from agent.llm_model import *
from langchain.agents import create_agent
from agent.tools import *
from langgraph.prebuilt import create_react_agent
import time

llm_creative = get_creative_llm_model()
llm_deterministic = get_deterministic_llm_model()

tools_list = [read_file, write_file, list_files, get_current_directory, run_cmd]
# llm_reactive = create_react_agent(llm, tools=tools_list)

def user_input(p_state: AppState) -> dict :

    user_prompt = input("Provide the app that you want to design: ")

    return {"user_input": user_prompt, "status": "STARTED"}


def subagent_plan(p_state: AppState) -> dict :

    query_prompt = get_planner_prompt(p_state["user_input"], p_state.get("hitl_feedback", None))

    if query_prompt is None:
        raise ValueError("Unable to get prompt for planner agent")

    llm_resp = llm_creative.invoke(query_prompt)

    if llm_resp is None:
        raise ValueError("Unable to get response from LLM for planner agent")

    try:
        data = json.loads(llm_resp.content)
        formatted_resp = AppPlanner(**data)
    except ValueError as e:
        raise ValueError(f"Error while formatting Plan Code Agent Response: {e}")

    return {"plan": formatted_resp, "status": "PLANNED"}


def hitl_review(p_state: AppState) -> dict :
    """Human-in-the-loop review of the plan."""
    
    plan = p_state["plan"]
    
    # Display the plan to human
    print("\n" + "="*80)
    print("PLAN REVIEW - HUMAN IN THE LOOP")
    print("="*80)
    print(f"\n📱 App Name: {plan.appname}")
    print(f"\n📝 Description: {plan.description}")
    print(f"\n🛠️  Tech Stack: {', '.join(plan.tech_stack)}")
    print(f"\n✨ Features:")
    for i, feature in enumerate(plan.features, 1):
        print(f"   {i}. {feature}")
    print(f"\n📁 Files to be created:")
    for file in plan.files:
        print(f"   - {file.filename}: {file.purpose}")
    print("\n" + "="*80)
    
    # Get human feedback
    print("\nOptions:")
    print("  [A] Approve and proceed")
    print("  [F] Provide feedback for changes")
    
    choice = input("\nEnter choice (A/F): ").strip().upper()
    
    if choice == "A":
        print("\n✅ Plan approved! Proceeding to architecture...")
        return {"status": "PLAN_APPROVED", "hitl_feedback": None}
    
    elif choice == "F":
        feedback = input("\nEnter your feedback: ").strip()
        if feedback:
            print(f"\n📝 Feedback received: {feedback}")
            print("Going back to planner with feedback...")
            return {
                "status": "PLAN_REJECTED",
                "user_input": f"Previous plan: {plan.appname}\n\nUser feedback: {feedback}\n\nPlease revise the plan based on this feedback.",
                "hitl_feedback": feedback
            }
        else:
            print("No feedback provided. Proceeding with approval...")
            return {"status": "PLAN_APPROVED", "hitl_feedback": None}
    
    else:
        print("\nInvalid choice. Defaulting to approval...")
        return {"status": "PLAN_APPROVED", "hitl_feedback": None}


def subagent_architect(p_state: AppState) -> dict :

    query_prompt = get_architect_prompt(p_state["plan"].files)

    if query_prompt is None:
        raise ValueError("Unable to prompt for architect agent")

    llm_resp = llm_creative.invoke(query_prompt)

    if llm_resp is None:
        raise ValueError("Unable to get response from LLM for architect agent")

    try:
        data = json.loads(llm_resp.content)
        formatted_resp = AppArchitecture(**data)
    except ValueError as e:
        raise ValueError(f"Error while formatting Architecture Code Agent Response: {e}")

    return {"architecture": formatted_resp, "status": "ARCHITECTED"}

# def subagent_coder(p_state: AppState) -> dict :
#
#     sys_prompt = get_coder_prompt()
#     files_completely_done = 0
#     curr_itr = p_state.get("coding_iteration", 0)
#
#     for file_architecture in p_state["architecture"].architecture_files:
#
#         target_path = file_architecture.filepath.lstrip("\\/")
#         existing_content = read_file.invoke({"path": target_path})
#
#         user_prompt = f"""
#         Task: Create/Update the following file based on the architecture instructions.
#         Architecture: {file_architecture.instructions}\n
#         File Path: {target_path}\n
#         Existing Content: \n\n{existing_content}\n\n
#
#         When you are finished writing the code and verifying it, reply with 'DONE'.
#         """
#         # 3. Execution
#         print(f"\n--- Coding File: {target_path} (Iteration: {curr_itr + 1}) ---")
#
#         time.sleep(2)
#         print("\n<---------SLEPT FOR 2S------------>\n")
#         llm_resp = llm_reactive.invoke({"messages": [{"role": "system", "content": sys_prompt},
#                                           {"role": "user", "content": user_prompt}]})
#
#         last_msg = llm_resp["messages"][-1].content
#
#         if "DONE" in last_msg.upper():
#             files_completely_done += 1
#
#     curr_itr+=1
#
#     if files_completely_done == len(p_state["architecture"].architecture_files):
#         return {"status": "DONE", "coding_iteration": curr_itr}
#
#     if curr_itr>=5:
#         return {"status": "DONE", "coding_iteration": curr_itr}
#
#     return {"status": "CODING", "coding_iteration": curr_itr}

def subagent_coder(p_state: AppState) -> dict:

    sys_prompt = get_coder_prompt()

    needs_more_work = False
    curr_itr = p_state.get("coding_iteration", 0)

    for file_architecture in p_state["architecture"].architecture_files:

        # --- CLEAN PATH ---
        target_path = file_architecture.filepath.lstrip("\\/")

        # --- READ EXISTING CONTENT (used for iterative improvement) ---
        existing_content = read_file.invoke({"path": target_path})

        # =========================
        # STEP 1: GENERATE CODE
        # =========================
        user_prompt = f"""
        You are improving an existing file.
        GOAL:
        Incrementally improve the code without breaking working parts.

        Architecture Instructions:
        {file_architecture.instructions}

        File Path:
        {target_path}

        Existing Content (if any):
        {existing_content}

        RULES:
        - DO NOT rewrite from scratch unless necessary
        - PRESERVE working logic
        - ONLY improve or fix issues
        - Output ONLY code
        - No markdown
        - No backticks
        - No explanation
        """

        print(f"\n--- Coding File: {target_path} (Iteration: {curr_itr + 1}) ---")

        time.sleep(3)

        llm_resp = llm_deterministic.invoke([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ])

        code = llm_resp.content.strip()

        # --- CLEANUP (in case model still adds formatting) ---
        code = code.replace("```", "").replace("```python", "").strip()

        # =========================
        # STEP 2: CRITIC (NEW)
        # =========================
        critique_prompt = f"""
        You are a strict senior engineer.

        Compare OLD vs NEW code.

        OLD CODE:
        {existing_content}

        NEW CODE:
        {code}

        Check:
        1. Did the new code improve or degrade?
        2. Any bugs introduced?
        3. Missing functionality?

        Review the following code for:
        - syntax errors
        - missing imports
        - logical mistakes
        - incomplete implementation
        
        Architecture:
        {file_architecture.instructions}

        Code:
        {code}
        
        Return ONLY:
        - OK
        OR
        - FIX: <issues>
        """

        time.sleep(3)
        critique_resp = llm_deterministic.invoke(critique_prompt)
        critique = critique_resp.content.strip()

        print(f"Critique Result: {critique}")

        # =========================
        # STEP 3: FIX IF NEEDED (NEW)
        # =========================
        if critique.startswith("FIX"):

            needs_more_work = True  # 🔥 THIS DRIVES LOOP

            fix_prompt = f"""
            Fix the code based on the issues below.

            Issues:
            {critique}

            Original code:
            {code}

            RULES:
            - Return ONLY corrected code
            - No explanation
            - No markdown
            """

            time.sleep(3)
            fix_resp = llm_deterministic.invoke(fix_prompt)
            code = fix_resp.content.strip()

            # --- CLEAN AGAIN ---
            code = code.replace("```", "").replace("```python", "").strip()

            print("Code was fixed based on critique.")

        # =========================
        # STEP 4: WRITE FILE (FORCED EXECUTION - CRITICAL FIX)
        # =========================
        write_file.invoke({
            "path": target_path,
            "content": code
        })

    # =========================
    # ITERATION MANAGEMENT
    # =========================
    curr_itr += 1

    # --- IF ALL FILES DONE ---
    # if files_completely_done == len(p_state["architecture"].architecture_files):
    #     return {"status": "DONE", "coding_iteration": curr_itr}
    #
    # # --- SAFETY EXIT ---
    # if curr_itr >= 5:
    #     return {"status": "DONE", "coding_iteration": curr_itr}

    if needs_more_work and curr_itr < 5:
        return {"status": "CODING", "coding_iteration": curr_itr}

    return {"status": "DONE", "coding_iteration": curr_itr}

# def subagent_reviewer(p_state: AppState) -> dict:
#
# def subagent_fixer(p_state: AppState) -> dict: