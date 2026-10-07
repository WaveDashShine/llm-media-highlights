import argparse
import os

from openai import OpenAI

from configs import OPENCODE_API_KEY, PROJECT_DIRECTORY, SupportedLlm
from llm.abstractllm import AbstractLlm
from llm.prompts import GET_HIGHLIGHTS_PROMPT
from output_log import logger

GO_BASE_URL = "https://opencode.ai/zen/go/v1"
# Go requires a stable session id per conversation for routing/prompt caching:
# https://opencode.ai/docs/go/#where-can-i-use-it
SESSION_ID = "whisper-srt-opencode-llm"


def write_highlights_file(file_path: str, highlight_txt: str) -> str:
    """
    Writes highlights next to file_path with .txt extension.
    Returns the .txt file path.
    """
    file_name, _ = os.path.splitext(file_path)
    txt_filepath = f"{file_name}.txt"
    os.makedirs(os.path.dirname(txt_filepath), exist_ok=True)
    logger.info(f"writing to {txt_filepath}")
    with open(txt_filepath, "w", encoding="utf-8") as highlights_file:
        highlights_file.write(highlight_txt)
    return txt_filepath


class GlmFlash(AbstractLlm):

    def get_highlights(self, file_path: str) -> str:
        """
        :param file_path: path to a .srt (or plain text) subtitle file,
            e.g. "input/test_long_video.srt" or "input/subdir/test_long_video.srt"
        :return: highlights extracted from the subtitle text
        """
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
    parser = argparse.ArgumentParser(
        prog="GLM Highlights",
        description="Parses highlights from a subtitle file using GLM",
    )
    parser.add_argument(
        "--file",
        type=str,
        help='file path relative to root directory, with .srt extension; nested subdirectories supported (e.g. "test_long_video.srt" or "subdir/test_long_video.srt")',
    )
    args = parser.parse_args()
    input_file = str(os.path.join(PROJECT_DIRECTORY, args.file))
    glm = GlmFlash()
    highlights = glm.get_highlights(file_path=input_file)
    write_highlights_file(file_path=input_file, highlight_txt=highlights)
