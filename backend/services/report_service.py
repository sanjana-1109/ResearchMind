from langchain_groq import ChatGroq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# Store last report globally
LAST_REPORT = ""

def generate_report(query, context, sources):
    global LAST_REPORT

    llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
    )

    sources = [str(s) for s in sources]

    prompt = f"""
    Generate a professional research report .

    Query: {query}

    Context:
    {context}

    Format:
    Title:
    Summary:
    Key Points:
    Detailed Explanation:
    Advantages & Limitations:
    Conclusion:
    Sources:
    {sources}
    """

    response = llm.invoke(prompt)
    LAST_REPORT = response.content   
    return LAST_REPORT


#  PDF Generator 
def generate_pdf(file_path="report.pdf"):
    global LAST_REPORT

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    for line in LAST_REPORT.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

    return file_path