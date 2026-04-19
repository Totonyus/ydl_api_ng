# Presets

`ydl_api_ng` works with a system of presets.

A preset is a predefined set of options.

## Presets types

There is 6 types of presets. Some are not really useful but stay here for compatibility purpose :

- `preset:<NAME>` : meant for different download options (audio only, video, archiving...)
- `location:<NAME>` : different locations for downloads
- `template:<NAME>` : different output templates for
  downloads ([documentation](https://github.com/yt-dlp/yt-dlp#output-template))
- `user:<NAME>` : specific options for a given user
- `site:<NAME>` : specific options for a given site
- `auth:<NAME>` : for username/password/cookies, mostly useless

## Convention

- All the "basic" options are supposed to be `yt-dlp` compatible
  options : [documentation](https://github.com/yt-dlp/yt-dlp/blob/cda1bc51973c89b72b916dcc40dbe3d7f457097d/yt_dlp/YoutubeDL.py#L183)
- All the options starting with a `_` are `ydl_api_ng` specific options : you can of course create your own with this
  format but it may create problems if I decide to use the same option name in a future release

Note that `yt-dlp` is just ignores options it doesn't know, it helps a lot.

## Default preset

The only mandatory preset is the default one. If not stated specifically, all others presets will extend the DEFAULT
preset.

```
[preset:DEFAULT]
_location = DEFAULT
_template = DEFAULT
quiet = true
noplaylist = true
updatetime = false
format = bestvideo+bestaudio/best
restrictfilenames = true
windowsfilenames = true
ignoreerrors = true
_when_playlist = {"ignoreerrors" : true}
cachedir = /home/ydl_api_ng/cache
```

## Expansion

A preset can extend another preset. For example, the default preset extends two presets : `LOCATION` and `TEMPLATE`

All the options present in extended presets will override the current preset.

Example :

```
[preset:HD]
subtitleslangs = fr,en
_preset = FHD

[preset:FHD]
subtitleslangs = es
```

Will result in:

```
[preset:HD]
subtitleslangs = es
```

## Specificity of site and users presets

Those two presets types are processed before download and not on app launch

Precedence from lowest to highest : preset, user, site

### user

```
[user:TOTONYUS]
;; mandatory
_token = totonyus_super_password
;; optional, default = false
_allow_programmation = true

;; Exemple of user specific options you may want to add
subtitleslangs = fr,en
writesubtitles = true
```

## Site

There is no mandatory options for this one but remember `ydl_api_ng` is not (yet ?) capable of retrieving certain
informations from `yt-dlp` so you'll probrably want to keep the at least the `_video_indicators` and
`_playlist_indicators` options.

```
[site:YOUTUBE]
_hosts = music.youtube.com,www.youtube.com,youtu.be
_video_indicators = /watch?
;; download check will not be performed on playlists (youtube-dl checks every video of the playlist)
_playlist_indicators = ?list=,&list=,/user/,/playlists,/videos,/featured
;; Default redis queue for this site
_redis_queue = ydl_api_ng_slow
;; However, if this is a running livestream : use the usual queue
_when_live = {"_redis_queue": "ydl_api_ng"}
```

# Special options

Some options are used directly by `yt-dlp` :

| option                 | usage                                                                         |
|------------------------|-------------------------------------------------------------------------------|
| _ignore_default_preset | Will not extend default preset                                                |
| _ignore_site_config    | Will not automatically extend site preset                                     |
| _hosts                 | All hostnames of a website                                                    |
| _video_indicators      | All things that may indicates this is not a playlist                          |
| _playlist_indicators   | All things that may indicates this is a playlist                              |
| _redis_queue           | The redis queue to use                                                        |
| _when_live             | Options to apply when it's a running livestream (detection from `yt-dlp` api) |
| _when_playlist         | Options to apply when it's a playlist (detection from `_playlist_indicators`) |
| _cli                   | Continue reading this file                                                    |

# The `_cli` parameter

The `_cli` parameter allows the usage of a command line configuration to make `ydl_api_ng` even simpler.

Note you cannot pass the url to download in the `_cli` paramater

```
[preset:AUDIO_CLI]
_template = AUDIO
_cli = -f bestaudio --embed-metadata --embed-thumbnail --extract-audio --audio-format mp3 --split-chapters
```

Is the same thing as:

```
[preset:AUDIO]
_template = AUDIO
format = bestaudio
writethumbnail = true
final_ext = mp3
postprocessors: [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "5", "nopostoverwrites": false}, {"key": "FFmpegMetadata", "add_chapters": true, "add_metadata": true, "add_infojson": "if_exists"}, {"key": "EmbedThumbnail", "already_have_thumbnail": false}, {"key": "FFmpegSplitChapters", "force_keyframes": false}]}
```

To use a yt-dlp configuration file:

```
[preset:AUDIO]
_cli = --config-location params/conf_audio.conf
```
