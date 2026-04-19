# Installation using Docker/Podman

Image on [Docker Hub](https://hub.docker.com/r/totonyus/ydl_api_ng)
or [Github Registry](https://github.com/Totonyus/ydl_api_ng/pkgs/container/ydl_api_ng)

You can use `Podman` instead of `Docker`.

The parameters file will be generated in the `/app/params/` volume on the first launch of the container.

## Docker-compose

Just copy the `[docker-compose.yml](../docker-compose.yml)` file where you want and launch this command :

```shell
docker compose pull # pull the latest image
docker compose up # to start the container
docker compose stop # to start the container
docker compose down # to destroy the container
```

Note that additional informations are present in the `[docker-compose.yml](../docker-compose.yml)` file

## Volumes mapping

Volumes you could want to map :

- `/app/downloads/` : where files will be downloaded
- `/app/params/` : where the parameters files will be stored (`params.ini` and the hooks files)
- `/app/logs` : application logging
- `/app/persistant_cookies` : where you can store all your [cookies](005_Cookies.md)

## Force yt-dlp version:

HIGHLY DISCOURAGED but may be useful when there is a blocking bug in new yt-dlp release : you can force the version of
`yt-dlp` by adding this environment parameter in your compose file.

```
FORCE_YTDLP_VERSION=2022.11.11
```

## UID and GID

The default user used in the container is `1000:1000`. You can edit those by changing the environment vars `UID`
and `GID` in the `docker-compose.yml` or in the `docker run` command.

The user must be root (`UID=0` and `GID=0`) or match the owner of the download repository.

To know your `UID` and `GID`, simply run this command with the right user or check your `/etc/passwd` file.

```shell
echo $UID $GID
```

# Next step ?

Check how to [configure](100_Configuration.md) your instance then set up
the [userscript](002_Installation_userscript.md)