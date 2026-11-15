# AI Cover Letter Generator — Streamlit + Ollama

A Streamlit app that creates a tailored cover letter under 300 words and lets the user download it as a `.txt` file.

## 1. Requirements

- Python 3.10+
- Ollama running locally, OR a reachable Ollama Cloud / remote Ollama endpoint
- Access to the `gemma4` model name configured for your Ollama account/host

> Important: Streamlit Community Cloud does not run your local Ollama server and cannot reach `localhost` on your computer. For a cloud deployment, configure a publicly reachable Ollama endpoint and its API key. Do not expose an unauthenticated Ollama server to the public internet.

## 2. Run locally

```bash
# 1) Install Ollama from https://ollama.com
# 2) Pull the model (if this model is available to your Ollama installation)
ollama pull gemma4

# 3) Create and activate a virtual environment (optional but recommended)
python -m venv .venv

# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

# macOS / Linux:
source .venv/bin/activate

# 4) Install Python dependencies
pip install -r requirements.txt

# 5) Run the app
streamlit run app.py
```

By default the app connects to `http://localhost:11434`. If your Ollama server uses another address, set `OLLAMA_HOST`.

### Local secrets

Create `.streamlit/secrets.toml` (copy `.streamlit/secrets.toml.example`) and set:

```toml
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma4"
OLLAMA_API_KEY = ""
```

For local Ollama, an API key is normally not required.

## 3. Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Open https://share.streamlit.io/ and deploy the repository. Set the main file path to `app.py`.
3. In your deployed app, open **Settings → Secrets**.
4. Paste the following TOML, replacing the placeholder with a valid key and setting the correct endpoint/model for your Ollama hosting setup:

```toml
OLLAMA_HOST = "https://ollama.com"
OLLAMA_MODEL = "gemma4"
OLLAMA_API_KEY = "YOUR_OLLAMA_API_KEY"
```

5. Save secrets and reboot/restart the app.

**Do not use `http://localhost:11434` in Streamlit Cloud** unless Ollama is running inside the same deployed environment (this project does not install or start Ollama there). The host must be reachable from Streamlit Cloud. Confirm the model identifier and authentication format in your Ollama provider account/docs. If your provider gives a different API base URL, use that URL as `OLLAMA_HOST`; this app appends `/v1/chat/completions`.

## 4. Streamlit secrets: what exactly to paste

For an Ollama-hosted endpoint that accepts Ollama's OpenAI-compatible API and bearer-key authentication:

```toml
OLLAMA_HOST = "https://ollama.com"
OLLAMA_MODEL = "gemma4"
OLLAMA_API_KEY = "paste_your_real_ollama_api_key_here"
```

The above is a configuration template, not a working key. Create/get the API key from your Ollama account. If using local Ollama instead, use:

```toml
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma4"
OLLAMA_API_KEY = ""
```

That local configuration is for running Streamlit locally, not Streamlit Cloud.

## 5. Features

- Candidate profile: name, degree, skills, projects, internship/experience
- Job details: company, role, job description
- Prompt rules to avoid invented credentials and achievements
- 300-word target with a second shortening pass if needed
- Editable generated result
- Download as plain-text `.txt`

## Troubleshooting

- **Connection refused / connection error:** endpoint is unreachable or Ollama is not running.
- **401 / 403:** API key or authentication is incorrect.
- **404:** check the endpoint path and whether the provider supports `/v1/chat/completions`.
- **Model not found:** verify the exact model identifier available to your Ollama host/account. Model names and availability can vary; use the exact identifier shown by the provider.
- **Timeout:** try again or use a faster model / hosted instance with sufficient capacity.

Never commit `.streamlit/secrets.toml` or API keys to GitHub.
