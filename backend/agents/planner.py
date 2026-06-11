from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant",temperature=0)

def planner_node(state:dict):
    query = state["query"]

    prompt = f"""
    You are a planning agent.

    Decide:
    1. Should we use web search? (yes/no)
    2. steps needed

    Query: {query}

    Retuen JSON:
    {{
        "use_web_search": true/false,
        "plan":["step1","step2"]   
    }}
    """
    try:
        response = llm.invoke(prompt).content

        import json
        parsed = json.loads(response)

        return {
            "plan":parsed.get("plan",[]),
            "use_web_search":parsed.get("use_web_search", False)
        }
    except Exception as e:
        print("Planner error", e)

        return {
            **state,
            "plan":["retrive_documents", "generate_report"],
            "use_web_search": False
        }
