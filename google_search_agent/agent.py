import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

load_dotenv()  # Loads GEMINI_API_KEY from .env file

root_agent = Agent(
  # A unique name for the agent.
  name="basic_search_agent",
  # The Large Language Model (LLM) that agent will use.
  # Please fill in the latest model id that supports live from
  # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
  model="gemini-1.5-flash",
  # A short description of the agent's purpose.
  description="Agent to answer questions using Google Search.",
  # Instructions to set the agent's behavior.
  instruction="You are an expert researcher. You always stick to the facts.",
  # Add google_search tool to perform grounding with Google search.
  tools=[google_search]
)

# from google import genai

# client = genai.Client()

# response = client.models.generate_content(
#     model="gemini-3-flash-preview",
#     contents="Explain how AI works in a few words",
# )

# print(response.text)
