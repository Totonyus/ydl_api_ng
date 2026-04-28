# Hooks

There are 4 types of hooks :

- [postprocessor_hooks.py](../params/postprocessor_hooks.py)
- [progress_hooks.py](../params/progress_hooks.py)
- [ydl_api_programmation_hooks.py](../params/ydl_api_programmation_hooks.py)
- [ydl_api_hooks.py](../params/ydl_api_hooks.py)

## Progress and Postprocessors hooks

Those 2 hooks are standard `yt-dlp` hooks.

- `progress_hooks` : launched periodically during download with informations of how the download is going.
    - May not be trigger in certain cases like livestreams of during the download of a file you already have
- `postprocessors_hooks` : triggered at the beginning and at the end of post process, event is the postprocessor does
  nothing

## ydl_api_programmation hooks

- `purged_programmation_handler` : Triggered when a programmation is automatically deleted
- `post_launch_handler` : Triggered when a download is launched by the daemon
- `post_termination_handler` : Triggered when a programmation is stopped by the daemon

## ydl_api_hooks

Hooks triggered for specific `ydl_api_ng` lifecycle steps.

- `pre_download_handler` : triggered just before preset effective download
- `post_download_handler` : triggered after all files of the preset are downloaded
- `post_termination_handler` : triggered after a download is terminated by the user
- `post_redis_termination_handler` : triggered after a download is terminated by the user (or programmation) (in redis)

# Usage

To override the default hooks, you must copy the hook file in your `params/` directory.

# Requirements

If you need specify python packages for your hooks, you can create the `params/hooks_requirements` file with all you
need.

# Warning

A bad hook file may prevent `ydl_api_ng` or `yt-dlp` from working properly.

# Example (from my usage)

Send a telegram notification when :

- a programmation is removed automatically
- a programmation triggered a download
- a file is downloaded or failed to download
- create a symlink to make the file available via reverse proxy (and send the link)