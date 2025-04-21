import whisper
import os
import torch
from datetime import datetime
from whisper.utils import get_writer
from configs import INPUT_DIRECTORY, OUTPUT_DIRECTORY
from output_log import logger


# TODO: if you need more fine grain control on the result segments
#  https://github.com/openai/whisper/discussions/911

SUPPORTED_FILE_TYPE = ["m4a", "mp3", "webm", "mp4", "mpga", "wav", "mpeg"]


def is_supported(file_path: str) -> bool:
    for file_type in SUPPORTED_FILE_TYPE:
        if file_path.lower().endswith(file_type):
            return True
    return False


def generate_srt(file_path: str) -> str:
    """
    :param file_path: file name with extension of file in input/ directory
    :return: file path of
    """
    if not is_supported(file_path=file_path):
        raise RuntimeError(f"file type is not supported by whisper {file_path}")

    start_time = datetime.now()
    logger.info(f"Start Time: {start_time}")

    torch.cuda.init()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"{device} device")
    model = whisper.load_model("turbo").to(device=device)
    audio = whisper.load_audio(file=file_path)
    trimmed_audio = whisper.pad_or_trim(audio)
    result = model.transcribe(
        audio=trimmed_audio, fp16=False, word_timestamps=True, task="transcribe"
    )
    logger.info(result["text"])
    file_name = os.path.basename(file_path)
    srt_filepath = os.path.join(OUTPUT_DIRECTORY, f"{file_name}.srt")
    logger.info(f"writing to {srt_filepath}")
    writer = get_writer(output_format="srt", output_dir=OUTPUT_DIRECTORY)

    writer_options = {  # TODO: handle from argparse
        "max_line_count": 100,
        "max_words_per_line": 10,
        "max_line_width": 47,
    }
    writer(result, srt_filepath, writer_options)

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    elapsed_sec = elapsed_time.total_seconds()
    elapsed_min = elapsed_sec / 60
    logger.info(f"End Time: {end_time}")
    logger.info(f"Time taken: {elapsed_sec} sec or {elapsed_min} min")
    return srt_filepath


if __name__ == "__main__":
    FILENAME = "Recording.m4a"  # change to media file
    input_file = str(os.path.join(INPUT_DIRECTORY, FILENAME))
    generate_srt(file_path=input_file)
