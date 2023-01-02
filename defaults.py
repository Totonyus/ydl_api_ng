app_defaults = {
    '_allow_dangerous_post_requests': False,
    '_api_route_active_downloads': '/active_downloads',
    '_api_route_download': '/download',
    '_api_route_queue': '/queue',
    '_api_route_extract_info': '/extract_info',
    '_api_route_info': '/info',
    '_api_route_programmation': '/programmation',
    '_enable_users_management': False,
    '_listen_ip': '0.0.0.0',
    '_listen_port': 80,
    '_log_backups': 7,
    '_log_level': 20,
    '_programmation_interval': 60,
    '_unit_test': True,
    '_enable_redis': True,
    '_redis_ttl': 3600,
    '_redis_host': 'ydl_api_ng',
    '_redis_port': 6379
}

programmation_object_default = {
    'id': None,
    'url': None,
    'user_token': None,
    'enabled': True,
    'planning': {
        'recording_start_date': None,
        'recording_duration': None,
        'recording_stops_at_end': False,
        'recording_restarts_during_duration': True,

        'recurrence_cron': None,
        'recurrence_start_date': None,
        'recurrence_end_date': None,
    },
    'presets': None
}
