from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
)


def generate_answer(query, history):
    """General answer with no document context — uses LLM knowledge only."""

    prompt = f"""
You are a helpful AI assistant.

Conversation history:
{history}

User: {query}

Answer naturally and helpfully.
"""
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)


def generate_answer_with_context(query, context, history):
    """Answer grounded in uploaded document context + conversation history."""

    prompt = f"""
You are a helpful AI research assistant. Answer the user's question using the provided document context.

Rules:
- If the answer is found in the context, answer from it and be specific.
- If the context is not relevant to the question, answer from your general knowledge and mention it.
- Always be clear, concise, and helpful.
- Do NOT make up information that isn't in the context.

Document Context:
{context}

Conversation History:
{history}

User Question: {query}

Answer:
"""
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)