# Whisper Highlighter

Given a media file, parse the audio using whisper into an srt file.  
Then use an LLM to find a number of highlights with timestamps

___

## HOW TO

### DOWNGRADE TO PYTHON 3.11
- the installation seems incompatible with python 3.13

### TORCH
- https://pytorch.org/ use compatibility installation tool here
- I used pip for my windows machine

### CUDA
Depending on your GPU, may need to install cuda toolkit  
https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_network

### ffmpeg
- it may not be enough to install ffmpeg via pip
- https://ffmpeg.org/download.html
  - if windows, also need to add ffmpeg to PATH

original repo's details here:
https://github.com/openai/whisper