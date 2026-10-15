import argparse
import os

from openai import OpenAI

from configs import OPENCODE_API_KEY, PROJECT_DIRECTORY, SupportedLlm
from llm.abstractllm import AbstractLlm
from llm.prompts import PromptType, get_prompt
from output_log import logger

GO_BASE_URL = "https://opencode.ai/zen/go/v1"
# Go requires a stable session id per conversation for routing/prompt caching:
# https://opencode.ai/docs/go/#where-can-i-use-it
SESSION_ID = "whisper-srt-opencode-llm"
DEFAULT_MODEL = SupportedLlm.GLM_5_3_FLASH


def write_highlights_file(file_path: str, highlight_txt: str) -> str:
    """
    Writes highlights next to file_path with .txt extension.
    Returns the .txt file path.
    Kept for backwards compatibility with main.py's highlights flow.
    """
    file_name, _ = os.path.splitext(file_path)
    txt_filepath = f"{file_name}.txt"
    os.makedirs(os.path.dirname(txt_filepath), exist_ok=True)
    logger.info(f"writing to {txt_filepath}")
    with open(txt_filepath, "w", encoding="utf-8") as highlights_file:
        highlights_file.write(highlight_txt)
    return txt_filepath


def write_prompt_output_file(file_path: str, prompt_type: PromptType, result_text: str) -> str:
    """
    Writes the result of running prompt_type next to file_path as
    <original_name>.<prompt_type>.txt. Returns the .txt file path.
    """
    file_name, _ = os.path.splitext(file_path)
    txt_filepath = f"{file_name}.{prompt_type.value}.txt"
    os.makedirs(os.path.dirname(txt_filepath), exist_ok=True)
    logger.info(f"writing to {txt_filepath}")
    with open(txt_filepath, "w", encoding="utf-8") as result_file:
        result_file.write(result_text)
    return txt_filepath


class GlmFlash(AbstractLlm):

    def __init__(self, model: SupportedLlm = DEFAULT_MODEL):
        self.model = model

    def generate(self, file_path: str, prompt_type: PromptType) -> str:
        """
        :param file_path: path to a .srt (or plain text) subtitle file,
            e.g. "input/test_long_video.srt" or "input/subdir/test_long_video.srt"
        :param prompt_type: which prompt from llm/prompts.py to run
        :return: the LLM response text for the requested prompt
        """
        client = OpenAI(
            base_url=GO_BASE_URL,
            api_key=OPENCODE_API_KEY,
            default_headers={"x-opencode-session": SESSION_ID},
        )
        with open(file_path, "r", encoding="utf-8") as subtitle_file:
            subtitle_text = subtitle_file.read()
        prompt_text = get_prompt(prompt_type)
        logger.info(f"prompt_type: {prompt_type}")
        logger.info(f"{prompt_text}")
        stream = client.chat.completions.create(
            model=self.model,
            max_tokens=131072,
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": f"{subtitle_text}\n\n{prompt_text}",
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
        prog="GLM Prompt Runner",
        description="Runs a prompt from llm/prompts.py over a subtitle file using GLM",
    )
    parser.add_argument(
        "--file",
        type=str,
        help='file path relative to root directory, with .srt extension; nested subdirectories supported (e.g. "test_long_video.srt" or "subdir/test_long_video.srt")',
    )
    parser.add_argument(
        "--prompt",
        type=PromptType,
        required=False,
        default=PromptType.HIGHLIGHTS,
        choices=list(PromptType),
        help="which prompt from llm/prompts.py to run",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        required=False,
        default=False,
        help="run every registered prompt instead of just one",
    )
    args = parser.parse_args()
    input_file = str(os.path.join(PROJECT_DIRECTORY, args.file))
    glm = GlmFlash()
    prompt_types = list(PromptType) if args.all else [args.prompt]
    for prompt_type in prompt_types:
        result_text = glm.generate(file_path=input_file, prompt_type=prompt_type)
        write_prompt_output_file(file_path=input_file, prompt_type=prompt_type, result_text=result_text)
