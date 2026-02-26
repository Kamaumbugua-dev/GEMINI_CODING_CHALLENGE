# Voice UI Navigator — Gemini Live Agent Challenge

A voice-powered research assistant that **sees your screen** and **searches the web** using Google's Gemini multimodal AI.

Built for the **UI Navigator** category of the Gemini Live Agent Challenge.

---

## What It Does

1. **You upload a screenshot** of your browser or any screen
2. **You speak (or type) a question** about what you see or want to find
3. **The agent analyzes the screenshot** using Gemini vision — no DOM access, pure visual understanding
4. **The agent searches Google** if research is needed
5. **The agent speaks back** a summary and suggested next steps

---

## Architecture

```
User (browser)
   |  upload screenshot + voice query
   v
ADK Web UI (localhost:8000 / Cloud Run)
   |
   v
root_agent  [gemini-2.0-flash-live-001]
   |
   +-- analyze_screenshot()  →  Gemini 2.0 Flash (vision)
   |        reads uploaded screenshot artifact
   |        returns: page_summary, ui_elements, suggested_actions
   |
   +-- google_search()       →  Gemini grounding / Google Search API
            returns: real-time web results

Response: spoken audio via Gemini Live API
```

**Google Cloud Services Used:**
- Gemini API (gemini-2.0-flash-live-001, gemini-2.0-flash)
- Cloud Run (hosting)

---

## Local Setup

### Prerequisites
- Python 3.10+
- A [Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd "GEMINI LIVE AGENT CHALLENGE/ADK-STREAMING"
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your API key
Edit `app/.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_key_here
GOOGLE_GENAI_USE_VERTEXAI=False
```

### 5. Run locally
```bash
adk web app --no-reload
```
Open [http://localhost:8000](http://localhost:8000)

---

## How to Use

1. Open the ADK web UI at `http://localhost:8000`
2. Select the `voice_ui_navigator` agent
3. **Attach a screenshot** using the file attachment button (any PNG/JPG of your browser)
4. Type or speak: *"What do you see on my screen?"* or *"Search for more info about this topic"*
5. Click the **microphone button** for voice mode — the agent will respond with audio

---

## Cloud Run Deployment

### Prerequisites
- [Google Cloud SDK](https://cloud.google.com/sdk) installed
- A GCP project with Cloud Run and Artifact Registry enabled

```bash
export PROJECT_ID=your-gcp-project-id
export REGION=us-central1

# Build and push the Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/voice-navigator .

# Deploy to Cloud Run
gcloud run deploy voice-navigator \
  --image gcr.io/$PROJECT_ID/voice-navigator \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --set-env-vars "GEMINI_API_KEY=your_key_here,GOOGLE_GENAI_USE_VERTEXAI=False"
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | Google ADK (Agent Development Kit) v1.25.1 |
| AI Model | Gemini 2.0 Flash Live (voice) + Gemini 2.0 Flash (vision) |
| Voice | Gemini Live API via ADK `/run_live` WebSocket |
| Search | ADK `google_search` tool |
| Hosting | Google Cloud Run |
| Language | Python 3.11 |
