from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

prompt = PromptTemplate(
    input_variables=["cleaned_transcript"],
    template="""
    You are a medical data extractor. You will receive a cleaned doctor-patient conversation.
    Extract the following information in JSON format:

    {{
        "diagnosis": "the main diagnosis or condition identified",
        "medications": [
            {{
                "name": "medication name",
                "dosage": "dosage amount",
                "frequency": "how many times per day",
                "duration": "how many days"
            }}
        ],
        "follow_up": "follow up date or instruction",
        "warnings": ["warning 1", "warning 2"],
        "tests_required": ["any lab tests or scans requested"]
    }}

    If any field is not mentioned in the conversation, set it to null.
    Return only the JSON, nothing else.

    Conversation:
    {cleaned_transcript}
    """
)

chain2 = prompt | llm

def extract_medical_data(cleaned_transcript: str) -> str:
    result = chain2.invoke({"cleaned_transcript": cleaned_transcript})
    return result.content