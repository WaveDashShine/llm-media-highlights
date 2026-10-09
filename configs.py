import os
from enum import StrEnum

from dotenv import load_dotenv

# directories
PROJECT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
INPUT_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "input/")
OUTPUT_DIRECTORY = os.path.join(PROJECT_DIRECTORY, "output/")

# environment variables
load_dotenv()
OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")


class SupportedLlm(StrEnum):
    GLM_5_3_FLASH = "glm-5.3-flash"


class SrtFormat(StrEnum):
    SHORT = "short"
    LONG = "long"
