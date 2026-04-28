# Redis queues

If redis is enabled, there is by default two redis queues : `ydl_api_ng` and `ydl_api_ng_slow`.

The `ydl_api_ng_slow` is processed by an unique worker. It's designed to queue downloads to :

- avoid throttle from websites
- don't overcharge your connection / disk

You can add more redis queues or customize existing by putting and customizing the [workers.ini](../params/workers.ini)
file in your `params/` directory. All redis queues workers names must starts with `worker_`.

```
[program:worker_ydl_api_ng] -> Real redis queue name : ydl_api_ng
```

The first queue in the file will be the default one.

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