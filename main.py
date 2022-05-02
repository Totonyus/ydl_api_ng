from urllib.parse import unquote

import uvicorn
import yt_dlp.version
from fastapi import BackgroundTasks, FastAPI, Response, Body

import config_manager
import download_manager
import process_utils
import os

__cm = config_manager.ConfigManager()
__pu = process_utils.ProcessUtils(__cm)

app = FastAPI()
enable_redis = False if __cm.get_app_params().get('_enable_redis') is not True else True


###
# Application
###

@app.get(__cm.get_app_params().get('_api_route_info'))
async def info_request(response: Response, token=None):
    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return {
        'ydl_engine': 'yt-dlp',
        'ydl_version': yt_dlp.version.__version__,
        'ydl_git_head': yt_dlp.version.RELEASE_GIT_HEAD,
        'ydl_api_ng_container_date': os.environ.get('DATE'),
        'ydl_api_ng_branch': os.environ.get('GIT_BRANCH'),
        'ydl_api_ng_revision': os.environ.get('GIT_REVISION'),
        'processed_config': {
            'meta_keys': __cm.get_keys_meta(),
            'app_config': __cm.sanitize_config_object(__cm.get_app_params_object()),
            'user_config': __cm.sanitize_config_object(__cm.get_all_users_params()),
            'preset_config': __cm.sanitize_config_object(__cm.get_all_preset_params()),
            'site_config': __cm.sanitize_config_object(__cm.get_all_sites_params()),
            'auth_config': __cm.sanitize_config_object(__cm.get_all_auth_params()),
            'location_config': __cm.sanitize_config_object(__cm.get_all_locations_params()),
            'template_config': __cm.sanitize_config_object(__cm.get_all_templates_params()),
        }
    }


###
# Download
###

@app.get(__cm.get_app_params().get('_api_route_download'))
async def download_request(response: Response, background_tasks: BackgroundTasks, url, token=None, presets=None):
    param_url = unquote(url)
    param_token = unquote(token) if token is not None else None
    param_presets = unquote(presets).split(',') if presets is not None else None

    dm = download_manager.DownloadManager(__cm, param_url, param_presets, param_token)

    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    if param_url == '':
        response.status_code = 400
        return

    response.status_code = dm.get_api_status_code()

    if response.status_code != 400:
        if enable_redis:
            dm.process_downloads()
        else:
            background_tasks.add_task(dm.process_downloads)

    return dm.get_api_return_object()


@app.post(__cm.get_app_params().get('_api_route_download'))
async def download_request(response: Response, background_tasks: BackgroundTasks, url, body=Body(...), token=None):
    param_url = unquote(url)
    param_token = unquote(token) if token is not None else None

    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    dm = download_manager.DownloadManager(__cm, param_url, None, param_token, body)
    response.status_code = dm.get_api_status_code()

    if response.status_code != 400:
        if enable_redis:
            dm.process_downloads()
        else:
            background_tasks.add_task(dm.process_downloads)

    return dm.get_api_return_object()


@app.get(f"{__cm.get_app_params().get('_api_route_download')}/{'{redis_id}'}/failed")
async def relaunch_failed_download(response: Response, redis_id, token=None):
    if not enable_redis:
        response.status_code = 409
        return "Redis management is disabled"

    param_token = unquote(token) if token is not None else None

    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    response.status_code, return_object = __pu.relaunch_failed(redis_id, token)
    return return_object


@app.get(f"{__cm.get_app_params().get('_api_route_download')}/{'{redis_id}'}")
async def relaunch_download(response: Response, redis_id, token=None):
    if not enable_redis:
        response.status_code = 409
        return "Redis management is disabled"

    param_token = unquote(token) if token is not None else None

    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    response.status_code, return_object = __pu.relaunch_job(redis_id, token)
    return return_object


###
# Video
###

@app.get(__cm.get_app_params().get('_api_route_extract_info'))
async def extract_info_request(response: Response, url, token=None):
    param_url = unquote(url)
    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return download_manager.DownloadManager.extract_info(param_url)


###
# Process
###
@app.get(__cm.get_app_params().get('_api_route_active_downloads'))
async def active_downloads_request(response: Response, token=None):
    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return __pu.get_active_downloads_list()


@app.get(f"{__cm.get_app_params().get('_api_route_active_downloads')}/terminate/{'{pid}'}")
async def terminate_active_download_request(response: Response, pid, token=None):
    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return_status = __pu.terminate_active_download(unquote(pid))

    if return_status is None:
        response.status_code = 404
        return

    return return_status


@app.get(f"{__cm.get_app_params().get('_api_route_active_downloads')}/terminate")
async def terminate_all_active_downloads_request(response: Response, token=None):
    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return __pu.terminate_all_active_downloads()


@app.get(f"{__cm.get_app_params().get('_api_route_queue')}")
async def active_downloads_request(response: Response, token=None):
    if not enable_redis:
        response.status_code = 409
        return "Redis management is disabled"

    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return __pu.get_queue_content('all')


@app.delete(f"{__cm.get_app_params().get('_api_route_queue')}")
async def clear_registries(response: Response, token=None):
    if not enable_redis:
        response.status_code = 409
        return "Redis management is disabled"

    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return __pu.clear_all_but_pending_and_started()


@app.get(f"{__cm.get_app_params().get('_api_route_queue')}/{'{registry}'}")
async def active_downloads_request(response: Response, registry, token=None):
    if not enable_redis:
        response.status_code = 409
        return "Redis management is disabled"

    param_token = unquote(token) if token is not None else None
    user = __cm.is_user_permitted_by_token(param_token)

    if user is False:
        response.status_code = 401
        return

    return __pu.get_queue_content(registry)


uvicorn.run(app, host=__cm.get_app_params().get('_listen_ip'), port=__cm.get_app_params().get('_listen_port'), log_config=None)
