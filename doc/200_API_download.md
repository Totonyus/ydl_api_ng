# Download API

Only the url is required to use the api.

```shell
# Simplest case, uses the DEFAULT preset
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=9Lgc3TxqgHA

# You can download multiple presets at once, if no preset is valid, will download with DEFAULT preset, if at least one preset is valid, will download only valid presets
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=Kf1XttuuIiQ&presets=audio,hd

# If the user management is enabled
GET http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4&token=dad_super_password
```

## Post request

You can download the video you want by providing the parameters directly in a post request. The order of the expandable attributes is important : each attribute will be expanded in this order.

```shell
POST http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4&token=dad_super_password
Content-Type: application/json

{
  "cookies" : "URL encoded (RFC3986 format) netscape cookies format",
  "presets": [
  {
    "_ignore_site_config": false,    # (optional, default : false) if true, will not load parameters from site detection
    "_ignore_default_preset": false, # (optional, default : false) if true, will not expand default preset
    # You can expand parameters
    "_preset" : "AUDIO",
    "_location" : "AUDIO",
    # just put below your standard youtube-dlp options
    "format" : "best[height=360]/bestvideo[height=360]+bestaudio/best"
  }
  ]
}
```

It is possible to add a timer to stop the download (`recording_stops_at_end` will be automatically set on `True`) :

```shell
POST http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4&token=dad_super_password
Content-Type: application/json

{
  "programmation": {
    "planning": {
      "recording_duration": 10
    }
  },
  "presets": [
    {
      "_preset": "HD"
    }
  ]
}
```

Reminder : if you want to expand a preset : all presets automatically expand the `DEFAULT` preset. Basically, expand a
preset with `_preset` means `_ignore_default_preset`can't be true.

You can use the `_cli` attribute here :
```shell
POST http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4
Content-Type: application/json

{
  "presets": [
    {
      "_template": "AUDIO",
      "_cli" : "-f bestaudio --embed-metadata --embed-thumbnail --extract-audio --audio-format mp3 --split-chapters",
    }
  ]
}
```

### Important notice

As the post request can be dangerous by allowing to write anywhere on your system
(if not running in docker) a parameter `_allow_dangerous_post_requests` (`false` by default) has been added.

For each preset if `_allow_dangerous_post_requests` is false :

- `paths` will be deleted and replaced by the `default` location parameter
- `outtmpl` will be deleted and replaced by the `default` template parameter
- You still can select a `paths` or a `outtmpl` by using expansion system
- You can only use `paths` and `outtmpl` present in `params.ini`

## API return

Here an example of what you get as API return after a download

```json
{
  "status_code": 200,
  "url": "https://www.youtube.com/watch?v=a0sxBO9HZ-M",
  "url_hostname": "www.youtube.com",
  "no_preset_found": false,
  "presets_found": 1,
  "presets_not_found": 0,
  "all_downloads_checked": true,
  "passed_checks": 1,
  "failed_checks": 0,
  "downloads_can_be_checked": 1,
  "downloads_cannot_be_checked": 0,
  "ignore_post_security": false,
  "relaunch_failed_mode": null,
  "downloads": [
    {
      "_name": "SD",
      "format": "best[height=360]/bestvideo[height=360]+bestaudio/best",
      "_ignore_default_preset": true,
      "_default": false,
      "_hosts": [
        "music.youtube.com",
        "www.youtube.com",
        "youtu.be"
      ],
      "_video_indicators": [
        "/watch?"
      ],
      "_playlist_indicators": [
        "?list=",
        "&list=",
        "/user/",
        "/playlists",
        "/videos",
        "/featured"
      ],
      "_redis_queue": "ydl_api_ng_slow",
      "_when_live": {
        "_redis_queue": "ydl_api_ng"
      },
      "ignoreerrors": false,
      "__check_exception_message": null,
      "__can_be_checked": true,
      "__check_result": true,
      "__is_video": true,
      "__is_playlist": false,
      "_redis_id": "82981af0-dab8-4a2f-85e7-34abc40caac9",
      "_redis_ttl": 3600
    }
  ],
  "programmation": null,
  "programmation_date": null,
  "programmation_end_date": null,
  "extra_parameters": null
}
```