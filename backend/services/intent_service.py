from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

def detect_intent_llm(query: str):
    prompt = f"""
Classify the user query into ONE of these categories:
- greeting
- introduction
- qa
- report

Query: {query}

Answer ONLY the category name.
"""

    res = llm.invoke(prompt).content.strip().lower()

    return res