from langchain_core.globals import set_debug, set_verbose
from rich import print
from agent.graph import graph_agent

if __name__ == '__main__':

    set_debug(True)
    set_verbose(True)

    config = {"configurable": {"thread_id": 1, "recursion_limit": 15}}

    #Fetch current snapshot from the Checkpointer
    current_state = graph_agent.get_state(config)

    if current_state.next:
        #Crashed somewhere, fetched the old state & running it again from checkpoint
        state = graph_agent.invoke(None, config)
    else:
        # Running for the first time
        state = graph_agent.invoke({}, config)

    print("\n\n\n<-------FINAL STATE-------->\n\n\n")
    print(state)
