# Voice UI Navigator — Gemini Live Agent Challenge

A voice-powered AI agent that **sees your screen**, **searches the web in real time**, and **speaks results back to you** — all without touching the DOM.

Built for the **UI Navigator** category of the [Gemini Live Agent Challenge](https://googleai.devpost.com/).

---

## Demo

> Upload a screenshot of any browser page, speak your question, and the agent analyzes what it sees, searches Google, and responds with voice.

**Live Deployment:** https://voice-navigator-913580598688.us-central1.run.app

---

## What It Does

| Feature | Description |
|---|---|
| Screen Vision | Uploads a screenshot → Gemini analyzes visible UI elements, page content, and layout |
| Voice Input/Output | Speak your queries via microphone; agent responds in natural audio |
| Web Research | Real-time Google Search grounding for up-to-date answers |
| Navigation Planning | Suggests step-by-step actions based on what is visible on screen |
| No DOM Access | Pure visual understanding — works on any app, not just the web |

---

## Architecture

```
User (Browser)
      |
      |  1. Attach screenshot PNG
      |  2. Speak or type a query
      v
ADK Web UI  ──────────────────────────────────────────────────────────
      |                                                               |
      v                                                               |
root_agent [gemini-2.0-flash-live-001]                               |
      |                                                               |
      +── analyze_screenshot()                                        |
      |       Reads uploaded image artifact                           |
      |       Sends to Gemini 2.0 Flash (vision)                     |
      |       Returns: page_summary, ui_elements, suggested_actions   |
      |                                                               |
      +── google_search()                                             |
              ADK built-in tool                                       |
              Real-time Google Search grounding                       |
              Returns: web search results                             |
      |
      v
Voice Response (Gemini Live API audio)
Text Response  (chat display)

─────────────────────────────────────────────
Google Cloud Services:
  - Gemini API (gemini-2.0-flash-live-001)
  - Cloud Run (hosting)
  - Artifact Registry (Docker image storage)
  - Cloud Build (CI/CD)
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent Framework | Google ADK (Agent Development Kit) v1.25.1 |
| Live Voice Model | `gemini-2.0-flash-live-001` (Gemini Live API) |
| Vision Model | `gemini-2.0-flash` (multimodal screenshot analysis) |
| Search | ADK `google_search` tool |
| Backend | Python 3.11 + FastAPI (via ADK) |
| Hosting | Google Cloud Run |
| Container Registry | Google Artifact Registry |

---

## Project Structure

```
GEMINI LIVE AGENT CHALLENGE/
├── ADK-STREAMING/               # Main hackathon project
│   ├── app/
│   │   ├── __init__.py          # Package entry point
│   │   ├── agent.py             # Root agent + analyze_screenshot tool
│   │   └── .env                 # API keys (not committed)
│   ├── Dockerfile               # Cloud Run container
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Project docs
├── google_search_agent/         # Prototype / baseline agent
│   ├── __init__.py
│   ├── agent.py
│   └── .env                     # API keys (not committed)
└── .gitignore
```

---

## Local Setup

### Prerequisites
- Python 3.10 or higher
- A [Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone the repository
```bash
git clone https://github.com/Kamaumbugua-dev/GEMINI_CODING_CHALLENGE.git
cd "GEMINI_CODING_CHALLENGE"
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
cd ADK-STREAMING
pip install -r requirements.txt
```

### 4. Configure environment variables
Create `ADK-STREAMING/app/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=False
```

Get your API key at: https://aistudio.google.com/apikey

### 5. Run locally
```bash
# From inside ADK-STREAMING/
adk web . --no-reload
```

Open http://localhost:8000 in your browser.

---

## How to Use

1. Open the app (local or deployed URL)
2. Select the **`voice_ui_navigator`** agent
3. **Attach a screenshot** of any browser page using the file upload button
4. **Type or speak** your question (e.g. *"What do you see on my screen?"* or *"Search for more about this topic"*)
5. The agent will:
   - Analyze the screenshot with Gemini vision
   - Search Google if needed
   - Respond with voice and text

**Voice mode:** Click the microphone button in the ADK UI for real-time audio conversation.

---

## Cloud Run Deployment

### Prerequisites
- [Google Cloud SDK](https://cloud.google.com/sdk) installed and authenticated
- GCP project with Cloud Run, Cloud Build, and Artifact Registry enabled

### Enable required APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com
```

### Create Artifact Registry repository
```bash
gcloud artifacts repositories create voice-navigator-repo \
  --repository-format=docker \
  --location=us-central1
```

### Build and push Docker image
```bash
cd ADK-STREAMING

gcloud builds submit \
  --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voice-navigator-repo/voice-navigator
```

### Deploy to Cloud Run
```bash
gcloud run deploy voice-navigator \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/voice-navigator-repo/voice-navigator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars "GEMINI_API_KEY=your_key_here,GOOGLE_GENAI_USE_VERTEXAI=False"
```

---

## Hackathon Category

**UI Navigator** — The agent observes the user's screen visually (via screenshot), interprets UI elements using Gemini multimodal vision without any DOM access, and outputs actionable navigation steps and spoken responses.

**Mandatory Tech Used:**
- Gemini multimodal vision to interpret screenshots
- Gemini Live API for real-time voice interaction
- Google ADK (Agent Development Kit)
- Google Cloud Run for hosting

---

## Key Design Decisions

- **No DOM access** — The agent reads screens exactly as a human would, making it work across any application (browser, desktop, mobile screenshots)
- **Gemini Live API** — Enables natural voice conversations with interruption support via ADK's `/run_live` WebSocket endpoint
- **Separate vision call** — Screenshot analysis uses `gemini-2.0-flash` synchronously inside a tool, keeping the live audio session lightweight
- **ADK artifact system** — Screenshots uploaded in the chat are stored as session artifacts and retrieved by the tool via `tool_context.load_artifact()`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Your Gemini API key from Google AI Studio |
| `GOOGLE_GENAI_USE_VERTEXAI` | No | Set to `True` to use Vertex AI backend instead |
| `GOOGLE_CLOUD_PROJECT` | Only for Vertex AI | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Only for Vertex AI | GCP region (e.g. `us-central1`) |

---

## License

MIT License — feel free to use, modify, and build on this project.
