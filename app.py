import os
import re
import requests
import streamlit as st

st.set_page_config(page_title="AI Cover Letter Generator", page_icon="✉️", layout="centered")

st.markdown("""
<style>
    .main {max-width: 900px; padding-top: 2rem;}
    .hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#172554,#2563eb); color:white; margin-bottom:1.2rem;}
    .hero h1 {color:white; margin:0 0 .4rem 0;}
    .hero p {color:#dbeafe; margin:0;}
    div[data-testid="stForm"] {border:1px solid rgba(128,128,128,.25); border-radius:14px; padding:1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>✉️ AI Cover Letter Generator</h1>
  <p>Create a tailored, professional cover letter in seconds — powered by Ollama + Gemma 4.</p>
</div>
""", unsafe_allow_html=True)

def get_config():
    # Streamlit Cloud: configure these in App → Settings → Secrets.
    # Local development: environment variables or .streamlit/secrets.toml.
    try:
        host = st.secrets.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        model = st.secrets.get("OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "gemma4"))
        api_key = st.secrets.get("OLLAMA_API_KEY", os.getenv("OLLAMA_API_KEY", ""))
    except Exception:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma4")
        api_key = os.getenv("OLLAMA_API_KEY", "")
    return str(host).rstrip("/"), str(model), str(api_key)

def generate_cover_letter(profile, job, host, model, api_key):
    prompt = f"""You are an expert career coach and professional cover-letter writer.

Write one personalized cover letter using ONLY the candidate facts provided below.
Requirements:
- Maximum 300 words (strictly).
- Professional, confident, natural and specific; avoid clichés and exaggerated claims.
- Connect the candidate's actual skills, projects and internship experience to the job description.
- Do not invent achievements, experience, metrics, qualifications, tools or company facts.
- If information is missing, omit it rather than guessing.
- Include a greeting, 3 concise body paragraphs, and a professional closing.
- Do not include a subject line, markdown headings, commentary, or a word count.
- Use placeholders only for missing contact details, not for facts.

CANDIDATE
Name: {profile['name']}
Degree: {profile['degree']}
Skills: {profile['skills']}
Projects: {profile['projects']}
Internship / experience: {profile['experience']}

JOB
Company: {job['company']}
Role: {job['role']}
Job description:
{job['description']}

Return only the finished cover letter.
"""
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Ollama's OpenAI-compatible chat endpoint works with Ollama local and cloud hosts.
    url = f"{host}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You write truthful, tailored job application cover letters."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.65,
        "max_tokens": 650
    }
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    if not response.ok:
        detail = response.text[:1200]
        raise RuntimeError(f"Ollama returned HTTP {response.status_code}: {detail}")
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Unexpected response from Ollama: {str(data)[:1000]}")

def word_count(text):
    return len(re.findall(r"\b[\w’'-]+\b", text))

with st.form("cover_letter_form"):
    st.subheader("1. Your details")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Full name *", placeholder="e.g. Mokshith Nani")
        degree = st.text_input("Degree / education *", placeholder="e.g. B.Tech in Computer Science")
    with c2:
        skills = st.text_area("Skills *", placeholder="Python, SQL, Streamlit, communication...", height=105)
        experience = st.text_area("Internship / work experience", placeholder="Role, organization, responsibilities, results (if any)...", height=105)
    projects = st.text_area("Projects", placeholder="Project name, what you built, technologies used, your contribution...", height=110)

    st.divider()
    st.subheader("2. Job details")
    c3, c4 = st.columns(2)
    with c3:
        company = st.text_input("Company name *", placeholder="e.g. Acme Technologies")
    with c4:
        role = st.text_input("Job role *", placeholder="e.g. Python Developer Intern")
    description = st.text_area("Job description *", placeholder="Paste the job responsibilities, required skills and qualifications here...", height=190)

    submitted = st.form_submit_button("✨ Generate cover letter", type="primary", use_container_width=True)

if submitted:
    required = {
        "Full name": name, "Degree / education": degree, "Skills": skills,
        "Company name": company, "Job role": role, "Job description": description
    }
    missing = [label for label, value in required.items() if not value.strip()]
    if missing:
        st.error("Please complete the required fields: " + ", ".join(missing))
    else:
        host, model, api_key = get_config()
        profile = {"name": name.strip(), "degree": degree.strip(), "skills": skills.strip(),
                   "projects": projects.strip() or "Not provided",
                   "experience": experience.strip() or "Not provided"}
        job = {"company": company.strip(), "role": role.strip(), "description": description.strip()}
        with st.spinner(f"Generating your cover letter with {model}..."):
            try:
                letter = generate_cover_letter(profile, job, host, model, api_key)
                # Enforce the requested limit even if the model exceeds it.
                if word_count(letter) > 300:
                    trim_prompt = (
                        "Edit the following cover letter to no more than 280 words. Preserve all factual "
                        "details and do not add anything. Return only the edited letter:\n\n" + letter
                    )
                    headers = {"Content-Type": "application/json"}
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"
                    r = requests.post(
                        f"{host}/v1/chat/completions", headers=headers,
                        json={"model": model, "messages":[{"role":"user","content":trim_prompt}],
                              "temperature":0.2,"max_tokens":550}, timeout=180
                    )
                    r.raise_for_status()
                    letter = r.json()["choices"][0]["message"]["content"].strip()
                if word_count(letter) > 300:
                    st.warning("The model returned more than 300 words after shortening. Please regenerate or edit the text before sending.")
                st.session_state["generated_letter"] = letter
                st.session_state["letter_company"] = company.strip()
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Ollama. Check OLLAMA_HOST and confirm the Ollama service is running and reachable.")
            except requests.exceptions.Timeout:
                st.error("Ollama took too long to respond. Try again, or use a faster/smaller model.")
            except Exception as e:
                st.error(f"Generation failed: {e}")

if st.session_state.get("generated_letter"):
    st.divider()
    st.subheader("3. Your cover letter")
    letter = st.session_state["generated_letter"]
    st.caption(f"{word_count(letter)} words · Review names and facts before sending.")
    edited = st.text_area("Edit your cover letter if needed", value=letter, height=360, key="letter_editor")
    st.download_button(
        "⬇️ Download as .txt",
        data=edited.encode("utf-8"),
        file_name=f"cover_letter_{re.sub(r'[^a-zA-Z0-9_-]+', '_', st.session_state.get('letter_company','company')).strip('_')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.info("Tip: Check the spelling of the company and role, and make sure every claim accurately reflects your experience.")

with st.expander("Connection help"):
    st.markdown("""
    - **Local:** Start Ollama on the same computer as Streamlit, pull the model, then run `streamlit run app.py`.
    - **Streamlit Community Cloud:** It cannot access `localhost` on your own computer. Set `OLLAMA_HOST` to a reachable Ollama Cloud or remotely hosted Ollama endpoint in Secrets.
    - Never paste API keys into `app.py` or commit them to GitHub.
    """)
