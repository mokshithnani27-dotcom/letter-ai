import os
import streamlit as st
import ollama

# ---------- Config ----------
st.set_page_config(page_title="AI Cover Letter Generator", page_icon="✉️", layout="centered")

def get_setting(key, default=None):
    """Read from Streamlit secrets first, then environment variables."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

MODEL = get_setting("OLLAMA_MODEL", "gemma4")
HOST = get_setting("OLLAMA_HOST", "http://localhost:11434")
API_KEY = get_setting("OLLAMA_API_KEY")  # only needed for Ollama Cloud / protected hosts

def get_client():
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else None
    return ollama.Client(host=HOST, headers=headers)

MAX_WORDS = 300

# ---------- Prompt ----------
def build_prompt(d):
    return f"""You are an expert career coach who writes concise, personalized cover letters.

Write a cover letter using ONLY the facts provided below. Do not invent experience,
numbers, or achievements.

CANDIDATE
- Name: {d['name']}
- Degree: {d['degree']}
- Skills: {d['skills']}
- Projects / Internship: {d['experience']}

JOB
- Company: {d['company']}
- Role: {d['role']}
- Job Description:
{d['jd']}

REQUIREMENTS
- Strictly under {MAX_WORDS} words (aim for 220-270).
- Format: greeting ("Dear Hiring Manager,"), 3 short paragraphs, closing, and the candidate's name.
- Paragraph 1: enthusiasm for the role at {d['company']} and a one-line introduction.
- Paragraph 2: connect the candidate's most relevant skills/projects to the job description requirements.
- Paragraph 3: confident closing with a call to action.
- Professional, warm tone. No placeholders like [Your Address]. No markdown, no extra commentary.
- Output ONLY the cover letter text."""

def word_count(text):
    return len(text.split())

def generate_letter(d):
    client = get_client()
    messages = [{"role": "user", "content": build_prompt(d)}]
    letter = ""
    for _ in range(3):  # retry up to 3 times if too long
        resp = client.chat(model=MODEL, messages=messages, options={"temperature": 0.7})
        letter = resp["message"]["content"].strip()
        if word_count(letter) < MAX_WORDS:
            return letter
        messages = [
            {"role": "user", "content": build_prompt(d)},
            {"role": "assistant", "content": letter},
            {"role": "user", "content": f"That is {word_count(letter)} words. Shorten it to under 270 words. Output only the letter."},
        ]
    return letter

# ---------- UI ----------
st.title("✉️ AI Cover Letter Generator")
st.caption(f"Powered by Ollama • model: `{MODEL}`")

with st.form("letter_form"):
    st.subheader("👤 About You")
    c1, c2 = st.columns(2)
    name = c1.text_input("Full Name*", placeholder="Priya Sharma")
    degree = c2.text_input("Degree*", placeholder="B.E. Computer Science")
    skills = st.text_input("Skills*", placeholder="Python, SQL, React, Machine Learning")
    experience = st.text_area("Projects / Internship*", height=120,
                              placeholder="e.g. Built a sentiment analysis app using Python & Streamlit; 2-month internship at XYZ working on REST APIs")

    st.subheader("🏢 About the Job")
    c3, c4 = st.columns(2)
    company = c3.text_input("Company Name*", placeholder="Google")
    role = c4.text_input("Job Role*", placeholder="Software Engineer Intern")
    jd = st.text_area("Job Description*", height=180, placeholder="Paste the job description here...")

    submit = st.form_submit_button("🚀 Generate Cover Letter", use_container_width=True)

if submit:
    data = dict(name=name.strip(), degree=degree.strip(), skills=skills.strip(),
                experience=experience.strip(), company=company.strip(),
                role=role.strip(), jd=jd.strip())
    if not all(data.values()):
        st.error("Please fill in all the fields.")
    else:
        try:
            with st.spinner("Writing your cover letter..."):
                st.session_state["letter"] = generate_letter(data)
                st.session_state["fname"] = f"cover_letter_{data['company'].replace(' ', '_')}.txt"
        except Exception as e:
            st.error(f"Could not reach Ollama or the model. Is Ollama running and is `{MODEL}` pulled?\n\n{e}")

if "letter" in st.session_state:
    st.subheader("📄 Your Cover Letter")
    edited = st.text_area("You can edit before downloading:", st.session_state["letter"], height=380)
    wc = word_count(edited)
    st.caption(f"Word count: {wc} / {MAX_WORDS}" + ("  ✅" if wc < MAX_WORDS else "  ⚠️ over limit"))
    st.download_button("⬇️ Download as .txt", data=edited,
                       file_name=st.session_state["fname"], mime="text/plain",
                       use_container_width=True)