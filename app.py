import streamlit as st
import os
import json
import tempfile
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder

from database.db import (
    init_db, save_session, get_patient_history,
    create_patient, get_all_patients, get_patient_by_national_id
)
from utils.transcriber import transcribe_audio
from chains.chain1_clean import clean_transcript
from chains.chain2_extract import extract_medical_data
from chains.chain3_summarize import generate_doctor_summary, generate_patient_summary
from utils.output_parser import parse_output, format_for_display

load_dotenv()
init_db()

st.set_page_config(
    page_title="MediScribe AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Fix white bar at top ── */
header[data-testid="stHeader"] {
    background: #111827 !important;
    border-bottom: 1px solid #1f2f45 !important;
}

.stApp {
    background: #111827 !important;
    color: #e2e8f0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f1f35 !important;
    border-right: 1px solid #1f3050 !important;
}

[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}

[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
    cursor: pointer !important;
    color: #cbd5e1 !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: #1a3050 !important;
    color: #38bdf8 !important;
}

.sidebar-logo {
    padding: 24px 20px 32px;
    border-bottom: 1px solid #1f3050;
    margin-bottom: 24px;
}

.sidebar-logo h1 {
    font-family: 'Instrument Serif', serif;
    font-size: 28px;
    color: #f1f5f9;
    margin: 0;
}

.sidebar-logo span { color: #38bdf8; }

.sidebar-logo p {
    font-size: 11px;
    color: #64748b;
    margin: 6px 0 0;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ── Page header ── */
.page-header {
    background: #1a2f4a;
    border: 1px solid #2a4a6a;
    border-radius: 20px;
    padding: 36px 40px;
    margin-bottom: 32px;
}

.page-header h2 {
    font-family: 'Instrument Serif', serif;
    font-size: 34px;
    color: #f1f5f9;
    margin: 0 0 10px;
    font-weight: 400;
}

.page-header p {
    color: #94a3b8;
    font-size: 16px;
    margin: 0;
}

/* ── Cards ── */
.card {
    background: #1a2840;
    border: 1px solid #2a3f5f;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}

.card-title {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 20px;
}

/* ── Patient badge ── */
.patient-badge {
    background: #0f2d1f;
    border: 1px solid #1a5c30;
    border-radius: 12px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 16px 0;
}

.patient-avatar {
    width: 52px;
    height: 52px;
    background: #1a4a3a;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.patient-info h4 {
    color: #4ade80;
    font-size: 17px;
    font-weight: 700;
    margin: 0 0 5px;
}

.patient-info p {
    color: #86efac;
    font-size: 13px;
    margin: 0;
}

/* ── Result badges ── */
.result-header {
    font-size: 14px;
    font-weight: 700;
    color: #94a3b8;
    margin: 16px 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.result-value {
    background: #0f1f35;
    border: 1px solid #2a3f5f;
    border-radius: 10px;
    padding: 16px 18px;
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.7;
    margin-bottom: 8px;
}

.diagnosis-badge {
    display: inline-block;
    background: #1e1b4b;
    border: 1px solid #4338ca;
    color: #c4b5fd;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    margin: 4px 4px 4px 0;
}

.med-badge {
    display: inline-block;
    background: #0f2d1f;
    border: 1px solid #16a34a;
    color: #86efac;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    margin: 4px 4px 4px 0;
}

.warning-badge {
    display: inline-block;
    background: #2d1f0f;
    border: 1px solid #d97706;
    color: #fcd34d;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    margin: 4px 4px 4px 0;
}

/* ── Inputs ── */
.stTextInput input,
.stNumberInput input {
    background: #0f1f35 !important;
    border: 1.5px solid #2a3f5f !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-size: 15px !important;
    padding: 12px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px #38bdf825 !important;
}

.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: #cbd5e1 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #4a6080 !important;
}

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, #0369a1, #0284c7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, #0284c7, #0ea5e9) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px #38bdf840 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1f35 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid #2a3f5f !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stTabs [aria-selected="true"] {
    background: #1a3a5a !important;
    color: #38bdf8 !important;
}

/* ── Fix audio recorder white background ── */
.audio-recorder,
[data-testid="stCustomComponentV1"],
.stCustomComponentV1,
iframe {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color-scheme: dark !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-size: 15px !important;
}

.stSuccess > div {
    background: #0f2d1f !important;
    border: 1px solid #16a34a !important;
    color: #86efac !important;
    border-radius: 10px !important;
    font-size: 15px !important;
}

.stError > div {
    background: #2d0f0f !important;
    border: 1px solid #dc2626 !important;
    border-radius: 10px !important;
    font-size: 15px !important;
}

.stInfo > div {
    background: #0f1f3d !important;
    border: 1px solid #1d4ed8 !important;
    border-radius: 10px !important;
    font-size: 15px !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #1a2840 !important;
    border: 1px solid #2a3f5f !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
}

[data-testid="stExpander"] summary {
    color: #e2e8f0 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

/* ── General text ── */
p, span, div, label {
    font-size: 15px !important;
    line-height: 1.7 !important;
}

h1, h2, h3 {
    color: #f1f5f9 !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div {
    background: #38bdf8 !important;
    border-radius: 4px !important;
}

/* ── Divider ── */
hr {
    border-color: #2a3f5f !important;
    margin: 28px 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f1f35; }
::-webkit-scrollbar-thumb { background: #2a3f5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a5f7f; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h1>Medi<span>Scribe</span></h1>
        <p>AI Medical Recorder</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🩺  New Session", "📂  Patient History", "➕  Register Patient"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    patients = get_all_patients()
    total    = len(patients)

    st.markdown(f"""
    <div style="padding: 0 8px;">
        <div style="font-size:12px; color:#64748b; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:14px; font-weight:700;">
            System Stats
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
            <span style="color:#94a3b8; font-size:14px;">Total Patients</span>
            <span style="color:#38bdf8; font-weight:700; font-size:14px;">{total}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#94a3b8; font-size:14px;">AI Model</span>
            <span style="color:#4ade80; font-weight:700; font-size:12px;">LLaMA 3.3 70B</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PAGE 1 — NEW SESSION
# ══════════════════════════════════════════════════════════
if "New Session" in page:

    st.markdown("""
    <div class="page-header">
        <h2>New Medical Session</h2>
        <p>Record or upload a doctor-patient session and let AI handle the rest</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card"><div class="card-title">👤 Session Details</div>', unsafe_allow_html=True)
        doctor_name       = st.text_input("Doctor Name", placeholder="Dr. Ahmed Hassan")
        national_id_input = st.text_input("Patient National ID", placeholder="12345678901234", max_chars=14)
        st.markdown('</div>', unsafe_allow_html=True)

        patient = None
        if national_id_input:
            patient = get_patient_by_national_id(national_id_input)
            if patient:
                st.markdown(f"""
                <div class="patient-badge">
                    <div class="patient-avatar">👤</div>
                    <div class="patient-info">
                        <h4>✓ {patient.name}</h4>
                        <p>Age {patient.age}  •  {patient.phone}  •  ID {national_id_input}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("No patient found with this National ID.")

    with col_right:
        st.markdown('<div class="card"><div class="card-title">🎙️ Session Audio</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🎙️  Record Live", "📁  Upload File"])

        audio_bytes = None
        audio_file  = None

        with tab1:
            st.info("Click the button below to start recording. Click again to stop.")
            audio_bytes = audio_recorder(
                text="Click to Record",
                recording_color="#e74c3c",
                neutral_color="#38bdf8",
                icon_size="2x"
            )
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                st.success("Recording ready!")

        with tab2:
            audio_file = st.file_uploader(
                "Drop your audio file here",
                type=["mp3", "wav", "m4a"],
                label_visibility="collapsed"
            )
            if audio_file:
                st.audio(audio_file)

        st.markdown('</div>', unsafe_allow_html=True)

    has_audio = audio_bytes if audio_bytes else audio_file

    if has_audio and doctor_name and patient:
        if st.button("🚀  Process Session with AI", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes if audio_bytes else audio_file.read())
                tmp_path = tmp.name

            steps = [
                ("🎧", "Transcribing audio with Whisper..."),
                ("🧹", "Cleaning transcript..."),
                ("🔬", "Extracting medical data..."),
                ("📝", "Generating summaries..."),
                ("✅", "Finalizing output..."),
            ]

            progress_bar = st.progress(0)
            status_text  = st.empty()

            try:
                status_text.markdown(f"**{steps[0][0]} {steps[0][1]}**")
                transcript = transcribe_audio(tmp_path)
                progress_bar.progress(20)

                status_text.markdown(f"**{steps[1][0]} {steps[1][1]}**")
                cleaned = clean_transcript(transcript)
                progress_bar.progress(40)

                status_text.markdown(f"**{steps[2][0]} {steps[2][1]}**")
                medical_data = extract_medical_data(cleaned)
                progress_bar.progress(60)

                status_text.markdown(f"**{steps[3][0]} {steps[3][1]}**")
                doctor_summary  = generate_doctor_summary(cleaned, medical_data)
                patient_summary = generate_patient_summary(medical_data)
                progress_bar.progress(80)

                status_text.markdown(f"**{steps[4][0]} {steps[4][1]}**")
                parsed = parse_output(cleaned, medical_data, doctor_summary, patient_summary)
                progress_bar.progress(100)

                save_session(
                    patient_id  = patient.id,
                    doctor_name = doctor_name,
                    transcript  = cleaned,
                    diagnosis   = parsed.get("diagnosis", ""),
                    medications = json.dumps(parsed.get("medications", []), ensure_ascii=False),
                    follow_up   = parsed.get("follow_up", ""),
                    warnings    = json.dumps(parsed.get("warnings", []), ensure_ascii=False)
                )
                os.remove(tmp_path)

                status_text.empty()
                progress_bar.empty()

                st.success("Session processed and saved successfully!")
                st.markdown("---")

                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown('<div class="card"><div class="card-title">👨‍⚕️ Doctor Summary</div>', unsafe_allow_html=True)

                    diag = parsed.get("diagnosis", "N/A")
                    st.markdown(f'<div class="result-header">Diagnosis</div><div class="diagnosis-badge">{diag}</div>', unsafe_allow_html=True)

                    meds = parsed.get("medications", [])
                    st.markdown('<div class="result-header" style="margin-top:16px;">Medications</div>', unsafe_allow_html=True)
                    if isinstance(meds, list):
                        for m in meds:
                            if isinstance(m, dict):
                                st.markdown(f'<span class="med-badge">💊 {m.get("name","")} — {m.get("dosage","")} × {m.get("frequency","")}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="med-badge">💊 {meds}</span>', unsafe_allow_html=True)

                    warnings = parsed.get("warnings", [])
                    if warnings:
                        st.markdown('<div class="result-header" style="margin-top:16px;">Warnings</div>', unsafe_allow_html=True)
                        if isinstance(warnings, list):
                            for w in warnings:
                                st.markdown(f'<span class="warning-badge">⚠️ {w}</span>', unsafe_allow_html=True)

                    follow = parsed.get("follow_up", "N/A")
                    st.markdown(f'<div class="result-header" style="margin-top:16px;">Follow Up</div><div class="result-value">📅 {follow}</div>', unsafe_allow_html=True)

                    summary = parsed.get("doctor_summary", "N/A")
                    st.markdown(f'<div class="result-header">Clinical Summary</div><div class="result-value">{summary}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="card"><div class="card-title">🧑‍💼 Patient Summary</div>', unsafe_allow_html=True)
                    patient_sum = parsed.get("patient_summary", "N/A")
                    st.markdown(f'<div class="result-value" style="direction:rtl; text-align:right; line-height:2;">{patient_sum}</div>', unsafe_allow_html=True)

                    tests = parsed.get("tests_required")
                    if tests and tests != "null":
                        st.markdown('<div class="result-header" style="margin-top:16px;">Tests Required</div>', unsafe_allow_html=True)
                        if isinstance(tests, list):
                            for t in tests:
                                st.markdown(f'<span class="diagnosis-badge">🔬 {t}</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"Error: {str(e)}")
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


# ══════════════════════════════════════════════════════════
# PAGE 2 — PATIENT HISTORY
# ══════════════════════════════════════════════════════════
elif "History" in page:

    st.markdown("""
    <div class="page-header">
        <h2>Patient History</h2>
        <p>Search any patient by their National ID to view full medical history</p>
    </div>
    """, unsafe_allow_html=True)

    national_id_input = st.text_input("🔍  Search by National ID", placeholder="Enter 14-digit National ID", max_chars=14)

    if national_id_input:
        patient = get_patient_by_national_id(national_id_input)
        if not patient:
            st.error("No patient found with this National ID.")
        else:
            st.markdown(f"""
            <div class="patient-badge">
                <div class="patient-avatar">👤</div>
                <div class="patient-info">
                    <h4>{patient.name}</h4>
                    <p>Age {patient.age}  •  {patient.phone}  •  ID {national_id_input}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            history = get_patient_history(patient.id)

            if not history:
                st.info("No sessions recorded for this patient yet.")
            else:
                st.markdown(f"""
                <div style="font-size:15px; color:#94a3b8; margin-bottom:20px; font-weight:600;">
                    {len(history)} session(s) found
                </div>
                """, unsafe_allow_html=True)

                for session in history:
                    with st.expander(f"📅  {session.date.strftime('%d %b %Y  %H:%M')}  —  Dr. {session.doctor_name}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**🔬 Diagnosis:** {session.diagnosis}")
                            st.markdown(f"**💊 Medications:** {session.medications}")
                            st.markdown(f"**📅 Follow Up:** {session.follow_up}")
                            st.markdown(f"**⚠️ Warnings:** {session.warnings}")
                        with c2:
                            st.text_area("Transcript", session.transcript, height=180, key=f"t_{session.id}")


# ══════════════════════════════════════════════════════════
# PAGE 3 — REGISTER PATIENT
# ══════════════════════════════════════════════════════════
elif "Register" in page:

    st.markdown("""
    <div class="page-header">
        <h2>Register New Patient</h2>
        <p>Add a new patient to the system using their National ID</p>
    </div>
    """, unsafe_allow_html=True)

    col, _ = st.columns([1.2, 1])

    with col:
        st.markdown('<div class="card"><div class="card-title">📋 Patient Information</div>', unsafe_allow_html=True)

        with st.form("register_form"):
            national_id = st.text_input("National ID Number", placeholder="14-digit National ID", max_chars=14)
            name        = st.text_input("Full Name", placeholder="Ahmed Mohamed")
            age         = st.number_input("Age", min_value=1, max_value=120, value=30)
            phone       = st.text_input("Phone Number", placeholder="010XXXXXXXX")
            submitted   = st.form_submit_button("➕  Register Patient", use_container_width=True)

            if submitted:
                if national_id and name and phone:
                    patient, message = create_patient(
                        national_id=national_id,
                        name=name,
                        age=int(age),
                        phone=phone
                    )
                    if message == "success":
                        st.success(f"✅ Patient **{patient.name}** registered successfully!")
                    else:
                        st.error("This National ID is already registered.")
                else:
                    st.error("Please fill in all fields.")

        st.markdown('</div>', unsafe_allow_html=True)