import copy
import functools
import logging
from urllib.parse import urlparse

import yt_dlp as ydl

from params import progress_hooks, postprocessor_hooks, ydl_api_hooks


class DownloadManager:
    __cm = None

    def __init__(self, config_manager, url, presets, user_token):
        logging.getLogger('download_manager').info(f'Init download - user_token: {user_token} - presets: {presets} - url :{url} ')

        self.presets = []
        self.presets_display = []

        self.all_downloads_checked = True
        self.no_preset_found = False

        self.presets_not_found = 0
        self.presets_found = 0

        self.downloads_cannot_be_checked = 0
        self.downloads_can_be_checked = 0

        self.failed_checks = 0
        self.passed_checks = 0

        self.downloaded_files = []

        self.__cm = config_manager
        self.url = url
        self.site_hostname = urlparse(url).hostname
        self.site = self.__cm.get_site_params(self.site_hostname)
        self.user = self.__cm.get_user_param_by_token(user_token)
        self.get_presets_objects(presets)
        self.simulate_all_downloads()

    def simulate_all_downloads(self):
        for preset in self.presets:
            check_result = self.simulate_download(preset)
            if check_result is False:
                self.failed_checks = self.failed_checks + 1
                logging.getLogger('download_manager').error(f'Checking url with preset {preset.get("_name")} => check failed')
            else:
                self.passed_checks = self.passed_checks + 1
                logging.getLogger('download_manager').info(f'Checking url with preset {preset.get("_name")} => check passed')

            preset.append('__is_video', self.is_video())
            preset.append('__is_playlist', self.is_from_playlist())

    # Retrieve parameters objects from api string presets
    def get_presets_objects(self, presets):
        default_preset = self.get_preset_for_user(self.__cm.get_preset_params('DEFAULT'))
        default_preset.append('_default', True)

        if presets is None:
            self.presets.append(default_preset)
            self.presets_display.append(self.__cm.sanitize_config_object_section(default_preset))
            return self.presets

        for preset in presets:
            found_preset = self.__cm.get_preset_params(preset)

            if found_preset is not None:
                found_preset.append('_default', False)
                self.presets.append(self.get_preset_for_user(found_preset))
                self.presets_display.append(self.__cm.sanitize_config_object_section(found_preset))

                self.presets_found = self.presets_found + 1
            else:
                self.presets_not_found = self.presets_not_found + 1

        # Add default preset if not valid preset found
        if len(self.presets) == 0:
            self.presets.append(self.get_preset_for_user(default_preset))
            self.presets_display.append(self.__cm.sanitize_config_object_section(default_preset))
            self.no_preset_found = True

        return self.presets

    def is_from_playlist(self):
        if self.site is None or self.site.get('_playlist_indicators') is None:
            return None

        for playlist_indicator in self.site.get('_playlist_indicators'):
            if self.url.find(playlist_indicator) != -1:
                return True

        return False

    def is_video(self):
        if self.site is None or self.site.get('_video_indicators') is None:
            return None

        for video_indicator in self.site.get('_video_indicators'):
            if self.url.find(video_indicator) != -1:
                return True

        return False

    def get_site_param_object(self):
        return self.site

    # A playlist should not be cheched
    # A video in a playlist should checked only if noplaylist = True
    def can_url_be_checked(self, preset):
        noplaylist_param = preset.get('noplaylist')

        if noplaylist_param is None:
            noplaylist_param = False

        is_from_playlist = self.is_from_playlist()
        is_video = self.is_video()

        return_value = True
        if is_from_playlist is None and is_video is None:
            return_value = True

        if not noplaylist_param and is_from_playlist:
            return_value = False

        if noplaylist_param and is_from_playlist and not is_video:
            return_value = False

        return return_value

    def is_user_permitted(self, users_management=None):
        manage_user = self.__cm.get_app_params().get('_enable_users_management') if users_management is None else users_management

        if manage_user:
            if self.user is None:
                return False
            else:
                return self.user
        else:
            return None

    # Extends preset with user informations
    def get_preset_for_user(self, preset):
        self.__cm.merge_configs_object(self.user, preset)
        self.__cm.merge_configs_object(self.site, preset)
        preset.delete('_token')

        return preset

    def simulate_download(self, preset):
        if not self.can_url_be_checked(preset):
            self.downloads_cannot_be_checked = self.downloads_cannot_be_checked + 1
            self.all_downloads_checked = False

            preset.append('__can_be_checked', False)
            preset.append('__check_result', None)

            return None

        self.downloads_can_be_checked = self.downloads_can_be_checked + 1

        ydl_opts = copy.deepcopy(preset)
        ydl_opts.append('simulate', True)
        ydl_opts.append('logger', logging.getLogger('youtube-dlp'))

        ydl_opts = ydl_opts.get_all()

        with ydl.YoutubeDL(ydl_opts) as dl:
            simulation_result = dl.download([self.url]) == 0

        preset.append('__can_be_checked', True)
        preset.append('__check_result', simulation_result)

        return simulation_result

    def progress_hooks_proxy(self, download):
        if download.get('status') == 'finished':
            self.downloaded_files.append(download)

    def process_download(self, preset):
        if self.__cm.get_app_params().get('_dev_mode'):
            logging.getLogger('download_manager').critical("server in DEV mode, set the _dev_mode at false in the [app] parameters")
            return

        ydl_opts = copy.deepcopy(preset)

        ydl_opts.append('progress_hooks', [functools.partial(progress_hooks.handler, ydl_opts, self, self.__cm), functools.partial(self.progress_hooks_proxy)])
        ydl_opts.append('postprocessor_hooks', [functools.partial(postprocessor_hooks.handler, ydl_opts, self, self.__cm)])
        ydl_opts.append('logger', logging.getLogger('youtube-dlp'))

        ydl_api_hooks.pre_download_handler(ydl_opts, self, self.__cm)

        with ydl.YoutubeDL(ydl_opts.get_all()) as dl:
            download_result = dl.download([self.url]) == 0

            ydl_api_hooks.post_download_handler(ydl_opts, self, self.__cm, self.downloaded_files)

        return download_result

    def process_downloads(self):
        for preset in self.presets:
            self.process_download(preset)

    def flush_presets(self):
        self.url = None
        self.presets = []
        self.user = None
        self.site = None

        self.all_downloads_checked = True
        self.no_preset_found = False

        self.presets_not_found = 0
        self.presets_found = 0

        self.downloads_cannot_be_checked = 0
        self.downloads_can_be_checked = 0

        self.failed_checks = 0
        self.passed_checks = 0

    @staticmethod
    def extract_info(url):
        ydl_opts = {
            'ignoreerrors': True
        }

        with ydl.YoutubeDL(ydl_opts) as dl:
            informations = dl.extract_info(url, download=False)

        return informations
