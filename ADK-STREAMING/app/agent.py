import os
import json
import logging
from dotenv import load_dotenv
from google.genai import types, Client
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.tool_context import ToolContext

load_dotenv()

logger = logging.getLogger(__name__)


async def analyze_screenshot(tool_context: ToolContext) -> dict:
    """
    Analyzes the most recently uploaded screenshot of the user's browser or screen.
    Uses Gemini multimodal vision to interpret visible UI elements and page content.
    The user must first attach a screenshot (.png/.jpg) in the chat.
    """
    screenshot_part = None
    for name in ["screenshot.png", "screenshot.jpg", "screenshot.jpeg", "screen.png"]:
        screenshot_part = await tool_context.load_artifact(name)
        if screenshot_part is not None:
            break

    if screenshot_part is None:
        try:
            artifact_names = await tool_context.list_artifacts()
            image_artifacts = [
                n for n in artifact_names
                if n.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            ]
            if image_artifacts:
                screenshot_part = await tool_context.load_artifact(image_artifacts[-1])
        except Exception as e:
            logger.warning(f"Could not list artifacts: {e}")

    if screenshot_part is None:
        return {
            "error": (
                "No screenshot found. Please attach a screenshot of your browser "
                "or screen in the chat before asking me to analyze it."
            ),
            "page_summary": "",
            "ui_elements": [],
            "suggested_actions": [],
        }

    client = Client(api_key=os.environ["GEMINI_API_KEY"])

    analysis_prompt = """You are analyzing a browser or desktop screenshot.

Respond ONLY with a valid JSON object in this exact format (no markdown, no code fences):
{
  "page_type": "search_results | article | form | dashboard | homepage | other",
  "page_title": "visible heading or browser tab title",
  "page_summary": "2-3 sentence summary of what is visible",
  "current_url_visible": "URL shown in address bar, or null if not visible",
  "main_content": "the primary text content visible on screen",
  "ui_elements": [
    {"type": "button|link|input|text|image|nav|menu", "label": "visible label", "location": "top|center|bottom|left|right"}
  ],
  "suggested_actions": [
    "Specific action the user could take based on what is visible"
  ]
}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    screenshot_part,
                    types.Part.from_text(analysis_prompt),
                ],
            )
        ],
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1])

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {
            "page_summary": raw_text,
            "ui_elements": [],
            "suggested_actions": [],
            "note": "Raw vision response (could not parse as JSON)",
        }


root_agent = Agent(
    name="voice_ui_navigator",
    model="gemini-2.0-flash-live-001",
    description=(
        "A voice-powered research assistant that sees your browser screen, "
        "interprets the UI using Gemini vision, performs Google searches, "
        "and speaks results back to you in real time."
    ),
    instruction="""You are a Voice UI Navigator — a hands-free research assistant
that can see the user's screen and search the web.

## Your Capabilities
1. **Screen Analysis**: When the user shares a screenshot, call `analyze_screenshot`
   to understand what is visible. Describe what you see before taking action.
2. **Web Research**: Use `google_search` to find information on any topic.
3. **Navigation Planning**: Based on what you see and what the user wants,
   suggest clear step-by-step actions they can take.

## How to Respond
- Always speak naturally — you are having a voice conversation.
- When analyzing a screenshot: describe the page type, key content, and
  what actions are available to the user.
- When searching: summarize the key findings concisely.
- Suggest specific next steps the user can take.
- Keep responses under 3-4 sentences unless detail is requested.

## Important Rules
- NEVER attempt to access the DOM, JavaScript, or any browser APIs.
- You interpret screens visually only, exactly as a human would.
- If no screenshot has been shared, politely ask the user to attach one.
- If you cannot find information via search, say so honestly.
""",
    tools=[
        analyze_screenshot,
        google_search,
    ],
    generate_content_config=types.GenerateContentConfig(
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Puck"
                )
            )
        )
    ),
)
