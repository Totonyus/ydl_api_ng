# ydl_api_ng

ydl_api_ng is the new version of [ydl_api](https://github.com/Totonyus/ydl_api)

## But why ?

ydl_api was built to fulfill my needs, and it works really well for me. However, it has a few drawbacks :

- limited to a few parameters
- complexity to add new parameters in the api
- Not suitable for advanced youtube-dl users

## Differences with ydl_api ?

- A huge portion of the codebase has been rewritten
- A new system of parameter file
- More powerful : you can now add any youtube-dlp option to enhance your downloads
- Better maintainability : no need new devs on this application if youtube-dlp adds new options
- Suitable for advanced youtube-dlp users
- Not complicated for basic users
- New features are planned
- (Optional) Use redis for a better queue management

# Installation

## With docker

Container on Docker Hub [here](https://hub.docker.com/r/totonyus/ydl_api_ng)

The parameters files are generated in the params volume on the first launch of the container.

### Volumes mapping

Volumes you could want to map :

- `/app/downloads/` : where files will be downloaded
- `/app/params/` : where the parameters files will be stored
- `/app/params/hooks_utils/` : if you need to import your own python scripts for the hooks handlers
- `/app/logs`

### Ports

The internal port of the api is `80`

### Docker-compose

Just copy the `docker-compose.yml` file where you want and launch this command :

```shell
docker-compose pull # pull the latest image
docker-compose up # to start the container
docker-compose down # to stop the container
```

## Force yt-dlp version:
Add the version of `yt-dlp` you want in docker environment :

```
FORCE_YTDLP_VERSION=2022.11.11
```

### By command line

```shell
docker run -p 5011:80 totonyus/ydl_api_ng # don't forget to map the folders
```

Note : the standard image comes with redis enabled. Please view on the queue management documentation to know how to disable it.

You can also find the `docker-compose.yml` file.

### UID and GID

The default user used in the container is `1000:1000`. You can edit those by changing the environment vars `UID`
and `GID` in the `docker-compose.yml` or in the `docker run` command.

The user must be root (`UID=0` ans `GID=0`) or match the owner of the download repository.

To know your `UID` and `GID`, simple run this command with the right user or check your `/etc/passwd` file.

```shell
echo $UID $GID
```

## Without Docker

### Requirements

* Installation with distribution package manager (`apt`, `yum`, ...) : `python3`, `python3-pip`, `ffmpeg`

```shell
pip3 install -r pip_requirements
``` 

### Download this repo

Download the latest release :

```shell
wget https://github.com/Totonyus/ydl_api_ng/archive/master.zip
```

Then unzip the file and rename the unzipped folder : (note you can use `unzip -d %your_path%` to specify where you want
to unzip the file )

```shell
unzip master.zip; mv ydl_api_ng-master ydl_api_ng
```

### Modify listening port

The api listen by default on the port `80`. It's perfect for docker use but not really a good idea for a bare metal
user. Set the port you want in the `params.ini` file.

### Install as daemon

Just fill the `ydl_api_ng.service` file and move it in `/usr/lib/systemd/system/` for `systemd` linux.

```shell
mv ydl_api.service /usr/lib/systemd/system/
```

You can change the name of the service by changing the name of the file.

then (you must run this command every time you change the service file)

```shell
systemctl daemon-reload
```

Commands :

```shell
systemctl start ydl_api_ng
systemctl stop ydl_api_ng
systemctl enable ydl_api_ng # start at boot
systemctl disable ydl_api_ng # don't start at boot
```

### Install the userscript

Install [Greasemonkey (firefox)](https://addons.mozilla.org/fr/firefox/addon/greasemonkey/)
or [Tampermonkey (chrome)](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=fr)
and add a new userscript. Then copy the content of `userscript.js` in the interface and save.

Then change the default host set in the script. You can also customize all the presets to match the configuration file
of your server.

You now should have access to download options on every site. You can also modify the match options to limit the usages.

![Userscript in action](userscript.jpg)

## Files you'll probably want to consult or customize

These files are generated in `params/`

* `params.ini` all the default parameters of the application, everything is set up to offer you a working application
  out of the box
* `params_metadata.ini` describe how each parameter in `params.ini` should be interpreted
* `userscript.js` a javascript file you can import
  in [Greasemonkey (firefox)](https://addons.mozilla.org/fr/firefox/addon/greasemonkey/)
  or [Tampermonkey (chrome)](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=fr)
  to access the api from yout browser
* `progress_hooks.py` youtube-dl progress hooks handler method
* `postprocessor_hooks.py` youtube-dl postprocessor hooks handler method
* `ydl_api_hooks.py` api hooks handler methods, only called at few moments
* `hooks_requirements` the extra requirements you need to fully use the hooks

There files are in the base folder :

* `docker-compose.yml` to configure easily the container
* `ydl_api_ng.service` a systemd service file to launch this application as a daemon

## Updating youtube-dlp

### Docker

Simply reload the container, an update is performed at launch

### Without docker

```shell
pip3 install yt_dlp --upgrade
```

## Configuration details

### parameters_metadata.ini

Each parameter in the `params.ini` file is a string. The `parameters_metadata.ini` file is used to describe how each
parameter must be cast.

As I don't know any option of `youtuble-dlp`, I tried my best to arrange the fields correctly but some are probably
wrong.

Please don't hesitate to make a merge request or to open a ticket on this repo to ask the correction.

You can also add your own parameters fields if you need it.

### params.sample.ini

This file is a complete working configuration file who is fully documented to help you to understand how it works.

### The `_cli` parameter
The `_cli` parameter allows the usage of a command line configuration to make `ydl_api_ng` even more simple than before.

```
[preset:AUDIO_CLI]
_template = AUDIO
_cli = -f bestaudio --embed-metadata --embed-thumbnail --extract-audio --audio-format mp3 --split-chapters
```

Is the same thing than:
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

## User management

If the user management is activated (disabled by default), each request must have the `&token` query parameter. You can
override some parameters for a specific user.

## Site management

You can define parameters for given websites. It's useful to avoid long-running playlist download simulation.

```ini
# Every host matching this site
_hosts = www.youtube.com,youtu.be
# How to define the url is a video 
_video_indicators = /watch?
# How to define the url is a playlist
_playlist_indicators = ?list=,&list=,/user/,/playlists
```

You can also add parameters tied to the site like login information

## Queue management

A new system of queue management has been build to have a better view of current, past and future downloads.

You can choose the number of workers in the docker-compose file : `NB_WORKERS=5` (environment parameter). The number of
workers determines the number of parallel downloads.

### Without docker

You can perfectly run ydl_api_ng with redis without docker. However, to keep it simple for basic users, the option is
disabled by default in the `params.ini` file :

    _enable_redis = true # (false is not in parameter file)
    _redis_host = localhost
    _redis_port = 6379

The application will run downloads without redis and the old queue management system will be used for the
api `/active_downloads` and `/terminate`

### With docker

If you don't want to use redis with docker, you can remove the corresponding block in the docker-compose
file : `ydl_api_ng_redis`.

You must disable redis in the `params.ini` file : `_enable_redis = false`

You can also pass the `DISABLE_REDIS` environment parameter in the docker-compose file to avoid workers launching.

## Programmation
A new feature allow you to schedule ydl_dlp executions. This feature needs `redis`.

Three usecases:
- Continuously download a livestream when it's available
- Archive a channel at given hours
- Schedule a download at a precise date for a precise duration

### Representation
Here what a programmation object looks like in database :
```json
{
"id": "string (generated)",
"url": "string",
"user_token": "string (null)",
"enabled": "bool (true)",
"planning": {
    "recording_start_date": "string date : YYYY-MM-DD hh:mm (null)",
    "recording_duration": "int > 0 (null)",
    "recording_stops_at_end": "bool (false)",
    "recording_restarts_during_duration" : "bool (true)",

    "recurrence_cron": "string (null)",
    "recurrence_start_date": "string date : YYYY-MM-DD hh:mm (null)",
    "recurrence_end_date": "string date : YYYY-MM-DD hh:mm (null)"
    },
"presets": ["string"], 
"extra_parameters" : {}
}
```

Fields:
- `id` : generated by the api
- `url` : url to download, it will not be checked
- `user_token` : unused if the `_allow_programmation` is not explicitly set at true in the user config
- `enabled` : if false, the programmation will be ignored
- `planning.recording_start_date`
- `planning.recording_duration` : how many minutes recording is supposed to long
- `planning.recording_stops_at_end` : if true, the download will be force stopped when `recording_duration` is reached
- `planning.recording_restarts_during_duration` : if False, the download will not be restarted if stopped before `recording_duration`
- `planning.recurrence_cron` : same cron as linux
- `planning.recurrence_start_date` : useful only if `recurrence_cron` is used
- `planning.recurrence_end_date` : useful only if `recurrence_cron` is used
- `presets` : list of presets names
- `extra_parameters` : an arbitrary object of parameters you can use to store informations or directives to use in hooks

Notes:
- `recording_start_date` and `recurrence_cron` cannot be used at the same type
- if `recording_duration` is set, the download will be relaunched automatically if stopped during the interval 

### Reliability
The launch hours are not perfectly exact and have an error range of `-1` minute

### Examples of minimal configurations
#### Continuous download

```json
{
"url": "string"
}
```

#### Archiving execution
```json
{
"url": "string",
"planning": {
    "recurrence_cron": "00 01 * * *"
    }
}
```

#### Special program
Every day in december from 13:00 to 14:00
```json
{
"url": "string",
"planning": {
    "recording_duration": 60,
    "recording_stops_at_end": true,

    "recurrence_cron": "00 13 * * *",
    "recurrence_start_date": "2022-12-01 00:00",
    "recurrence_end_date": "2022-12-31 23:00"
    }
}
```

#### One time special program

Will last at least 4 hours
```json
{
  "url": "string",
  "planning": {
    "recording_start_date" : "2022-12-31 22:00",
    "recording_duration": 240
  }
}
```

#### Programmation with extra parameters

```json
{
  "url": "string",
  "planning": {
    "recurrence_cron": "00 * * * *"
  },
  "extra_parameters": {
    "notification_level": "critical",
    "video_description": "Josephine Ange Gardien - 25th anniversary epic trailer"
  }
}
```

# API

## Application information

Return the application complete parameters

```shell
GET http://localhost:5011/info
```

### Responses status

* `401` : User is not permitted

## Downloads

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
POST http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4 &
token=dad_super_password
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

## Video information

Returns the standard youtube-dlp extract info object.

```shell
GET http://localhost:5011/extract_info?url=https://www.youtube.com/watch?v=9Lgc3TxqgHA
```

### Responses status

* `401` : User is not permitted

## Process management

The process management system only works on livestreams

### Global

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

### Redis only

```shell
# Get all registries content
GET http://localhost:5011/queue

# Get registry content (all, workers, pending_job, started_job, finished_job, failed_job, deferred_job, scheduled_job, canceled_job)
GET http://localhost:5011/queue/finished_job

# Delete all jobs but pending and started jobs
DELETE http://localhost:5011/queue
```

## Programmation
```shell
# Get programmations in database
GET {{host}}/programmation?token=user_token

# Add a new programmation
POST {{host}}/programmation?url=an_added_url&token=user_token

{
  "planning": {
    "recording_duration": 60,
    "recurrence_cron": "00 12 * * *"
  }
} 

# Update a programmation
PUT {{host}}/programmation/<id>

{
  "planning": {
    "recurrence_end_date" : "2022-12-31 00:00"
  }
}

# Delete a programmation by ID
DELETE {{host}}/programmation/<ID>

# Delete all programmations for the URL
DELETE {{host}}/programmation?url=url
```


## Responses status

* `401` : User is not permitted

# Redis queues
If redis is enabled, there is two redis queues that : `ydl_api_ng` and `ydl_api_ng_slow`.

The `ydl_api_ng_slow` is processed by an unique worker. It's designed to queue downloads to :
- avoid throttle from websites 
- don't overcharge your connection / disk

You can add more redis queues or customize existing ones by editing the `params/workers.ini` file. All redis queues workers names must starts with `worker_`.

```
[program:worker_ydl_api_ng] -> Real redis queue name : ydl_api_ng
```

The first queue in the file will be the default.

## Usage in presets
Example of preset : 
```
[preset:ARCHIVE]
_redis_queue = ydl_api_ng_slow
; Set redis TTL specifically for this preset
_redis_ttl = 31400
```

## Usage in api
Example :
```shell
# Get active downloads in all redis queues
GET http://localhost:5011/active_downloads

# Get active downloads is a given queue
GET http://localhost:5011/active_downloads?redis_queue=ydl_api_ng_slow

#  This queue doesn't exists, send a 404 error
GET http://localhost:5011/active_downloads?redis_queue=ydl_api_ng_live
```

# iOS shortcut

There is now an iOS shortcut you can find [here](https://www.icloud.com/shortcuts/deb4fea950ee436daf9a1f668a55add4).

If the shortcut is launched outside the share interface, it uses the content of the clipboard.

## Shortcut configuration

```
host : download url (with endpoint)
token : the user token
preset_selection : if true, asks the preset to use. If false, use the default preset
presets : a map with all the presets 
default_preset : the default preset if preset_selection is false
```

# Contributing

- Found a bug ? Need an improvement ? Need help ? Open a ticket !
- Found a typo in documentation ? That's normal ! I'm French. Don't hesitate to contact me if you don't understand a
  sentence or if there are mistakes.