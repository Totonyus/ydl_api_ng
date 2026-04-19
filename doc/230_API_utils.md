# Utils API endpoints

## yt-dlp information

Return the application complete parameters

```shell
GET http://localhost:5011/info
```

Response example :

```json5
{
  "ydl_engine": "yt-dlp",
  "ydl_version": "2026.03.17",
  "ydl_git_head": "04d6974f502bbdfaed72c624344f262e30ad9708",
  "ydl_api_ng_container_date": "unknown",
  "ydl_api_ng_branch": "unknown",
  "ydl_api_ng_revision": "unknown",
  "processed_config": {
    "meta_keys": {
      "_int": [
        "_int_test",
        "_listen_port",
        "_log_backups",
        "_log_level",
        "_redis_ttl",
        "_redis_port",
        "age_limit",
        "buffersize",
        "concurrent_fragment_downloads",
        "extractor_retries",
        "http_chunk_size",
        "max_filesize",
        "max_sleep_interval",
        "max_views",
        "min_filesize",
        "min_views",
        "ratelimit",
        "retries",
        "skip_playlist_after_errors",
        "sleep_interval",
        "sleep_interval_requests",
        "sleep_interval_subtitles",
        "socket_timeout",
        "throttledratelimit",
        "trim_file_name",
        "xattr_set_filesize"
      ],
      "_float": [
        "_float_test"
      ],
      "_bool": [
        "_allow_dangerous_post_requests",
        "_allow_programmation",
        "_bool_test",
        "_dev_mode",
        "_enable_redis",
        "_enable_users_management",
        "_skip_check",
        "_skip_info_dict",
        "allow_multiple_audio_streams",
        "allow_multiple_video_streams",
        "allow_playlist_files",
        "allow_unplayable_formats",
        "allsubtitles",
        "bidi_workaround",
        "break_on_existing",
        "break_on_reject",
        "break_per_url",
        "call_home",
        "check_formats",
        "clean_infojson",
        "continuedl",
        "debug_printtraffic",
        "dynamic_mpd",
        "extract_flat",
        "force_generic_extractor",
        "force_write_download_archive",
        "forcedescription",
        "forceduration",
        "forcefilename",
        "forceid",
        "forcethumbnail",
        "forcetitle",
        "forceurl",
        "format_sort_force",
        "geo_bypass",
        "getcomments",
        "hls_prefer_native",
        "hls_split_discontinuity",
        "hls_use_mpegts",
        "ignore_no_formats_error",
        "ignoreerrors",
        "include_ads",
        "keepvideo",
        "legacyserverconnect",
        "list_thumbnails",
        "listformats",
        "listsubtitles",
        "mark_watched",
        "no_color",
        "no_warnings",
        "nocheckcertificate",
        "nopart",
        "noplaylist",
        "noprogress",
        "noresizebuffer",
        "overwrites",
        "playlistrandom",
        "playlistreverse",
        "prefer_ffmpeg",
        "prefer_free_formats",
        "prefer_insecure",
        "quiet",
        "restrictfilenames",
        "simulate",
        "skip_download",
        "updatetime",
        "usenetrc",
        "verbose",
        "windowsfilenames",
        "write_all_thumbnails",
        "writeannotations",
        "writeautomaticsub",
        "writedescription",
        "writedesktoplink",
        "writeinfojson",
        "writelink",
        "writesubtitles",
        "writethumbnail",
        "writeurllink",
        "writewebloclink",
        "youtube_include_dash_manifest",
        "youtube_include_hls_manifest"
      ],
      "_array": [
        "_array_test",
        "_hosts",
        "_info_dict_field_retrieve",
        "_playlist_indicators",
        "_video_indicators",
        "format_sort",
        "subtitleslangs"
      ],
      "_object": [
        "_object_test",
        "_when_playlist",
        "_when_live",
        "compat_opts",
        "dump_single_json",
        "external_downloader",
        "external_downloader_args",
        "extractor_args",
        "forcejson",
        "forceprint",
        "http_headers",
        "match_filter",
        "outtmpl",
        "paths",
        "postprocessor_args",
        "postprocessor_hooks",
        "postprocessors",
        "print_to_file",
        "progress_hooks",
        "progress_template"
      ],
      "_hidden": [
        "_token",
        "_unit_test",
        "logger",
        "password",
        "postprocessor_hooks",
        "progress_hooks",
        "username"
      ]
    },
    "app_config": {
      "APP": {
        "_name": "APP",
        "_api_route_download": "/download",
        "_api_route_queue": "/queue",
        "_api_route_extract_info": "/extract_info",
        "_api_route_info": "/info",
        "_api_route_active_downloads": "/active_downloads",
        "_enable_users_management": false,
        "_log_level": 20,
        "_log_backups": 7,
        "_listen_port": 80,
        "_listen_ip": "0.0.0.0",
        "_enable_redis": true,
        "_redis_ttl": 3600,
        "_redis_host": "ydl_api_ng_redis",
        "_redis_port": 6379,
        "_skip_info_dict": true,
        "_allow_dangerous_post_requests": false,
        "_api_route_programmation": "/programmation",
        "_programmation_interval": 60,
        "_info_dict_field_retrieve": [
          "id",
          "title",
          "original_url",
          "duration"
        ]
      }
    },
    "user_config": {},
    "preset_config": {
      "DEFAULT": {
        "_name": "DEFAULT",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "format": "bestvideo+bestaudio/best",
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      },
      "AUDIO": {
        "_name": "AUDIO",
        "format": "bestaudio",
        "postprocessors": [
          {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320"
          },
          {
            "key": "EmbedThumbnail"
          },
          {
            "key": "FFmpegMetadata"
          },
          {
            "key": "FFmpegSplitChapters",
            "force_keyframes": false
          }
        ],
        "writethumbnail": true,
        "outtmpl": {
          "default": "audio/%(title)s.%(ext)s",
          "chapter": "audio/%(title)s/%(section_number)s-%(section_title)s.%(ext)s"
        },
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        }
      },
      "BEST": {
        "_name": "BEST",
        "format": "bestvideo+bestaudio/best",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      },
      "FULLHD": {
        "_name": "FULLHD",
        "format": "best[height=1080]/bestvideo[height=1080]+bestaudio/best",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      },
      "HD": {
        "_name": "HD",
        "format": "best[height=720]/bestvideo[height=720]+bestaudio/best",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      },
      "SD": {
        "_name": "SD",
        "format": "best[height=360]/bestvideo[height=360]+bestaudio/best",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": true,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      }
    },
    "site_config": {
      "KNOWN": {
        "_name": "KNOWN",
        "ignoreerrors": false
      },
      "YOUTUBE": {
        "_name": "YOUTUBE",
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
        "_when_playlist": {
          "_redis_queue": "ydl_api_ng_slow"
        },
        "ignoreerrors": false
      }
    },
    "auth_config": {},
    "location_config": {
      "DEFAULT": {
        "_name": "DEFAULT",
        "paths": {
          "home": "./downloads/"
        }
      }
    },
    "template_config": {
      "DEFAULT": {
        "_name": "DEFAULT",
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        }
      },
      "AUDIO": {
        "_name": "AUDIO",
        "outtmpl": {
          "default": "audio/%(title)s.%(ext)s",
          "chapter": "audio/%(title)s/%(section_number)s-%(section_title)s.%(ext)s"
        }
      }
    },
    "workers_config": {
      "SUPERVISORD": {
        "_name": "SUPERVISORD",
        "logfile": "/app/logs/supervisord.log",
        "pidfile": "/app/tmp/supervisord_pid",
        "loglevel": "%(ENV_LOG_LEVEL)s",
        "user": "%(ENV_UID)s"
      },
      "PROGRAMMATION": {
        "_name": "PROGRAMMATION",
        "command": "python3 programmation_daemon.py",
        "process_name": "%(program_name)s-%(process_num)s",
        "numprocs": "1",
        "directory": ".",
        "stopsignal": "TERM",
        "autostart": "true",
        "autorestart": "true",
        "user": "%(ENV_UID)s",
        "stdout_logfile": "/app/logs/%(program_name)s.log",
        "stderr_logfile": "/app/logs/%(program_name)s.log",
        "stdout_logfile_maxbytes": "25MB"
      },
      "WORKER_YDL_API_NG": {
        "_name": "WORKER_YDL_API_NG",
        "command": "rq worker ydl_api_ng -u \"redis://ydl_api_ng_redis:6379\"",
        "process_name": "%(program_name)s-%(process_num)s",
        "numprocs": "%(ENV_NB_WORKERS)s",
        "directory": ".",
        "stopsignal": "TERM",
        "autostart": "true",
        "autorestart": "true",
        "user": "%(ENV_UID)s",
        "stdout_logfile": "/app/logs/%(program_name)s.log",
        "stderr_logfile": "/app/logs/%(program_name)s.log",
        "stdout_logfile_maxbytes": "25MB"
      },
      "WORKER_YDL_API_NG_SLOW": {
        "_name": "WORKER_YDL_API_NG_SLOW",
        "command": "rq worker ydl_api_ng_slow -u \"redis://ydl_api_ng_redis:6379\"",
        "process_name": "%(program_name)s-%(process_num)s",
        "numprocs": "1",
        "directory": ".",
        "stopsignal": "TERM",
        "autostart": "true",
        "autorestart": "true",
        "user": "%(ENV_UID)s",
        "stdout_logfile": "/app/logs/%(program_name)s.log",
        "stderr_logfile": "/app/logs/%(program_name)s.log",
        "stdout_logfile_maxbytes": "25MB"
      }
    }
  }
}
```

# Extract info

Returns the standard youtube-dlp extract info object.

```shell
GET http://localhost:5011/extract_info?url=https://www.youtube.com/watch?v=9Lgc3TxqgHA
```

Or with a `POST` request to provide cookies :

```shell
POST http://localhost:5011/extract_info?url=https://www.youtube.com/watch?v=wV4wepiucf4
Content-Type: application/json

{
  "cookies" : "URL encoded (RFC3986 format) netscape cookies format"
}
```

## API return 

Example for youtube :
```json5
{
  "id": "a0sxBO9HZ-M",
  "title": "Moi j'envoie des GIF de loutres",
  "formats": [], // all available formats (censored for readability)
  "thumbnails": [], // all available thumbnails (censored for readability)
  "thumbnail": "https://i.ytimg.com/vi/a0sxBO9HZ-M/maxresdefault.jpg",
  "description": "Extrait de The Good Place, Saison 4 Épisode 8 : Irrévocables funérailles",
  "channel_id": "UCQexII-PYa3nOUYElK0sOPw",
  "channel_url": "https://www.youtube.com/channel/UCQexII-PYa3nOUYElK0sOPw",
  "duration": 3,
  "view_count": 91,
  "average_rating": null,
  "age_limit": 0,
  "webpage_url": "https://www.youtube.com/watch?v=a0sxBO9HZ-M",
  "categories": [
    "Gaming"
  ],
  "tags": [],
  "playable_in_embed": true,
  "live_status": "not_live",
  "media_type": "video",
  "release_timestamp": null,
  "_format_sort_fields": [
    "quality",
    "res",
    "fps",
    "hdr:12",
    "source",
    "vcodec",
    "channels",
    "acodec",
    "lang",
    "proto"
  ],
  "automatic_captions": {}, // all available captions (censored for readability, it really a lot)
  "subtitles": {},
  "comment_count": null,
  "chapters": null,
  "heatmap": null,
  "like_count": 2,
  "channel": "Totonyus",
  "channel_follower_count": 450,
  "creators": null,
  "uploader": "Totonyus",
  "uploader_id": "@Totonyus",
  "uploader_url": "https://www.youtube.com/@Totonyus",
  "upload_date": "20191127",
  "timestamp": 1574879390,
  "availability": "public",
  "original_url": "https://www.youtube.com/watch?v=a0sxBO9HZ-M",
  "webpage_url_basename": "watch",
  "webpage_url_domain": "youtube.com",
  "extractor": "youtube",
  "extractor_key": "Youtube",
  "playlist": null,
  "playlist_index": null,
  "display_id": "a0sxBO9HZ-M",
  "fulltitle": "Moi j'envoie des GIF de loutres",
  "duration_string": "3",
  "release_year": null,
  "is_live": false,
  "was_live": false,
  "requested_subtitles": null,
  "_has_drm": null,
  "epoch": 1776606203,
  "requested_formats": [], // requested formats (censored for readability)
  "format": "136 - 1280x720 (720p)+251 - audio only (medium)",
  "format_id": "136+251",
  "ext": "mkv",
  "protocol": "https+https",
  "language": "es",
  "format_note": "720p+medium",
  "filesize_approx": 484269,
  "tbr": 1176.267,
  "width": 1280,
  "height": 720,
  "resolution": "1280x720",
  "fps": 24,
  "dynamic_range": "SDR",
  "vcodec": "avc1.64001f",
  "vbr": 1058.342,
  "stretched_ratio": null,
  "aspect_ratio": 1.78,
  "acodec": "opus",
  "abr": 117.925,
  "asr": 48000,
  "audio_channels": 2
}
```