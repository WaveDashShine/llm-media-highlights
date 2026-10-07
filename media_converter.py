import os

from moviepy import VideoFileClip

from configs import INPUT_DIRECTORY
from output_log import logger

MEDIA_FORMATS = ["mov"]


def is_convertible_media_format(file_path: str) -> bool:
    for file_type in MEDIA_FORMATS:
        if file_path.lower().endswith(file_type):
            return True
    return False


def convert_media_to_mp3(file_path: str) -> str:
    """
    :param file_path: file name with extension of .mov file in input/ directory
    :return: file path of converted audio clip in input/ directory
    """
    if not is_convertible_media_format(file_path=file_path):
        raise RuntimeError(f"file type is not supported by media converter {file_path}")

    file_name, _ = os.path.splitext(os.path.basename(file_path))
    audio_filepath = os.path.join(INPUT_DIRECTORY, f"{file_name}.mp3")

    logger.info(f"converting {file_path} to {audio_filepath}")
    video_clip = VideoFileClip(file_path)
    video_clip.audio.write_audiofile(audio_filepath)
    video_clip.close()

    return audio_filepath
