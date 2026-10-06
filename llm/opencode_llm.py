import os

from openai import OpenAI

from configs import INPUT_DIRECTORY, OPENCODE_API_KEY, SupportedLlm
from llm.abstractllm import AbstractLlm
from llm.prompts import GET_HIGHLIGHTS_PROMPT
from output_log import logger

# OpenCode Zen serves GLM models through an OpenAI-compatible endpoint:
# https://opencode.ai/zen/v1/chat/completions


class GlmFlash(AbstractLlm):

    def get_highlights(self, file_path: str) -> str:
        client = OpenAI(
            base_url="https://opencode.ai/zen/v1",
            api_key=OPENCODE_API_KEY,
        )
        with open(file_path, "r", encoding="utf-8") as subtitle_file:
            subtitle_text = subtitle_file.read()
        logger.info(f"{GET_HIGHLIGHTS_PROMPT}")
        result = client.chat.completions.create(
            model=SupportedLlm.GLM_5_3_FLASH,
            messages=[
                {
                    "role": "user",
                    "content": f"{subtitle_text}\n\n{GET_HIGHLIGHTS_PROMPT}",
                },
            ],
        )
        response_text = result.choices[0].message.content
        logger.info(f"RESPONSE:\n{response_text}")
        return response_text


if __name__ == "__main__":
    FILENAME = "test_long_video.srt"  # change to test .srt
    glm = GlmFlash()
    input_file = str(os.path.join(INPUT_DIRECTORY, FILENAME))
    glm.get_highlights(file_path=input_file)
