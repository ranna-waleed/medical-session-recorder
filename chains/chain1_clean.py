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
    input_variables=["transcript"],
    template="""
    You are a medical assistant. You will receive a raw doctor-patient conversation transcript in Arabic or English.
    Your job is to:
    1. Clean any repeated words or filler sounds (um, ah, اه, ايه)
    2. Fix any obvious transcription errors
    3. Clearly label each line as either Doctor: or Patient:
    4. Keep the full meaning intact, do not remove any medical information

    Raw Transcript:
    {transcript}

    Return the cleaned and structured conversation only, nothing else.
    """
)

chain1 = prompt | llm

def clean_transcript(transcript: str) -> str:
    result = chain1.invoke({"transcript": transcript})
    return result.content