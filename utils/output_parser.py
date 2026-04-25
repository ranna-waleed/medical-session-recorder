import json
import re


def parse_output(cleaned_transcript: str, medical_data: str, doctor_summary: str, patient_summary: str) -> dict:
    """
    Parses the raw JSON string from chain2 and combines
    everything into one clean dictionary.
    """
    try:
        clean = re.sub(r"```json|```", "", medical_data).strip()
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        parsed = {
            "diagnosis": "Could not parse",
            "medications": [],
            "follow_up": "",
            "warnings": [],
            "tests_required": []
        }

    parsed["doctor_summary"] = doctor_summary
    parsed["patient_summary"] = patient_summary
    return parsed


def format_for_display(parsed: dict) -> str:
    output = []
    output.append(f"### Diagnosis\n{parsed.get('diagnosis', 'N/A')}\n")
    output.append(f"### Medications\n{parsed.get('medications', 'N/A')}\n")
    output.append(f"### Follow Up\n{parsed.get('follow_up', 'N/A')}\n")
    output.append(f"### Warnings\n{parsed.get('warnings', 'N/A')}\n")
    output.append(f"### Tests Required\n{parsed.get('tests_required', 'N/A')}\n")
    output.append(f"### Doctor Summary\n{parsed.get('doctor_summary', 'N/A')}\n")
    output.append(f"### Patient Summary\n{parsed.get('patient_summary', 'N/A')}\n")
    return "\n".join(output)