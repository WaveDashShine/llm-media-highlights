import argparse
import os

from configs import PROJECT_DIRECTORY, SupportedLlm
from llm.opencode_llm import GlmFlash
from llm.whisper_srt import generate_srt
from media_converter import convert_media_to_mp3, is_convertible_media_format
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
        case SupportedLlm.GLM_5_3_FLASH:
            return GlmFlash
        case _:
            raise NotImplemented("LLM Model is unsupported")


def write_highlights_file(file_path: str, highlights: str) -> str:
    """
    Writes highlights next to file_path with .txt extension.
    Returns the .txt file path.
    """
    file_name, _ = os.path.splitext(file_path)
    txt_filepath = f"{file_name}.txt"
    os.makedirs(os.path.dirname(txt_filepath), exist_ok=True)
    logger.info(f"writing to {txt_filepath}")
    with open(txt_filepath, "w", encoding="utf-8") as highlights_file:
        highlights_file.write(highlights)
    return txt_filepath


def generate_highlights(file_path: str, llm: SupportedLlm = SupportedLlm.GLM_5_3_FLASH):
    """
    Transcribes non-text media, extracts highlights via LLM,
    and saves them to a .txt next to the transcript.
    Returns the .txt file path.
    """
    if not is_text(file_path=file_path):
        text_filepath = generate_srt(file_path=file_path)
    else:
        text_filepath = file_path
    logger.info(text_filepath)
    llm_model_class = get_model(llm=llm)
    llm_model = llm_model_class()
    result_text: str = llm_model.get_highlights(file_path=text_filepath)
    return write_highlights_file(file_path=text_filepath, highlights=result_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Media Highlighter",
        description="Finds highlights in media files or text",
        epilog="TODO: fill out bottom of /help command",
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help='file path relative to input/ directory; nested subdirectories supported (e.g. "Recording.m4a" or "subdir/Recording.m4a")',
    )
    parser.add_argument(
        "--llm",
        type=str,
        required=False,
        default=SupportedLlm.GLM_5_3_FLASH,
        choices=[SupportedLlm.GLM_5_3_FLASH],
        help="LLM for parsing the subtitle files",
    )
    # TODO: whisper has writer_options for subtitles, add to parse
    args = parser.parse_args()
    input_file = str(os.path.join(PROJECT_DIRECTORY, args.file))
    if is_convertible_media_format(input_file):
        input_file = convert_media_to_mp3(input_file)
    generate_highlights(file_path=input_file, llm=args.llm)
