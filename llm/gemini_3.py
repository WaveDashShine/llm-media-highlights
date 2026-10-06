from google import genai
from configs import GEMINI_API_KEY, SupportedLlm
from llm.prompts import GEMINI_PROMPT
from llm.abstractllm import AbstractLlm
from output_log import logger

# if token consumption is needed, ref:
# https://ai.google.dev/gemini-api/docs/live#token-count


class GeminiFlash(AbstractLlm):

    def get_highlights(self, file_path: str) -> str:
        client = genai.Client(api_key=GEMINI_API_KEY)
        subtitle_file = client.files.upload(file=file_path)
        logger.info(f"{subtitle_file=}")
        logger.info(f"{GEMINI_PROMPT}")
        result = client.models.generate_content(
            model=SupportedLlm.GEMINI_FLASH,
            contents=[
                subtitle_file,
                "\n\n",
                GEMINI_PROMPT,
            ],
        )
        logger.info(f"RESPONSE:\n{result.text}")
        # delete file on the client
        client.files.delete(name=subtitle_file.name)
        return result.text


if __name__ == "__main__":
    FILENAME = "test_long_video.srt"  # change to test .srt
    gemini = GeminiFlash()
    gemini.get_highlights(file_path=FILENAME)
