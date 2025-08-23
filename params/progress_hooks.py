import logging
import sys

import humanize

sys.path.insert(1, 'params/hooks_utils/')


###
# ydl_opts contains all the informations of the selected preset
# download_manager contains all the processed informations about the download
# config_manager contains all the parameters of the application
# download contains the standard youtube-dlp object for progress hooks
###

def handler(ydl_opts, download_manager, config_manager, download, **kwargs):
    if download.get('status') == 'finished':
        logging.getLogger('progress_hooks').debug(f'[SUCCESS][preset:{ydl_opts.get("_name")}] - {download_manager.url} -> {download.get("filename")} ({humanize.naturalsize(download.get("total_bytes"), binary=True)})')
    if download.get('status') == 'error':
        logging.getLogger('progress_hooks').error(f'[FAILED][preset:{ydl_opts.get("_name")}] - {download_manager.url}')
