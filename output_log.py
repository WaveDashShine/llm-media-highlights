import logging
from configs import OUTPUT_DIRECTORY
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s: "
    "%(filename)s - %(funcName)s - line:%(lineno)d - %(message)s"
)

file_handler = logging.FileHandler(
    filename=os.path.join(OUTPUT_DIRECTORY, "debug.log"), encoding="utf-8", mode="w+"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
