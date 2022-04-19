import logging
import sys

import humanize

sys.path.insert(1, 'params/hooks_utils/')


###
# ydl_opts contains all the informations of the selected preset
# download_manager contains all the processed informations about the download
# config_manager contains all the parameters of the application
# downloads is a list of youtube-dlp stadart ojbects for progress_hooks
###

# Called just before preset effective download
def pre_download_handler(ydl_opts, download_manager, config_manager):
    logging.getLogger('pre_download_hooks').info(f'Downloading {download_manager.url} with preset {ydl_opts.get("_name")} in {ydl_opts.get("outtmpl")}')
    pass


# Called after all files of the preset are downloaded
def post_download_handler(ydl_opts, download_manager, config_manager, downloads):
    downloads_state = {}

    for download in downloads:
        video_id = download.get('info_dict').get('id')

        if downloads_state.get(video_id) is None:
            downloads_state[video_id] = {
                'finished_downloads': 0,
                'error_downloads': 0,
                'file_size': 0,
                'downloads': []
            }

        if download.get('status') == 'finished':
            downloads_state.get(video_id)['finished_downloads'] = downloads_state.get(video_id).get('finished_downloads') + 1
            downloads_state.get(video_id)['file_size'] = downloads_state.get(video_id).get('file_size') + download.get('total_bytes')
        else:
            downloads_state.get(video_id)['error_downloads'] = downloads_state.get(video_id).get('error_downloads') + 1

        downloads_state.get(video_id).get('downloads').append(download)

    logging.getLogger('post_download_hooks').info(f'[preset:{ydl_opts.get("_name")}] - {download_manager.url} :  download finished')

    for video_id in downloads_state:
        download_object = downloads_state.get(video_id)

        if download_object.get('finished_downloads') != 0 and download_object.get('error_downloads') != 0:
            logging.getLogger('post_download_hooks').error(f'[FAILED][preset:{ydl_opts.get("_name")}] - {download_object.get("downloads")[0].get("info_dict").get("webpage_url")} : Not all part of the files where downloaded')
        elif download_object.get('error_downloads') != 0 and download_object.get('finished_downloads') == 0:
            logging.getLogger('post_download_hooks').error(f'[FAILED][preset:{ydl_opts.get("_name")}] - {download_object.get("downloads")[0].get("info_dict").get("webpage_url")} : No file downloaded')
        elif download_object.get('finished_downloads') != 0 and download_object.get('error_downloads') == 0:
            logging.getLogger('post_download_hooks').info(f'[SUCCESS][preset:{ydl_opts.get("_name")}] - {download_object.get("downloads")[0].get("info_dict").get("webpage_url")} -> {download_object.get("downloads")[0].get("info_dict").get("_filename")} ({humanize.naturalsize(download_object.get("file_size"), binary=True)})')

# Called after a download is terminated
def post_termination_handler(config_manager, filename_info):
    logging.getLogger('post_termination_hooks').info(f'Downloading has been stopped by user : {filename_info.get("full_filename")} ({humanize.naturalsize(filename_info.get("file_size"), binary=True)})')