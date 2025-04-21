import os
from dotenv import load_dotenv
from enum import StrEnum

# directories
PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
INPUT_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "input/")
OUTPUT_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "output/")

# environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class SupportedLlm(StrEnum):
    GEMINI_FLASH = "gemini-2.0-flash"
