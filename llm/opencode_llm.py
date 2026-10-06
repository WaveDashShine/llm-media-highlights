import os

from openai import OpenAI

from configs import INPUT_DIRECTORY, OPENCODE_API_KEY, SupportedLlm
from llm.abstractllm import AbstractLlm
from llm.prompts import GET_HIGHLIGHTS_PROMPT
from output_log import logger

GO_BASE_URL = "https://opencode.ai/zen/go/v1"
# Go requires a stable session id per conversation for routing/prompt caching:
# https://opencode.ai/docs/go/#where-can-i-use-it
SESSION_ID = "whisper-srt-opencode-llm"


class GlmFlash(AbstractLlm):

    def get_highlights(self, file_path: str) -> str:
        client = OpenAI(
            base_url=GO_BASE_URL,
            api_key=OPENCODE_API_KEY,
            default_headers={"x-opencode-session": SESSION_ID},
        )
        with open(file_path, "r", encoding="utf-8") as subtitle_file:
            subtitle_text = subtitle_file.read()
        logger.info(f"{GET_HIGHLIGHTS_PROMPT}")
        stream = client.chat.completions.create(
            model=SupportedLlm.GLM_5_3_FLASH,
            max_tokens=40960,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": f"{subtitle_text}\n\n{GET_HIGHLIGHTS_PROMPT}",
                },
            ],
        )
        parts: list[str] = []
        for event in stream:
            if not event.choices:
                continue  # final usage-only chunk has no choices
            content = event.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                parts.append(content)
        print()  # newline after the streamed output
        response_text = "".join(parts)
        logger.info(f"RESPONSE:\n{response_text}")
        return response_text


if __name__ == "__main__":
    FILENAME = "test_long_video.srt"  # change to test .srt
    glm = GlmFlash()
    input_file = str(os.path.join(INPUT_DIRECTORY, FILENAME))
    glm.get_highlights(file_path=input_file)
