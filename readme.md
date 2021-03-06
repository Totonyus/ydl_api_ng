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

### By command line

```shell
docker run -p 5011:80 totonyus/ydl_api # don't forget to map the folders
```

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

You can download the video you want by providing the parameters directly in a post request

```shell
POST http://localhost:5011/download?url=https://www.youtube.com/watch?v=wV4wepiucf4&token=dad_super_password
Content-Type: application/json

{
  "presets": [
    {
      "_ignore_site_config": false, # (optional, default : false) if true, will not load parameters from site detection
      "_ignore_default_preset": false, # (optional, default : false) if true, will not expand default preset
      # You can expand parameters
      "_preset" : "AUDIO"
      "_location" : "AUDIO"
      # just put below your standard youtube-dlp options
      "format" : "best[height=360]/bestvideo[height=360]+bestaudio/best"
    }
  ]
}
```

Reminder if you want to expand a preset : all presets automatically expand the `DEFAULT` preset. Basically, expand a
preset with `_preset` means `_ignore_default_preset`can't be true.

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

The process management system only works you livestreams

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

## Responses status

* `401` : User is not permitted

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