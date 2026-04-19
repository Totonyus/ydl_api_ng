# App configuration

All the configuration of `ydl_api_ng` must be in the `[app]` section of the `params.ini` file.

None of this option is required in the `params.ini` file, the `[app]` section can be empty

| option                         | default value                               | description                                                                                                                                              |
|--------------------------------|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| _api_route_download            | /download                                   | Custumize endpoint                                                                                                                                       |
| _api_route_queue               | /queue                                      | Custumize endpoint                                                                                                                                       |
| _api_route_extract_info        | /extract_info                               | Custumize endpoint                                                                                                                                       |
| _api_route_info                | /info                                       | Custumize endpoint                                                                                                                                       |
| _api_route_active_downloads    | /active_downloads                           | Custumize endpoint                                                                                                                                       |
| _enable_users_management       | true                                        | Require a user token to avoid unauthorized used and to customize a few things according to user                                                          |
| _log_level                     | 20                                          | 0 : NOTSET, 10 : DEBUG, 20 : INFO; 30 : WARNING; 40 : ERROR; 50 : CRITICAL                                                                               |
| _log_backups                   | 7                                           | Number of days of log files to keep                                                                                                                      |
| _listen_port                   | 80                                          | API listen port (do not change for container)                                                                                                            |
| _listen_ip                     | 0.0.0.0                                     | API IP allowed to make requests                                                                                                                          |
| _programmation_interval        | 60                                          | Duration between two programmation daemon checks                                                                                                         |
| _enable_redis                  | true                                        | Enable or not redis (highly recommanded to keep it at True)                                                                                              |
| _redis_ttl                     | 3600                                        | The time a job will stay in queue after finished                                                                                                         |
| _redis_host                    | ydl_api_ng_redis                            | Redis host to use (can be changed to use a distant one)                                                                                                  |
| _redis_port                    | 6379                                        |                                                                                                                                                          |
| _skip_info_dict                | False                                       | `info_dict` can be very heavy, highly recommended to put this option at True (kept at false for compatibility purpose)                                   |
| _info_dict_field_retrieve      | ['id', 'title', 'original_url', 'duration'] | List of fields to keep in `info_dict`                                                                                                                    |
| _allow_dangerous_post_requests | false                                       | FALSE = Removes `outtmpl` and `paths` from post requests to avoir unwanted arbitrary writing (still can set location and template with preset expension) |

## Additional options

You can add any option you what, they will be passed through REST API and will be accessible in hooks.

Example from my personal setup to send notifications from telegram bot:

```
_app_url = ydl.my-domain.me
_telegram_chat_id = my_chat_id
_telegram_bot_key = my_super_secret_telegram_bot_key
```