![](https://img.shields.io/github/stars/totonyys/ydl_api_ng)
![](https://img.shields.io/docker/pulls/totonyys/ydl_api_ng)

# What is ydl_api_ng ?

`ydl_api_ng` is a webserver you can interact with via a `REST API` to perform downloads directly on your server
using [yt-dlp](https://github.com/yt-dlp/yt-dlp)

The application is meant to cover a large variety of use cases.

# Features

- Suitable for power users of `yt-dlp` but easy to use for beginners
- Easy to setup : the default configuration will allow you to use `ydl_api_ng` without further modification
- A userscript to easily launch downloads from your browser
- An iOS shortcut to send a download order from your device
- Download from any website supported by yt-dlp ([list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md))
- Hooks you can customize to extend features to use downloaded videos in your workflow

## For container version only :

- A full installation of `yt-dlp` with all addons needed to make it work at full potential
- Mostly no need to maintain manually this app to keep up with `yt-dlp` updates
- A programmation function to schedule downloads
- Queue management to monitor and control your downloads
- Multiple queues to manage your ressources

![002_installation_userscript.jpg](doc/002_installation_userscript.jpg)

# Engagements

- I'll always do my best to not introduce breaking changes and maintain compatibility
- I built `ydl_api_ng` for my usage and I use it a lot so I try to always test extensively changes I make

# Documentation

All documentation can be found in the [doc](docs/) folder

Quick start :

- Installation [with docker](doc/000_Installation_docker.md) or [without docker](doc/001_Installation_without_docker.md)
- User script [installation](doc/002_Installation_userscript.md) or iOS shortcut [usage](doc/003_IOS_shortcut.md)
- Configuration [guide](doc/100_Configuration.md)
- Features API usage :
    - [download](doc/200_API_download.md)
    - [queue management](doc/210_API_queue_management.md)
    - [programmation](doc/220_API_programmation.md)
    - [misc](doc/230_API_utils.md)
- A lot of [requests examples](requests.http)
- A [params.ini](params/params.sample.ini) example file with every option explained

# 🤖 AI usage disclaimer

No AI has been harmed during the development and I don't plan to start using AI. AI contributions are **not** welcome.

# Contributing

- Found a bug ? Need an improvement ? Need help ? Need a feature ? Open a ticket !
- Found a typo in documentation ? That's normal ! I'm French (sorry about that). Don't hesitate to contact me if you
  don't understand a sentence or if there are mistakes.