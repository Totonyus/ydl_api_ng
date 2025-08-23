import sys

sys.path.insert(1, 'params/hooks_utils/')


###
# ydl_opts contains all the informations of the selected preset
# download_manager contains all the processed informations about the download
# config_manager contains all the parameters of the application
# download contains the standard youtube-dlp object for postprocessor hooks
###

def handler(ydl_opts, download_manager, config_manager, download, **kwargs):
    if download.get('status') == 'finished':
        return
    if download.get('status') == 'error':
        return
