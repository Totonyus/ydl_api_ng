# Queue management

A new system of queue management has been build to have a better view of current, past and future downloads.

You can choose the number of workers in the docker-compose file : `NB_WORKERS=5` (environment parameter). The number of
workers determines the number of parallel downloads.

## Without docker

You can perfectly run ydl_api_ng with redis without docker. However, to keep it simple for basic users, the option is
disabled by default in the `params.ini` file :

    _enable_redis = true # (false is not in parameter file)
    _redis_host = localhost
    _redis_port = 6379

The application will run downloads without redis and the old queue management system will be used for the
api `/active_downloads` and `/terminate`

## With docker

If you don't want to use redis with docker, you can remove the corresponding block in the docker-compose
file : `ydl_api_ng_redis`.

You must disable redis in the `params.ini` file : `_enable_redis = false`

You can also pass the `DISABLE_REDIS` environment parameter in the docker-compose file to avoid workers getting
launched.

## Queue usage

You can define as many as queues as you want by modifying the `workers.ini` file.

By default, there are two different queues : `ydl_api_ng` (with 5 workers) and `ydl_api_ng_slow` with only one worker.

If all workers from a queue are busy, downloads requests will be in "pending" state and will be launched as soon as a
worker is freed.

# Process management API

## Global

```shell
# Get all active downloads (with PID)
GET http://localhost:5011/active_downloads

# Stop all active downloads
GET http://localhost:5011/active_downloads/terminate

# Stop the active download with it PID. It uses se system PID, this feature is safe, a non-child process cannot be killed
# If using redis, also permit to cancel pending job
# If job is finished or canceled, will delete from queue
GET http://localhost:5011/active_downloads/terminate/{pid}
```

## Redis only

```shell
# Get all registries content
GET http://localhost:5011/queue

# Get registry content (all, workers, pending_job, started_job, finished_job, failed_job, deferred_job, scheduled_job, canceled_job)
GET http://localhost:5011/queue/finished_job

# Delete all jobs but pending and started jobs
DELETE http://localhost:5011/queue
```

## API return
### Normal video

```json
{
  "pending_job": [],
  "started_job": [],
  "finished_job": [
    {
      "id": "63fb1cee-640b-49d5-818c-0894d54a7fb6",
      "preset": {
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
        "__can_be_checked": false,
        "__check_result": null,
        "__is_video": false,
        "__is_playlist": true
      },
      "download_manager": {
        "status_code": 202,
        "url": "https://www.youtube.com/playlist?list=PL8Zccvo5Xlj6LnmfpOligIqnUjfnM0X2R",
        "url_hostname": "www.youtube.com",
        "no_preset_found": false,
        "presets_found": 1,
        "presets_not_found": 0,
        "all_downloads_checked": false,
        "passed_checks": 1,
        "failed_checks": 0,
        "downloads_can_be_checked": 0,
        "downloads_cannot_be_checked": 1,
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
            "__can_be_checked": false,
            "__check_result": null,
            "__is_video": false,
            "__is_playlist": true
          }
        ],
        "programmation": null,
        "programmation_date": null,
        "programmation_end_date": null,
        "extra_parameters": null
      },
      "job": {
        "status": "finished",
        "result": null,
        "queue_name": "ydl_api_ng_slow",
        "result_ttl": 3600,
        "redis_id": "63fb1cee-640b-49d5-818c-0894d54a7fb6",
        "enqueued_at": "2026-04-19T20:08:10.935317+00:00",
        "started_at": "2026-04-19T20:08:11.311720+00:00",
        "ended_at": "2026-04-19T20:08:16.876839+00:00",
        "exc_info": null,
        "last_heartbeat": "2026-04-19T20:08:16.876842+00:00",
        "worker_name": "d91a17b982db403dadd87c3573a817dd",
        "meta": {
          "programmation_id": null,
          "programmation_date": null,
          "programmation_end_date": null,
          "downloaded_files": [
            {
              "id": "4rPyCPaVOqQ",
              "status": "finished",
              "filename": "Moi aussi je dois être pas contente, je dois avoir une raison de ronchonner ! [4rPyCPaVOqQ].mp4",
              "_filename": "Moi aussi je dois être pas contente, je dois avoir une raison de ronchonner ! [4rPyCPaVOqQ].mp4",
              "total_bytes": 181813,
              "elapsed": 0.11942362785339355,
              "info_dict": {
                "id": "4rPyCPaVOqQ",
                "title": "Moi aussi je dois être pas contente, je dois avoir une raison de ronchonner !",
                "original_url": "https://www.youtube.com/watch?v=4rPyCPaVOqQ",
                "duration": 5
              },
              "sub_downloads": {
                "18": {
                  "downloaded_bytes": 181813,
                  "total_bytes": 181813,
                  "filename": "Moi aussi je dois être pas contente, je dois avoir une raison de ronchonner ! [4rPyCPaVOqQ].mp4",
                  "status": "finished",
                  "elapsed": 0.11942362785339355,
                  "speed": 1522420.6739322697,
                  "_percent": 100.0
                }
              }
            },
            {
              "id": "YPYa0j5PftY",
              "status": "finished",
              "filename": "Je suis tellement mignonne que j'ai jamais fait le moindre petit caca de toute ma vie [YPYa0j5PftY].mp4",
              "_filename": "Je suis tellement mignonne que j'ai jamais fait le moindre petit caca de toute ma vie [YPYa0j5PftY].mp4",
              "total_bytes": 542289,
              "elapsed": 0.8382506370544434,
              "info_dict": {
                "id": "YPYa0j5PftY",
                "title": "Je suis tellement mignonne que j'ai jamais fait le moindre petit caca de toute ma vie",
                "original_url": "https://www.youtube.com/watch?v=YPYa0j5PftY",
                "duration": 12
              },
              "sub_downloads": {
                "18": {
                  "downloaded_bytes": 542289,
                  "total_bytes": 542289,
                  "filename": "Je suis tellement mignonne que j'ai jamais fait le moindre petit caca de toute ma vie [YPYa0j5PftY].mp4",
                  "status": "finished",
                  "elapsed": 0.8382506370544434,
                  "speed": 646929.4218559347,
                  "_percent": 100.0
                }
              }
            }
          ]
        }
      }
    }
  ],
  "failed_job": [],
  "deferred_job": [],
  "scheduled_job": [],
  "canceled_job": []
}
```

### Stopped download

When a livestream recording is stopped, no postprocessors hooks are triggered, here the after a `/terminate/{redis_id}` request :

```json
{
  "pending_job": [],
  "started_job": [],
  "finished_job": [
    {
      "id": "740b7721-38e7-4e2c-94e0-09b2106b758a",
      "preset": {
        "_name": "SD",
        "format": "best[height=360]/bestvideo[height=360]+bestaudio/best",
        "quiet": true,
        "noplaylist": true,
        "updatetime": false,
        "restrictfilenames": true,
        "windowsfilenames": true,
        "ignoreerrors": false,
        "_when_playlist": {
          "ignoreerrors": true
        },
        "cachedir": "/home/ydl_api_ng/cache",
        "paths": {
          "home": "./downloads/"
        },
        "outtmpl": {
          "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
        },
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
        "_redis_queue": "ydl_api_ng",
        "_when_live": {
          "_redis_queue": "ydl_api_ng"
        },
        "__check_exception_message": null,
        "__can_be_checked": true,
        "__check_result": true,
        "__is_video": true,
        "__is_playlist": false
      },
      "download_manager": {
        "status_code": 200,
        "url": "https://www.youtube.com/watch?v=aQWyyI7JmTk",
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
            "quiet": true,
            "noplaylist": true,
            "updatetime": false,
            "restrictfilenames": true,
            "windowsfilenames": true,
            "ignoreerrors": false,
            "_when_playlist": {
              "ignoreerrors": true
            },
            "cachedir": "/home/ydl_api_ng/cache",
            "paths": {
              "home": "./downloads/"
            },
            "outtmpl": {
              "default": "videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s"
            },
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
            "_redis_queue": "ydl_api_ng",
            "_when_live": {
              "_redis_queue": "ydl_api_ng"
            },
            "__check_exception_message": null,
            "__can_be_checked": true,
            "__check_result": true,
            "__is_video": true,
            "__is_playlist": false
          }
        ],
        "programmation": null,
        "programmation_date": null,
        "programmation_end_date": null,
        "extra_parameters": null
      },
      "job": {
        "status": "finished",
        "result": null,
        "queue_name": "ydl_api_ng",
        "result_ttl": 3600,
        "redis_id": "740b7721-38e7-4e2c-94e0-09b2106b758a",
        "enqueued_at": "2026-04-19T20:16:28.102593+00:00",
        "started_at": "2026-04-19T20:16:28.419508+00:00",
        "ended_at": "2026-04-19T20:17:01.747945+00:00",
        "exc_info": null,
        "last_heartbeat": "2026-04-19T20:17:01.747947+00:00",
        "worker_name": "48282085112d44e485f7bc32f19c4a98",
        "meta": {
          "programmation_id": null,
          "programmation_date": null,
          "programmation_end_date": null,
          "filename_info": {
            "part_filename": "downloads/videos/youtube.com/24_7_Shiny_Pokemon_Bot_-_Emerald_faq_target_guide_clips_download_bingo_2026-04-19_22_16_(360).mp4.part",
            "filename": "downloads/videos/youtube.com/24_7_Shiny_Pokemon_Bot_-_Emerald_faq_target_guide_clips_download_bingo_2026-04-19_22_16_(360).mp4",
            "path": "downloads/videos/youtube.com/",
            "filename_stem": "24_7_Shiny_Pokemon_Bot_-_Emerald_faq_target_guide_clips_download_bingo_2026-04-19_22_16_(360)",
            "extension": ".mp4",
            "full_filename": "24_7_Shiny_Pokemon_Bot_-_Emerald_faq_target_guide_clips_download_bingo_2026-04-19_22_16_(360).mp4",
            "file_size": 2883584
          },
          "terminated": true
        }
      }
    }
  ],
  "failed_job": [],
  "deferred_job": [],
  "scheduled_job": [],
  "canceled_job": []
}
```