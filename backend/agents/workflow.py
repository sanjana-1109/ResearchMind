from langgraph.graph import StateGraph
from backend.agents.state import AgentState
from backend.agents.planner import planner_node
from backend.agents.executer import executor_node

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node('planner',planner_node)
    graph.add_node('executor',executor_node)

    graph.set_entry_point('planner')
    graph.add_edge('planner', 'executor')
    
    return graph.compile()








