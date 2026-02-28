"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

# Load .env from project root (parent of backend directory)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dotenv_path = os.path.join(_project_root, '.env')
load_dotenv(_dotenv_path)

# Ollama API key (use OLLAMA_API_KEY for cloud, OLLAMA_TOKEN for local)
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", os.getenv("OLLAMA_TOKEN", ""))
OLLAMA_TOKEN = OLLAMA_API_KEY

# Council members - list of model identifiers (comma-separated in .env)
_default_models = os.getenv(
    "COUNCIL_MODELS",
    "openai/gpt-5.1,google/gemini-3-pro-preview,anthropic/claude-sonnet-4.5"
)
COUNCIL_MODELS = [m.strip() for m in _default_models.split(",") if m.strip()]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", "google/gemini-3-pro-preview")

# Ollama API endpoint (OpenAI-compatible)
# Local: http://localhost:11434/v1/chat/completions
# Cloud: https://ollama.com/v1/chat/completions
OLLAMA_API_URL = "https://ollama.com/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
