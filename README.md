## SUMMARY

Given a media file, parse the audio using whisper into an srt file.  
Then use an LLM to find a number of highlights with timestamps

Also includes MagicScript scripts (`Magic Scripts/`) for use in DaVinci Resolve,  
to import the LLM timestamps as spanning markers and rebuild timelines from them.

## MAGICSCRIPT (DAVINCI RESOLVE PLUGIN)

- MagicScript is a DaVinci Resolve plugin created by YouTuber MrAlexTech
- Requires DaVinci Resolve Studio edition (the paid version) - it will not run on the free Resolve

___

## HOW TO

### TORCH
- https://pytorch.org/ use compatibility installation tool here BEFORE installing the CUDA version below

### CUDA
Depending on your GPU, may need to install cuda toolkit  
https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_network

### ffmpeg
- may be needed depending on the media file format input
- it may not be enough to install ffmpeg via pip
- https://ffmpeg.org/download.html
  - if windows, also need to add ffmpeg to PATH

original repo's details here:
https://github.com/openai/whisper
