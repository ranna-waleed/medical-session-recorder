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

doctor_prompt = PromptTemplate(
    input_variables=["cleaned_transcript", "medical_data"],
    template="""
    You are a medical assistant generating a professional session summary for a doctor.
    Based on the conversation and extracted data below, write a concise clinical summary.
    Include: chief complaint, findings, diagnosis, treatment plan, and follow-up.
    Write in a professional medical tone in the same language as the conversation.

    Conversation:
    {cleaned_transcript}

    Extracted Data:
    {medical_data}

    Return the doctor summary only.
    """
)

patient_prompt = PromptTemplate(
    input_variables=["medical_data"],
    template="""
    You are a friendly medical assistant explaining a doctor's session to a patient.
    Based on the extracted medical data below, write a simple and clear summary for the patient.
    Use simple everyday language, no medical jargon.
    Include: what the doctor found, what medications to take and when, what to avoid, and when to come back.
    Write in Arabic.

    Extracted Data:
    {medical_data}

    Return the patient summary only.
    """
)

doctor_chain  = doctor_prompt  | llm
patient_chain = patient_prompt | llm


def generate_doctor_summary(cleaned_transcript: str, medical_data: str) -> str:
    result = doctor_chain.invoke({
        "cleaned_transcript": cleaned_transcript,
        "medical_data": medical_data
    })
    return result.content


def generate_patient_summary(medical_data: str) -> str:
    result = patient_chain.invoke({"medical_data": medical_data})
    return result.content