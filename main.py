import os
import argparse
from configs import INPUT_DIRECTORY, SupportedLlm
from llm.whisper_srt import generate_srt
from llm.gemini_2 import GeminiFlash
from output_log import logger

TEXT_FORMATS = ["txt", "srt"]


def is_text(file_path: str) -> bool:
    for file_type in TEXT_FORMATS:
        if file_path.lower().endswith(file_type):
            return True
    return False


def get_model(llm: SupportedLlm):
    """
    Update newly supported LLMs here
    """
    match llm:
        case SupportedLlm.GEMINI_FLASH:
            return GeminiFlash
        case _:
            raise NotImplemented("LLM Model is unsupported")


def generate_highlights(file_path: str, llm: SupportedLlm = SupportedLlm.GEMINI_FLASH):
    if not is_text(file_path=file_path):
        text_filepath = generate_srt(file_path=file_path)
    else:
        text_filepath = file_path
    logger.info(text_filepath)
    llm_model_class = get_model(llm=llm)
    llm_model = llm_model_class()
    result_text: str = llm_model.get_highlights(file_path=text_filepath)
    # TODO: clean the result text ?


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Media Highlighter",
        description="Finds highlights in media files or text",
        epilog="TODO: fill out bottom of /help command",
    )
    parser.add_argument("--file", type=str, required=True, help="file name")
    parser.add_argument(
        "--llm",
        type=str,
        required=False,
        default=SupportedLlm.GEMINI_FLASH,  # TODO: change if key exppires
        choices=[SupportedLlm.GEMINI_FLASH],
        help="LLM for parsing the subtitle files",
    )
    # TODO: whisper has writer_options for subtitles, add to parse
    args = parser.parse_args()
    # TODO: might be easier to keep track of the directories if we pass in a file object isntead
    input_file = str(os.path.join(INPUT_DIRECTORY, args.file))
    generate_highlights(file_path=input_file, llm=args.llm)
    # TODO: pass the number of highlights to find through args
