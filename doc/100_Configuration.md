# Configuration

## Mandatory

Those files will be copied in your `params/` directory on the first launch :

- `params.ini` all the default parameters of the application, if you use the container version, the default
  configuration file will in fact be [params_docker.ini](../params/params_docker.ini)

## Optional

Those files will not be automatically copied in your `params/` directory but you can override the default ones but
putting the files in it

- `workers.ini` : see [redis queues configuration](104_Redis_queues.md)
- `params_metadata.ini` : see [metadata_configuration](101_Configuration_metadata.md)
- hooks files : see [hooks](300_Hooks.md)
    - [postprocessor_hooks.py](../params/postprocessor_hooks.py)
    - [progress_hooks.py](../params/progress_hooks.py)
    - [ydl_api_hooks.py](../params/ydl_api_hooks.py)
    - [ydl_api_programmation_hooks.py](../params/ydl_api_programmation_hooks.py)

## Convention

- All the "basic" options are supposed to be `yt-dlp` compatible options : [documentation](https://github.com/yt-dlp/yt-dlp/blob/cda1bc51973c89b72b916dcc40dbe3d7f457097d/yt_dlp/YoutubeDL.py#L183)
- All the options starting with a `_` are `ydl_api_ng` specific options : you can of course create your own with this
  format but it may create problems if I decide to use the same option name in a future release
- You may find in api responses options starting with `__` : those are information added by `ydl_api_ng` during
  processing 