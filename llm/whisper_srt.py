import argparse
import os
from datetime import datetime

import torch
import whisper
from whisper.utils import get_writer

from configs import INPUT_DIRECTORY, OUTPUT_DIRECTORY, PROJECT_DIRECTORY, SrtFormat
from output_log import logger

# if you need more fine grain control on the result segments https://github.com/openai/whisper/discussions/911

SUPPORTED_FILE_TYPE = ["m4a", "mp3", "webm", "mp4", "mpga", "wav", "mpeg"]

# captions for short form video (youtube shorts, instagram reels)
SHORT_FORM_OPTIONS = {
    "max_line_count": 2,
    "max_words_per_line": 1,  # cannot be used with max_line_width
    # "max_line_width": 15,
    "highlight_words": False,
}

# captions for long form video (youtube videos, TV)
LONG_FORM_OPTIONS = {
    "max_line_count": 2,
    # "max_words_per_line": 10,  # cannot be used with max_line_width
    "max_line_width": 42,
}


def is_supported(file_path: str) -> bool:
    for file_type in SUPPORTED_FILE_TYPE:
        if file_path.lower().endswith(file_type):
            return True
    return False


def generate_srt(file_path: str, srt_format: SrtFormat = SrtFormat.SHORT) -> str:
    """
    :param file_path: file path with extension, relative to the input/
        directory (e.g. "input/Recording.m4a" or "input/subdir/Recording.m4a").
        Supported extensions: m4a, mp3, webm, mp4, mpga, wav, mpeg.
    :param srt_format: short form (shorts/reels) or long form (youtube/TV)
        subtitle configuration
    :return: file path of the generated .srt, mirrored from the input/
        structure into the output/ directory (e.g. output/subdir/Recording.m4a.srt)
    """
    if not is_supported(file_path=file_path):
        raise RuntimeError(f"file type is not supported by whisper {file_path}")

    match srt_format:
        case SrtFormat.SHORT:
            writer_options = SHORT_FORM_OPTIONS
        case SrtFormat.LONG:
            writer_options = LONG_FORM_OPTIONS
        case _:
            raise RuntimeError(f"srt format is unsupported {srt_format}")

    start_time = datetime.now()
    logger.info(f"Start Time: {start_time}")

    torch.cuda.init()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"{device} device")
    model = whisper.load_model("turbo").to(device=device)
    audio = whisper.load_audio(file=file_path)
    result = model.transcribe(
        audio=audio,
        fp16=False,
        word_timestamps=True,
        task="transcribe",
        no_speech_threshold=0.1,
    )
    logger.info(result["text"])
    rel_path = os.path.relpath(file_path, INPUT_DIRECTORY)
    nested_output_dir = os.path.join(OUTPUT_DIRECTORY, os.path.dirname(rel_path))
    os.makedirs(nested_output_dir, exist_ok=True)
    srt_filepath = os.path.join(nested_output_dir, f"{os.path.basename(rel_path)}.srt")
    logger.info(f"writing to {srt_filepath}")
    writer = get_writer(output_format="srt", output_dir=nested_output_dir)

    writer(result, srt_filepath, writer_options)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    elapsed_sec = elapsed_time.total_seconds()
    elapsed_min = elapsed_sec / 60
    logger.info(f"End Time: {end_time}")
    logger.info(f"Time taken: {elapsed_sec} sec or {elapsed_min} min")
    return srt_filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Whisper SRT",
        description="Transcribes a media file into an .srt subtitle file",
    )
    parser.add_argument(
        "--file",
        type=str,
        help='file path relative to root directory, with extension; nested subdirectories supported (e.g. "Recording.m4a" or "subdir/Recording.m4a")',
    )
    parser.add_argument(
        "--srt-format",
        type=str,
        required=False,
        default=SrtFormat.SHORT,
        choices=[SrtFormat.SHORT, SrtFormat.LONG],
        help="subtitle configuration for short form (shorts/reels) or long form (youtube/TV) video",
    )
    args = parser.parse_args()
    generate_srt(
        file_path=str(os.path.join(PROJECT_DIRECTORY, args.file)),
        srt_format=args.srt_format,
    )
