import os

from moviepy import VideoFileClip

from output_log import logger

MEDIA_FORMATS = ["mov"]


def is_convertible_media_format(file_path: str) -> bool:
    for file_type in MEDIA_FORMATS:
        if file_path.lower().endswith(file_type):
            return True
    return False


def convert_media_to_mp3(file_path: str) -> str:
    """
    :param file_path: file path with .mov extension, relative to the input/
        directory (e.g. "input/Recording.mov" or "input/subdir/Recording.mov")
    :return: file path of converted .mp3 audio clip, written into the same
        directory structure as the input file (under input/)
    """
    if not is_convertible_media_format(file_path=file_path):
        raise RuntimeError(f"file type is not supported by media converter {file_path}")

    file_name = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name)
    audio_filepath = os.path.join(os.path.dirname(file_path), f"{file_name}.mp3")

    logger.info(f"converting {file_path} to {audio_filepath}")
    video_clip = VideoFileClip(file_path)
    video_clip.audio.write_audiofile(audio_filepath)
    video_clip.close()

    return audio_filepath
