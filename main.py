import logging
from urllib.parse import unquote

import uvicorn
import yt_dlp.version
from fastapi import BackgroundTasks, FastAPI, Response

import config_manager
import download_manager
import process_utils

__cm = config_manager.ConfigManager()
__pu = process_utils.ProcessUtils(__cm)

app = FastAPI()


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
        'ydl_version': yt_dlp.version.__version__,
        'ydl_git_head': yt_dlp.version.RELEASE_GIT_HEAD,
        'processed_config': {
            'meta_keys': __cm.get_keys_meta(),
            'app_config': __cm.sanitize_config_object(__cm.get_app_params_object()),
            'user_config': __cm.sanitize_config_object(__cm.get_all_users_params()),
            'preset_config': __cm.sanitize_config_object(__cm.get_all_preset_params()),
            'site_config': __cm.sanitize_config_object(__cm.get_all_sites_params()),
            'auth_config': __cm.sanitize_config_object(__cm.get_all_auth_params()),
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
        logging.getLogger('api').error('Url paramater is empty')
        return

    # Some presets were not found
    if dm.presets_not_found > 0:
        response.status_code = 206

    # Some downloads can't be checked (playlists)
    if dm.downloads_cannot_be_checked > 0:
        response.status_code = 202

    # Some presets can't be downloaded
    if dm.failed_checks > 0 and dm.passed_checks > 0:
        response.status_code = 206

    # No video can be downloaded
    if dm.failed_checks == dm.downloads_can_be_checked and dm.downloads_cannot_be_checked == 0:
        logging.getLogger('api').error(f'Not downloadable with presets : {param_presets} : {param_url}')
        response.status_code = 400
    else:
        background_tasks.add_task(dm.process_downloads)

    return {
        'url': param_url,
        'url_hostname': dm.site_hostname,
        'no_preset_found': dm.no_preset_found,
        'presets_found': dm.presets_found,
        'presets_not_found': dm.presets_not_found,
        'all_downloads_checked': dm.all_downloads_checked,
        'passed_checks': dm.passed_checks,
        'failed_checks': dm.failed_checks,
        'downloads_can_be_checked': dm.downloads_can_be_checked,
        'downloads_cannot_be_checked': dm.downloads_cannot_be_checked,
        'downloads': dm.presets_display,
    }


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
        response.status_code = 400
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


uvicorn.run(app, host=__cm.get_app_params().get('_listen_ip'), port=__cm.get_app_params().get('_listen_port'), log_config=None)
