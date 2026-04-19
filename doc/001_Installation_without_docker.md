# Installation without Docker/Podman

Note : I highly recommend using the container

## Requirements

* Installation with distribution package manager (`apt`, `yum`, ...) : `python3`, `python3-pip`, `ffmpeg`

```shell
pip3 install -r pip_requirements
``` 

## Download this repo

Download the latest release :

```shell
wget https://github.com/Totonyus/ydl_api_ng/archive/master.zip
```

Then unzip the file and rename the unzipped folder : (note you can use `unzip -d %your_path%` to specify where you want
to unzip the file )

```shell
unzip master.zip; mv ydl_api_ng-main ydl_api_ng
```

## Modify listening port

The api listen by default on the port `80`. It's perfect for docker use but not really a good idea for a bare metal
user. Set the port you want in the [params.ini](../params/params.ini) file.

## Install as daemon

Just fill the [ydl_api_ng.service](../ydl_api_ng.service) file and move it in `/usr/lib/systemd/system/` for `systemd` linux.

```shell
mv ydl_api.service /usr/lib/systemd/system/
```

You can change the name of the service by changing the name of the file.

Then (you must run this command every time you change the service file) :

```shell
systemctl daemon-reload
```

Usage :

```shell
systemctl start ydl_api_ng
systemctl stop ydl_api_ng
systemctl enable ydl_api_ng # start at boot
systemctl disable ydl_api_ng # don't start at boot
```

# Next step ?

Check how to [configure](100_Configuration.md) your instance then set up
the [userscript](002_Installation_userscript.md)