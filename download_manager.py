import copy
import functools
import http.cookiejar
import logging
import optparse
from urllib.parse import urlparse
import os

import yt_dlp as ydl
from redis import Redis
from rq import Queue
from rq.job import Job

import config_manager

try:
    from params import progress_hooks
except ImportError as e:
    logging.warning(e)
    from setup import progress_hooks

try:
    from params import postprocessor_hooks
except ImportError as e:
    logging.warning(e)
    from setup import postprocessor_hooks

try:
    from params import ydl_api_hooks
except ImportError as e:
    logging.warning(e)
    from setup import ydl_api_hooks

from rq import get_current_job
import inspect
import ydl_api_ng_utils as ydl_utils

class DownloadManager:
    __cm = None

    def __init__(self, config_manager, url, presets_string, user_token, post_body=None, ignore_post_security=False,
                 **kwargs):
        logging.getLogger('download_manager').info(
            f'Init download - user_token: {user_token} - presets: {presets_string} - url :{url} ')

        self.request_id = None if kwargs.get('request_id') is None else kwargs.get('request_id')

        self.programmation = None if kwargs.get('programmation') is None else kwargs.get('programmation')
        self.programmation_id = None if kwargs.get('programmation_id') is None else kwargs.get('programmation_id')
        self.programmation_date = None if kwargs.get('programmation_date') is None else kwargs.get('programmation_date')
        self.programmation_end_date = None if kwargs.get('programmation_end_date') is None else kwargs.get(
            'programmation_end_date')

        self.presets_string = presets_string
        self.presets = []

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

        self.info_dict = None

        is_from_playlist = self.check_if_from_playlist()
        self.is_from_playlist = is_from_playlist if is_from_playlist is not None else False

        is_video = self.check_if_video()
        self.is_video = is_video if is_video is not None else False

        self.enable_redis = self.__cm.get_app_params().get('_enable_redis')

        self.ignore_post_security = ignore_post_security

        self.relaunch_failed_mode = kwargs.get('relaunch_failed_mode') if kwargs.get(
            'relaunch_failed_mode') is not None else None

        self.extra_parameters = None

        if post_body is not None:
            self.extra_parameters = post_body.get('extra_parameters')

            if post_body.get('presets') is not None and len(post_body.get('presets')) > 0:
                self.get_presets_from_post_request(post_body.get('presets'))
        else:
            self.get_presets_objects(presets_string)

        self.simulate_all_downloads()

    def simulate_all_downloads(self):
        for preset in self.presets:
            check_result = self.simulate_download(preset)
            if check_result is False:
                self.failed_checks = self.failed_checks + 1
                logging.getLogger('download_manager').error(
                    f'Checking url with preset {preset.get("_name")} => check failed')
            elif check_result is None:
                self.passed_checks = self.passed_checks + 1
                logging.getLogger('download_manager').info(
                    f'Checking url with preset {preset.get("_name")} => check ignored')
            else:
                self.passed_checks = self.passed_checks + 1
                logging.getLogger('download_manager').info(
                    f'Checking url with preset {preset.get("_name")} => check passed')

            preset.append('__is_video', self.is_video)
            preset.append('__is_playlist', self.is_from_playlist)

    def transform_post_preset_as_object(self, preset):
        temp_object = config_manager.SectionConfig()
        if preset.get('_name') is not None:
            temp_object.append('_name', preset.get('_name'))
        else:
            temp_object.append('_name', 'POST_REQUEST')

        for key in preset:
            temp_object.append(key, preset[key])

        return temp_object

    def get_presets_from_post_request(self, presets):
        default_preset = self.get_preset_for_user(self.__cm.get_preset_params('DEFAULT'))
        default_preset.append('_default', True)

        if presets is None:
            self.presets.append(default_preset)
            return self.presets

        config_objects_mapping = {'_preset': self.__cm.get_preset_params,
                                  '_template': self.__cm.get_template_params,
                                  '_location': self.__cm.get_location_params,
                                  '_auth': self.__cm.get_auth_params,
                                  '_site': self.__cm.get_site_params,
                                  '_user': None}

        for preset in presets:
            preset_object = self.transform_post_preset_as_object(preset)

            try:
                cli_preset = self.transform_post_preset_as_object(ydl_utils.cli_to_api(preset.get('_cli'))) if preset.get(
                '_cli') is not None else None
            except optparse.OptParseError as e:
                cli_preset = None
                error_message = ': '.join(e.msg.split(': ')[2:]).removesuffix('\n')
                preset_object.append('_error', error_message)
                logging.getLogger('download_manager').error(f'error during _cli expansion : {error_message}')

            field_to_remove = ['paths', 'outtmpl', '_when_playlist', '_when_live']
            if not self.__cm.get_app_params().get('_allow_dangerous_post_requests') and not self.ignore_post_security:
                for field in field_to_remove:
                    if cli_preset is not None:
                        cli_preset.delete(field)
                    preset_object.delete(field)

            for param in preset:
                if param in config_objects_mapping:
                    self.__cm.merge_configs_object(config_objects_mapping.get(param)(preset.get(param)), preset_object,
                                                   override=False)

                if param == '_cli':
                    self.__cm.merge_configs_object(cli_preset, preset_object,
                                                   override=False)

            if self.ignore_post_security is False:
                if preset_object.get('_ignore_default_preset') is None or (
                        preset_object.get('_ignore_default_preset') is not None and not preset_object.get(
                    '_ignore_default_preset')):
                    self.__cm.merge_configs_object(self.__cm.get_preset_params('DEFAULT'), preset_object,
                                                   override=False)

                self.__cm.merge_configs_object(self.user, preset_object, override=True)

                if preset_object.get('_ignore_site_config') is None or (
                        preset_object.get('_ignore_site_config') is not None and not preset_object.get(
                    '_ignore_site_config')):
                    self.__cm.merge_configs_object(self.site, preset_object, override=True)

                if preset_object.get('paths') is None:
                    preset_object.append('paths', {'home': './downloads'})
                    self.__cm.merge_configs_object(self.__cm.get_location_params('DEFAULT'), preset_object,
                                                   override=True)

                if preset_object.get('outtmpl') is None:
                    self.__cm.merge_configs_object(self.__cm.get_template_params('DEFAULT'), preset_object,
                                                   override=True)

            self.presets.append(preset_object)

    # Retrieve parameters objects from api string presets
    def get_presets_objects(self, presets):
        default_preset = self.get_preset_for_user(self.__cm.get_preset_params('DEFAULT'))
        default_preset.append('_default', True)

        if presets is None:
            self.presets.append(default_preset)
            return self.presets

        # Remove duplicated presets
        presets = list(dict.fromkeys(presets))

        for preset in presets:
            found_preset = self.__cm.get_preset_params(preset)

            if found_preset is not None:
                found_preset.append('_default', False)
                self.presets.append(self.get_preset_for_user(found_preset))

                self.presets_found = self.presets_found + 1
            else:
                self.presets_not_found = self.presets_not_found + 1

        # Add default preset if not valid preset found
        if len(self.presets) == 0:
            self.presets.append(self.get_preset_for_user(default_preset))
            self.no_preset_found = True

        return self.presets

    def check_if_from_playlist(self):
        if self.site is None or self.site.get('_playlist_indicators') is None:
            return None

        for playlist_indicator in self.site.get('_playlist_indicators'):
            if self.url.find(playlist_indicator) != -1:
                return True

        return False

    def check_if_video(self):
        if self.site is None or self.site.get('_video_indicators') is None:
            return None

        for video_indicator in self.site.get('_video_indicators'):
            if self.url.find(video_indicator) != -1:
                return True

        return False

    def get_site_param_object(self):
        return self.site

    # A playlist should not be cheched
    # A video in a playlist should be checked only if noplaylist = True
    def can_url_be_checked(self, preset):
        if preset.get('_skip_check'):
            return False

        noplaylist_param = preset.get('noplaylist')
        noplaylist_param = noplaylist_param if noplaylist_param is not None else False

        return not self.is_from_playlist or (noplaylist_param and self.is_video)

    def is_user_permitted(self, users_management=None):
        manage_user = self.__cm.get_app_params().get(
            '_enable_users_management') if users_management is None else users_management

        if manage_user:
            if self.user is None:
                return False
            else:
                return self.user
        else:
            return None

    # Extends preset with user informations
    def get_preset_for_user(self, preset):
        logging.getLogger('download_manager').info(f"Added specific configuration for user")
        self.__cm.merge_configs_object(self.user, preset)
        preset = self.add_site_config_to_preset(preset)
        preset.delete('_token')

        return preset

    def add_site_config_to_preset(self, preset):
        logging.getLogger('download_manager').info(f"Added specific configuration for site")
        self.__cm.merge_configs_object(self.site, preset)
        return preset

    def simulate_download(self, preset):
        if self.relaunch_failed_mode is True:
            preset.append('__can_be_checked', True)
            preset.append('__check_result', None)
            return None

        elif not self.can_url_be_checked(preset):
            self.downloads_cannot_be_checked = self.downloads_cannot_be_checked + 1
            self.all_downloads_checked = False

            preset.append('__can_be_checked', False)
            preset.append('__check_result', None)

            when_playlist_options = preset.get('_when_playlist')

            if when_playlist_options is not None:
                for option in when_playlist_options:
                    preset.append(option, when_playlist_options.get(option))

            return None

        self.downloads_can_be_checked = self.downloads_can_be_checked + 1

        ydl_opts = copy.deepcopy(preset)
        ydl_opts.append('simulate', True)
        ydl_opts.append('logger', logging.getLogger('youtube-dlp'))

        if self.request_id is not None:
            ydl_opts.append('cookiefile', f'cookies/{self.request_id}.txt')

        try:
            simulation_result = None
            ydl_opts_info_dicts = copy.deepcopy(ydl_opts)
            # For automatic playlist detection
            ydl_opts_info_dicts.append('noplaylist', True)
            ydl_opts_info_dicts.append('extract_flat', 'in_playlist')

            with ydl.YoutubeDL(ydl_opts_info_dicts.get_all()) as dl:
                info_dict = dl.extract_info(self.url)

                if info_dict is None:
                    simulation_result = False
                    preset.append('__check_exception_message',
                                  'info_dict contains no data, url may be wrong or format is unavailable')
                else:
                    if self.site is None and info_dict.get('extractor') is not None:
                        logging.getLogger('download_manager').info(
                            "Site config applied")
                        self.site = self.__cm.find_site_by_section_name(info_dict.get('extractor').split(':')[0].upper())
                        self.add_site_config_to_preset(preset)

                    self.is_from_playlist = info_dict.get('_type', None) == 'playlist'
                    self.is_video = info_dict.get('_type', None) != 'playlist'

                    preset.append('__is_live', info_dict.get('is_live', False))

                    if info_dict.get('is_live', None) is True:
                        when_live_options = preset.get('_when_live')

                        if when_live_options is not None:
                            for option in when_live_options:
                                preset.append(option, when_live_options.get(option))

                    if self.is_from_playlist:
                        when_playlist_options = preset.get('_when_playlist')

                        if when_playlist_options is not None:
                            for option in when_playlist_options:
                                preset.append(option, when_playlist_options.get(option))

                        self.downloads_cannot_be_checked = self.downloads_cannot_be_checked + 1
                        self.all_downloads_checked = False

                        self.info_dict = info_dict  # playlist = complete info_dict
                        preset.append('__can_be_checked', False)
                        preset.append('__check_result', None)
                    else:
                        field_to_remove = ['formats', 'thumbnails', '_format_sort_fields', 'subtitles',
                                           'automatic_captions', 'http_headers']
                        for field in field_to_remove:
                            info_dict.pop(field, None)

                        self.info_dict = info_dict  # video = reduced info dict
                        preset.append('__check_exception_message', None)


        except Exception as error:
            try:
                os.remove(f'cookies/{self.request_id}.txt')
            except FileNotFoundError:
                pass

            simulation_result = False
            preset.append('__check_exception_message', str(error))

        preset.append('__check_result', simulation_result)

        if simulation_result is False:
            try:
                os.remove(f'cookies/{self.request_id}.txt')
            except FileNotFoundError:
                pass

        return simulation_result

    def find_downloads_in_downloaded_files_list(self, video_id):
        for index, download in enumerate(self.downloaded_files):
            if download.get('info_dict').get('id') == video_id:
                return index
        return None

    def reduce_info_dict(self, download):
        reduced_file = copy.deepcopy(download)

        if self.__cm.get_app_params().get('_skip_info_dict'):
            saved_info = {}

            for field in self.__cm.get_app_params().get('_info_dict_field_retrieve'):
                saved_info[field]=reduced_file.get('info_dict', {}).get(field, None)

            return saved_info
        else:
            return download

    def delete_fields(self, download):
        fields_to_delete = ['ctx_id', '_speed_str', '_total_bytes_str', '_elapsed_str', '_percent_str',
                            '_default_template', 'info_dict', '_total_bytes_estimate_str', '_downloaded_bytes_str',
                            '_eta_str']

        clone = copy.deepcopy(download)
        if self.__cm.get_app_params().get('_skip_info_dict'):
            for field in fields_to_delete:
                try:
                    del clone[field]
                except KeyError:
                    pass
        return clone

    def progress_hooks_proxy(self, download):
        is_in_list = self.find_downloads_in_downloaded_files_list(download.get('info_dict').get('id'))

        # Those attributes makes redis go crazy, dunno why
        download.get('info_dict').pop('http_headers', None)
        for dl_format in download.get('info_dict').get('formats'):
            dl_format.pop('http_headers', None)

        if is_in_list is None:
            self.downloaded_files.append({
                'id' : download.get('info_dict').get('id'),
                'status': download.get('status'),
                'filename' : download.get('info_dict').get('filename'),
                '_filename' : download.get('info_dict').get('filename'),
                'total_bytes' : 0,
                'elapsed' : 0,
                'info_dict': download.get('info_dict'),
                'sub_downloads': {
                    download.get('info_dict').get('format_id'): download
                }
            })
            is_in_list = self.find_downloads_in_downloaded_files_list(download.get('info_dict').get('id'))
        else:
            self.downloaded_files[is_in_list].get('sub_downloads')[download.get('info_dict').get('format_id')] = download
            self.downloaded_files[is_in_list]['info_dict'] = download.get('info_dict')

        if self.enable_redis is None or self.enable_redis is False:
            return

        if get_current_job().meta.get('downloaded_files') is None:
            get_current_job().meta['downloaded_files'] = []

        try:
            get_current_job().meta['downloaded_files'][is_in_list]
        except IndexError:
            get_current_job().meta['downloaded_files'].append(copy.deepcopy(self.downloaded_files[is_in_list]))

        get_current_job().meta['downloaded_files'][is_in_list]['info_dict'] = self.reduce_info_dict(download)

        format_id = download.get('info_dict').get('format_id')
        get_current_job().meta['downloaded_files'][is_in_list].get('sub_downloads')[format_id] = self.delete_fields(download)
        get_current_job().save_meta()

    def postprocessor_hooks_proxy(self, download):
        is_in_list = self.find_downloads_in_downloaded_files_list(download.get('info_dict').get('id'))

        if self.enable_redis is None or self.enable_redis is False:
            return

        if is_in_list is None:
            self.downloaded_files.append({
                'id' : download.get('info_dict').get('id'),
                'status': download.get('status'),
                'filename' : download.get('info_dict').get('filename'),
                '_filename' : download.get('info_dict').get('filename'),
                'total_bytes' : 0,
                'elapsed' : 0,
                'info_dict': download.get('info_dict'),
                'sub_downloads': {}
            })

            is_in_list = self.find_downloads_in_downloaded_files_list(download.get('info_dict').get('id'))

        if is_in_list is not None and (download.get('status') == 'finished' or download.get('status') == 'error'):
            current_download = self.downloaded_files[is_in_list]
            if get_current_job().meta.get('downloaded_files') is None:
                get_current_job().meta['downloaded_files'] = []

            try:
                get_current_job().meta['downloaded_files'][is_in_list]
            except IndexError:
                get_current_job().meta['downloaded_files'].append(copy.deepcopy(self.downloaded_files[is_in_list]))

            current_download['status'] = download.get('status')

            current_download['total_bytes'] = 0
            current_download['elapsed'] = 0

            sub_downloads = {}
            for format_id, data in current_download.get('sub_downloads').items():
                current_download['total_bytes'] = current_download.get('total_bytes') + data.get('total_bytes')

                if current_download.get('elapsed') is None or data.get('elapsed') is None:
                    current_download['elapsed'] = None
                else:
                    current_download['elapsed'] = current_download.get('elapsed') + data.get('elapsed')

                sub_downloads[format_id] = self.delete_fields(data)

            get_current_job().meta['downloaded_files'][is_in_list] = copy.deepcopy(current_download)
            get_current_job().meta['downloaded_files'][is_in_list]['sub_downloads'] = sub_downloads
            get_current_job().meta['downloaded_files'][is_in_list]['info_dict'] = self.reduce_info_dict(download)
            get_current_job().save_meta()


    def process_download(self, preset):
        if self.__cm.get_app_params().get('_dev_mode'):
            logging.getLogger('download_manager').critical(
                "server in DEV mode, set the _dev_mode at false in the [app] parameters")
            return

        ydl_opts = copy.deepcopy(preset)

        ydl_opts.append('progress_hooks',
                        [functools.partial(self.progress_hooks_proxy),
                         functools.partial(progress_hooks.handler, ydl_opts, self, self.get_current_config_manager())])
        ydl_opts.append('postprocessor_hooks',
                        [functools.partial(self.postprocessor_hooks_proxy),
                         functools.partial(postprocessor_hooks.handler, ydl_opts, self, self.get_current_config_manager())])
        ydl_opts.append('logger', logging.getLogger('youtube-dlp'))

        if self.request_id is not None:
            ydl_opts.append('cookiefile', f'cookies/{self.request_id}.txt')

        ydl_api_hooks.pre_download_handler(ydl_opts, self, self.get_current_config_manager())

        if self.enable_redis is not None and self.enable_redis is True:
            redis_queue = self.__cm.redis_queues[0] if preset.get('_redis_queue') is None else preset.get('_redis_queue')

            if redis_queue not in self.__cm.redis_queues:
                logging.getLogger('download_manager').warning(f'Redis queue {redis_queue} doest not exists, fallback to {self.__cm.redis_queues[0]}')
                redis_queue = self.__cm.redis_queues[0]

            queue = Queue(redis_queue, connection=Redis(host=self.__cm.get_app_params().get('_redis_host'),
                                                         port=self.__cm.get_app_params().get('_redis_port')))

            redis_meta = {
                'programmation_id': self.programmation_id,
                'programmation_date': self.programmation_date,
                'programmation_end_date': self.programmation_end_date
            }

            redis_ttl = preset.get('_redis_ttl') if preset.get('_redis_ttl') is not None else self.__cm.get_app_params().get('_redis_ttl')

            redis_id = queue.enqueue(self.send_download_order,
                                     args=[ydl_opts, self],
                                     job_timeout=-1,
                                     result_ttl=redis_ttl,
                                     meta=redis_meta).id

            preset.append('_redis_id', redis_id)
            preset.append('_redis_queue', redis_queue, override=True)
            preset.append('_redis_ttl', redis_ttl, override=True)
        else:
            preset.append('_redis_id', None)
            preset.append('_redis_queue', None, override=True)
            preset.append('_redis_ttl', None, override=True)
            self.send_download_order(ydl_opts, self)

    def send_download_order(self, ydl_opts, dm):
        if self.enable_redis:
            self.get_current_config_manager().init_logger(file_name='downloader.log')

        try:
            with ydl.YoutubeDL(ydl_opts.get_all()) as dl:
                dl.download([self.url])
                ydl_opts.append('__download_exception_message', None)
        except Exception as error:
            ydl_opts.append('__download_exception_message', str(error))

        try:
            os.remove(f'cookies/{self.request_id}.txt')
        except FileNotFoundError:
            pass

        filename_info = None

        if self.enable_redis:
            job = Job.fetch(get_current_job().id, connection=Redis(host=self.__cm.get_app_params().get('_redis_host'),
                                                                   port=self.__cm.get_app_params().get('_redis_port')))
            filename_info = job.meta.get('filename_info')

        if 'filename_info' in inspect.getfullargspec(ydl_api_hooks.post_download_handler).args:
            ydl_api_hooks.post_download_handler(ydl_opts, self, self.get_current_config_manager(),
                                                self.downloaded_files, filename_info=filename_info)
        else:  # retrocompatibility
            ydl_api_hooks.post_download_handler(ydl_opts, self, self.get_current_config_manager(),
                                                self.downloaded_files)

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
    def extract_info(url, **kwargs):
        request_id = None if kwargs.get('request_id') is None else kwargs.get('request_id')

        ydl_opts = {
            'ignoreerrors': True,
            'quiet': True,
            'cookiefile' : f'cookies/{request_id}.txt' if request_id is not None else None
        }

        failed = False

        try:
            with ydl.YoutubeDL(ydl_opts) as dl:
                info = dl.extract_info(url, download=False)

            if info is None :
                info = "Video unavailable"
                failed = True
        except Exception as error:
            info = str(error)
            failed = True

        try:
            os.remove(f'cookies/{request_id}.txt')
        except FileNotFoundError:
            pass

        return info, failed

    def get_api_status_code(self):
        # Some presets were not found
        if self.presets_not_found > 0 or (self.failed_checks > 0 and self.passed_checks > 0):
            return 206

        # Some downloads can't be checked (playlists)
        if self.downloads_cannot_be_checked > 0:
            return 202

        # No video can be downloaded
        if self.failed_checks == self.downloads_can_be_checked and self.downloads_cannot_be_checked == 0:
            logging.getLogger('download_manager').error(f'Not downloadable with presets : {self.presets_string} : {self.url}')
            return 400

        return 200

    def get_api_return_object(self):
        presets_display = []
        for preset in self.presets:
            presets_display.append(self.__cm.sanitize_config_object_section(preset).get_all())

        if self.programmation is not None:
            self.programmation['user_token'] = 'censored'

        return {
            'status_code': self.get_api_status_code(),
            'url': self.url,
            'url_hostname': self.site_hostname,
            'no_preset_found': self.no_preset_found,
            'presets_found': self.presets_found,
            'presets_not_found': self.presets_not_found,
            'all_downloads_checked': self.all_downloads_checked,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'downloads_can_be_checked': self.downloads_can_be_checked,
            'downloads_cannot_be_checked': self.downloads_cannot_be_checked,
            'ignore_post_security': self.ignore_post_security,
            'relaunch_failed_mode': self.relaunch_failed_mode,
            'info_dict' : self.info_dict,
            'downloads': presets_display,
            'programmation' : self.programmation,
            'programmation_date' : self.programmation_date,
            'programmation_end_date' : self.programmation_end_date,
            'extra_parameters' : self.extra_parameters
        }

    def get_current_config_manager(self):
        return self.__cm

    @staticmethod
    def get_downloaded_files_info(downloaded_files_list):
        downloads_state = {}

        for download in downloaded_files_list:
            video_id = download.get('info_dict').get('id')

            if downloads_state.get(video_id) is None:
                downloads_state[video_id] = {
                    'finished_downloads': 0,
                    'error_downloads': 0,
                    'file_size': 0,
                    'downloads': []
                }

            if download.get('status') == 'finished':
                downloads_state.get(video_id)['finished_downloads'] = downloads_state.get(video_id).get(
                    'finished_downloads') + 1
                downloads_state.get(video_id)['file_size'] = downloads_state.get(video_id).get(
                    'file_size') + download.get('total_bytes')
            else:
                downloads_state.get(video_id)['error_downloads'] = downloads_state.get(video_id).get(
                    'error_downloads') + 1

            downloads_state.get(video_id).get('downloads').append(download)
        return downloads_state
