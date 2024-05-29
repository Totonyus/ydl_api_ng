import copy
import os
import unittest

import requests

import config_manager
import download_manager

from datetime import datetime
from programmation_persistence_manager import ProgrammationPersistenceManager as Ppm
from programmation_class import Programmation


class TestActualParametersFile(unittest.TestCase):
    def test_app(self):
        cm = config_manager.ConfigManager()

        self.assertEqual(5011, cm.get_app_params().get('_listen_port'))
        self.assertIsNot(True, cm.get_app_params().get('_dev_mode'))
        self.assertFalse(cm.get_app_params().get('_enable_users_management'))
        self.assertEqual('0.0.0.0', cm.get_app_params().get('_listen_ip'))
        self.assertFalse(cm.get_app_params().get('_allow_dangerous_post_requests'))
        self.assertFalse(cm.get_app_params().get('_enable_redis'))

    def test_docker_app(self):
        cm = config_manager.ConfigManager('params/params_docker.ini')

        self.assertEqual(80, cm.get_app_params().get('_listen_port'))
        self.assertIsNot(True, cm.get_app_params().get('_dev_mode'))
        self.assertFalse(cm.get_app_params().get('_enable_users_management'))
        self.assertEqual('0.0.0.0', cm.get_app_params().get('_listen_ip'))
        self.assertFalse(cm.get_app_params().get('_allow_dangerous_post_requests'))
        self.assertTrue(cm.get_app_params().get('_enable_redis'))
        self.assertEqual('ydl_api_ng_redis', cm.get_app_params().get('_redis_host'))


class TestConfig(unittest.TestCase):
    config_manager = config_manager.ConfigManager('params/params.sample.ini')

    def test_meta(self):
        self.assertIsInstance(self.config_manager.get_app_params().get('_int_test'), int)
        self.assertIsInstance(self.config_manager.get_app_params().get('_float_test'), float)
        self.assertIsInstance(self.config_manager.get_app_params().get('_bool_test'), bool)
        self.assertIsInstance(self.config_manager.get_app_params().get('_string_test'), str)
        self.assertIsInstance(self.config_manager.get_app_params().get('_array_test'), list)
        self.assertIsInstance(self.config_manager.get_app_params().get('_object_test'), dict)

    def test_sites(self):
        self.assertIsNotNone(self.config_manager.get_site_params('www.youtube.com'))
        self.assertIsNone(self.config_manager.get_site_params('youteu.be'))
        self.assertIsNotNone(self.config_manager.get_site_params('www.youtube.com').get('_hosts'))

    def test_presets(self):
        self.assertIsNotNone(self.config_manager.get_preset_params('HD'))
        self.assertIsNone(self.config_manager.get_preset_params('4K'))
        self.assertIsNotNone(self.config_manager.get_preset_params('HD'))
        self.assertIsNotNone(self.config_manager.get_preset_params('audio'))
        self.assertEqual('bestaudio', self.config_manager.get_preset_params('audio').get('format'))

    def test_expand(self):
        self.assertEqual('videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s',
                         self.config_manager.get_preset_params('DEFAULT').get('outtmpl').get('default'))
        self.assertEqual('videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s',
                         self.config_manager.get_preset_params('SHARE').get('outtmpl').get('default'))
        self.assertNotEqual('/home/videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s',
                            self.config_manager.get_preset_params('DEFAULT').get('outtmpl').get('default'))
        self.assertFalse(self.config_manager.get_preset_params('playlist').get('noplaylist'))
        self.assertTrue(self.config_manager.get_preset_params('DEFAULT').get('noplaylist'))
        self.assertEqual('mp3', self.config_manager.get_preset_params('AUDIO_CLI').get('final_ext'))

    def test_app(self):
        self.assertEqual('/download', self.config_manager.get_app_params().get('_api_route_download'))
        self.assertTrue(self.config_manager.get_app_params().get('_unit_test'))
        self.assertIsNotNone(self.config_manager.get_app_params().get('_enable_users_management'))

    def test_user(self):
        self.assertIsNotNone(self.config_manager.get_user_param_by_token('dad_super_password'))
        self.assertIsNone(self.config_manager.get_user_param_by_token('doggo_super_password'))
        self.assertIsNone(self.config_manager.get_user_param_by_token('dad_super_password').get('doesnotexists'))
        self.assertEqual('./downloads/symlink_to_dad_home/',
                         self.config_manager.get_user_param_by_token('dad_super_password').get('paths').get('home'))

    def test_auth(self):
        self.assertEqual('Totonyus', self.config_manager.get_auth_params('DAILYMOTION').get('username'))
        self.assertEqual('is_this_site_still_running_fr_?',
                         self.config_manager.get_auth_params('DAILYMOTION').get('password'))


class TestUtils(unittest.TestCase):
    config_manager = config_manager.ConfigManager('params/params.sample.ini')

    def test_get_presets(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=OWCK3413Wuk', None,
                                              None)

        dm.flush_presets()
        self.assertIsNotNone(dm.get_presets_objects(['AUDIO']))

        dm.flush_presets()
        self.assertEqual(2, len(dm.get_presets_objects(['HD', 'FULLHD'])))

        dm.flush_presets()
        self.assertEqual(1, len(dm.get_presets_objects(['8K', '4K'])))

        dm.flush_presets()
        self.assertEqual(1, len(dm.get_presets_objects([])))

        dm.flush_presets()
        self.assertEqual(1, len(dm.get_presets_objects(None)))

        dm.flush_presets()
        self.assertEqual('DEFAULT', dm.get_presets_objects([])[0].get('_name'))

        dm.flush_presets()
        self.assertEqual(1, len(dm.get_presets_objects(['HD', '4K'])))

        dm.flush_presets()
        dm.get_presets_objects(['HD', 'HD'])
        self.assertEqual(1, dm.presets_found)

        dm.flush_presets()
        dm.get_presets_objects(['HD', '4K'])
        self.assertEqual(1, dm.presets_not_found)

        dm.flush_presets()
        dm.get_presets_objects(['HD', '4K', '8K'])
        self.assertEqual(2, dm.presets_not_found)

        dm.flush_presets()
        dm.get_presets_objects(['HD', 'AUDIO'])
        self.assertEqual(2, dm.presets_found)

        dm.flush_presets()
        dm.get_presets_objects(['HD', '4K', '8K'])
        self.assertEqual(1, dm.presets_found)

        dm.flush_presets()
        dm.get_presets_objects(['HD', '4K', '8K', 'AUDIO'])
        self.assertEqual(2, dm.presets_found)

        dm.flush_presets()
        dm.get_presets_objects(['8K', '4K'])
        self.assertTrue(dm.no_preset_found)

        dm.flush_presets()
        dm.get_presets_objects(['8K', '4K', 'AUDIO'])
        self.assertFalse(dm.no_preset_found)

        dm.flush_presets()
        dm.get_presets_objects(['AUDIO_CLI'])
        self.assertEqual('mp3', dm.presets[0].get('final_ext'))

    def test_post_presets(self):
        body = {
            'cookies': 'no',
            'presets': [{
                "_preset": "SD"
            }],
        }

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=OWCK3413Wuk', None,
                                              None, body, request_id="UNIT_TEST")

        preset_result = dm.get_api_return_object().get('downloads')[0]
        self.assertEqual('POST_REQUEST', preset_result.get('_name'))
        self.assertEqual('SD', preset_result.get('_preset'))
        self.assertIsNotNone(preset_result.get('__check_exception_message'))

        body = {
            'presets': [{
                "_cli": "-f bestaudio --embed-metadata --embed-thumbnail --extract-audio --audio-format mp3 --split-chapters"
            }]
        }

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=OWCK3413Wuk', None,
                                              None, body)

        preset_result = dm.get_api_return_object().get('downloads')[0]
        self.assertEqual('POST_REQUEST', preset_result.get('_name'))
        self.assertEqual('bestaudio', preset_result.get('format'))
        self.assertIsNotNone(preset_result.get('postprocessors'))
        self.assertNotEqual(0, len(preset_result.get('postprocessors')))

    def test_is_from_playlist(self):
        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj',
                                              None, None)
        self.assertTrue(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2',
                                              None, None)
        self.assertTrue(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertFalse(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertIsNone(dm.check_if_from_playlist())

    def test_is_video(self):
        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj',
                                              None, None)
        self.assertFalse(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2',
                                              None, None)
        self.assertTrue(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertTrue(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertIsNone(dm.check_if_video())

    def test_can_be_checked(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')
        playlist_preset = self.config_manager.get_preset_params('PLAYLIST')

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj',
                                              None, None)
        self.assertFalse(dm.can_url_be_checked(default_preset))
        self.assertTrue(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2',
                                              None, None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertFalse(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertFalse(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertTrue(dm.presets[0].get('ignoreerrors'))

    def test_get_permission(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'dad_super_password')
        self.assertIsInstance(dm.is_user_permitted(True), config_manager.SectionConfig)

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'doggo_super_password')
        self.assertFalse(dm.is_user_permitted(True))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertFalse(dm.is_user_permitted(True))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'dad_super_password')
        self.assertIsNone(dm.is_user_permitted(False))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'doggo_super_password')
        self.assertIsNone(dm.is_user_permitted(False))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertIsNone(dm.is_user_permitted(False))

    def test_get_preset_for_user(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'totonyus_super_password')
        self.assertEqual(['fr', 'en'], dm.get_preset_for_user(copy.deepcopy(default_preset)).get('subtitleslangs'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'totonyus_super_password')
        self.assertEqual('./downloads/', dm.get_preset_for_user(copy.deepcopy(default_preset)).get('paths').get('home'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'totonyus_super_password')
        self.assertEqual('DEFAULT', dm.get_preset_for_user(copy.deepcopy(default_preset)).get('_name'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'dad_super_password')
        self.assertEqual(['en'], dm.get_preset_for_user(copy.deepcopy(default_preset)).get('subtitleslangs'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              'dad_super_password')
        self.assertEqual('./downloads/symlink_to_dad_home/',
                         dm.get_preset_for_user(copy.deepcopy(default_preset)).get('paths').get('home'))

    @unittest.skip
    def test_simulate(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None,
                                              None)
        self.assertTrue(dm.simulate_download(default_preset))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UfErWGjj95', None,
                                              None)
        self.assertFalse(dm.simulate_download(default_preset))

        dm = download_manager.DownloadManager(self.config_manager,
                                              'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj',
                                              None, None)
        self.assertIsNone(dm.simulate_download(default_preset))

    @unittest.skip
    def test_process_download(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y',
                                              ['DEFAULT'], None)
        self.assertTrue(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y',
                                              ['AUDIO'], None)
        self.assertTrue(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5dUErWGjj95',
                                              ['AUDIO'], None)
        self.assertFalse(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y',
                                              ['AUDIO'], 'dad_super_password')
        self.assertTrue(dm.process_download(dm.presets[0]))

    def test_sanitize(self):
        self.config_manager.get_user_param_by_token('dad_super_password'),
        self.assertEqual('dad_super_password',
                         self.config_manager.get_user_param_by_token('dad_super_password').get('_token'))

        self.assertIsNone(
            self.config_manager.sanitize_config_object(self.config_manager.get_all_users_params()).get('DAD').get(
                '_token'))


@unittest.skip
class TestAPI(unittest.TestCase):
    base_url = "http://localhost:5011/download"

    def test_download(self):
        self.assertEqual(401,
                         requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk').status_code)
        self.assertEqual(202, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&token=dad_super_password').status_code)
        self.assertEqual(200, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password').status_code)
        self.assertEqual(401, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=mom_super_password').status_code)
        self.assertEqual(400, requests.get(f'{self.base_url}?url=&token=dad_super_password').status_code)
        self.assertEqual(422, requests.get(f'{self.base_url}?token=dad_super_password').status_code)
        self.assertEqual(200, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd').status_code)
        self.assertEqual(200, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=totonyus_super_password&presets=hd').status_code)
        self.assertEqual(200, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio').status_code)
        self.assertEqual(200, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=HD,AUDIO').status_code)
        self.assertEqual(206, requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio,4k').status_code)

    def test_download_info(self):
        request_json = requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio,4k').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(2, request_json.get('presets_found'))
        self.assertEqual(1, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(2, request_json.get('passed_checks'))
        self.assertEqual('HD', request_json.get('downloads')[0].get('_name'))
        self.assertEqual('AUDIO', request_json.get('downloads')[1].get('_name'))

        request_json = requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=fdsOWCK3413Wuk&token=dad_super_password&presets=4K,8K').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertTrue(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(2, request_json.get('presets_not_found'))
        self.assertEqual(1, request_json.get('failed_checks'))
        self.assertEqual(0, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))

        request_json = requests.get(
            f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(0, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(1, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))

        request_json = requests.get(
            f'{self.base_url}?url=https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&token=dad_super_password').json()

        self.assertFalse(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(0, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(1, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))


class TestProgrammation(unittest.TestCase):
    config_manager = config_manager.ConfigManager('params/params.sample.ini')

    database_file = 'test_database.json'
    try:
        os.remove(database_file)
    except FileNotFoundError:
        pass

    pm = Ppm(database_file=database_file)

    def test_add_programmation(self):
        prog = Programmation(programmation={
            'url': None
        })

        self.assertEqual(1, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': 'a more valid_url',
            'presets': "non valid presets"
        })

        self.assertEqual(1, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': 'a more valid_url',
            'presets': ['HD', 'AUDIO']
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a more valid_url8",
            'planning': {
                'recording_start_date': '2022-12-00 00:00',
                'recurrence_start_date': '2022-12-00 00:00',
                'recurrence_end_date': '2022-12-00 00:00',
            },
        })

        self.assertEqual(3, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a more valid_url",
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recurrence_start_date': '2022-12-01 00:00',
                'recurrence_end_date': '2022-12-02 00:00',
            },
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recording_duration': 'not valid',
            },
        })

        self.assertEqual(1, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recurrence_cron': 'invalid'
            },
        })

        self.assertEqual(1, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recurrence_cron': '00 12 * * *',
                'recording_start_date': '2022-12-01 10:00'
            },
        })

        self.assertEqual(2, len(prog.errors))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a special test",
            'planning': {
                'recurrence_cron': '00 13 * * *',
                'recurrence_start_date': None,
            },
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a valid url",
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recording_duration': 120,
            },
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation={
            'id': '0',
            'url': "a valid url",
            'enabled': False,
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recording_duration': 120,
            },
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))
        self.assertFalse(prog.enabled)
        self.assertNotEqual('0', prog.id)

        prog = Programmation(id="0", programmation={
            'url': "a valid url",
            'enabled': False,
            'planning': {
                'recording_start_date': '2022-12-15 00:00',
                'recording_duration': 120,
            },
        })

        self.assertEqual('0', prog.id)

        prog = Programmation(programmation={
            'url': "a valid url",
            'enabled': False,
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recording_duration': 120,
            },
        }, id='0')

        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))
        self.assertIsNone(self.pm.add_programmation(programmation=prog))
        self.assertEqual('0', prog.id)

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recurrence_cron': '00 12 * * *',
                'recording_duration': 60,

                'recurrence_start_date': '2022-12-01 00:00',
                'recurrence_end_date': '2022-12-31 23:59',
            },
        })

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))

        prog = Programmation(programmation=(
            {
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 13 * * *',
                    'recording_duration': 60,

                    'recurrence_start_date': '2022-12-01 00:00',
                    'recurrence_end_date': '2022-12-31 23:59',
                },
            }
        ))

        self.assertEqual(0, len(prog.errors))
        self.assertIsNotNone(self.pm.add_programmation(programmation=prog))
        self.assertTrue(prog.enabled)

        self.last_added_id = prog.id

        prog = self.pm.update_programmation_by_id(
            id=self.last_added_id,
            programmation={
                'enabled': False
            })

        self.assertEqual(0, len(prog.errors))
        self.assertFalse(prog.enabled)

        self.assertEqual(prog.id, self.last_added_id)
        self.assertIsNotNone(self.pm.get_programmation_by_id(self.last_added_id))

        self.assertEqual(datetime.fromisoformat('2022-12-01 13:00:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-11-30 12:00')))

        prog = self.pm.update_programmation_by_id(id=self.last_added_id,
                                                  programmation={
                                                      'planning': {
                                                          'recurrence_start_date': '2022-12-00 12:00'
                                                      }
                                                  })

        self.assertEqual(1, len(prog.errors))

        ### ACCESS
        self.assertEqual(9, len(self.pm.get_all_programmations()))
        self.assertEqual(6, len(self.pm.get_all_enabled_programmations()))

        latest_created_programmation = self.pm.get_programmation_by_id(id=self.last_added_id)
        self.assertIsNotNone(latest_created_programmation)
        self.assertFalse(latest_created_programmation.enabled)

        self.assertIsNotNone(self.pm.delete_programmation_by_id(id=self.last_added_id))
        self.assertEqual(6, len(self.pm.get_all_enabled_programmations()))

        prog = Programmation(programmation=(
            {
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 00 * * *',
                    'recurrence_start_date': '2022-12-01 00:00',
                },
            }
        ))

        self.assertEqual(datetime.fromisoformat('2022-12-01 00:00:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-11-30 12:00')))
        self.assertEqual(datetime.fromisoformat('2022-12-01 00:00:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-12-01 00:00')))
        self.assertEqual(datetime.fromisoformat('2022-12-02 00:00:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-12-01 00:01')))

    def test_end_dates_manipulation(self):
        self.assertEqual(datetime.fromisoformat('2022-12-01 02:00'), Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recording_duration': 120,
            },
        }).get_end_date())

        self.assertEqual(datetime.fromisoformat('2022-12-01 02:00'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recording_start_date': '2022-12-01 00:00',
                                 'recording_duration': 120,
                             },
                         }).get_end_date())

        self.assertEqual(datetime.fromisoformat('2022-12-01 00:00'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recurrence_end_date': '2022-12-01 00:00',
                             },
                         }).get_end_date())

        self.assertEqual(datetime.fromisoformat('2022-12-01 02:00'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recurrence_end_date': '2022-12-01 00:00',
                                 'recording_duration': 120,
                             },
                         }).get_end_date())

        self.assertEqual(datetime.fromisoformat('2022-12-31 23:59'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recurrence_cron': '15 12 * * *',
                                 'recurrence_start_date': '2022-12-30 00:00',
                                 'recurrence_end_date': '2022-12-31 23:59',
                             },
                         }).get_end_date())

        self.assertEqual(datetime.fromisoformat('2023-01-01 00:59'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recurrence_cron': '15 12 * * *',
                                 'recording_duration': 60,
                                 'recurrence_start_date': '2022-12-30 00:00',
                                 'recurrence_end_date': '2022-12-31 23:59',
                             },
                         }).get_end_date())

        self.assertEqual(4, len(self.pm.purge_all_past_programmations(
            from_date=datetime.fromisoformat('2022-12-03 01:00'))))
        self.assertEqual(4, len(self.pm.get_all_programmations()))

        self.assertEqual(datetime.fromisoformat('2022-12-20 13:02:00'),
                         Programmation(programmation={
                             'url': "a valid url",
                             'planning': {
                                 'recurrence_cron': '*/15 * * * *',
                                 'recording_duration': 2,
                                 'recurrence_start_date': '2022-12-01 00:00',
                                 'recurrence_end_date': '2022-12-20 13:00',
                             },
                         }).get_end_date())

    def test_restart(self):
        self.assertIsNone(Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recording_start_date': '2022-12-01 00:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 12:00')))

        self.assertEqual(60, Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recording_start_date': '2022-12-01 00:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 01:00'), ))

        self.assertIsNone(Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 12 * * *',
                    'recurrence_start_date': '2022-12-01 00:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 15:00')))

        self.assertEqual(60, Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 12 * * *',
                    'recurrence_start_date': '2022-12-01 00:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 13:00')))

        self.assertIsNone(Programmation(
            programmation={
                'url': "a valid url",
                'planning': {},
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 13:00')))

        self.assertIsNone(Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 12 * * *',
                    'recurrence_start_date': '2022-12-01 00:00',
                    'recurrence_end_date': '2022-12-02 23:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-02 15:00')))

        self.assertEqual(45, Programmation(
            programmation={
                'url': "a valid url",
                'planning': {
                    'recurrence_cron': '00 12 * * *',
                    'recurrence_start_date': '2022-12-01 00:00',
                    'recurrence_end_date': '2022-12-02 23:00',
                    'recording_duration': 120,
                },
            }).must_be_restarted(from_date=datetime.fromisoformat('2022-12-02 13:15')))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recording_start_date': '2022-12-01 00:00',
                'recording_duration': 120,
                'recording_restarts_during_duration': False
            },
        })

        self.assertIsNone(prog.must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 01:00')))

        prog = Programmation(programmation={
            'url': "a valid url",
            'planning': {
                'recurrence_cron': '00 12 * * *',
                'recording_duration': 120,
                'recording_restarts_during_duration': False,
                'recurrence_start_date': '2022-11-01 00:00'
            },
        })

        self.assertIsNone(prog.must_be_restarted(from_date=datetime.fromisoformat('2022-12-01 13:00')))
        self.assertEqual(datetime.fromisoformat('2022-12-02 12:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-12-01 13:00')))
        self.assertEqual(datetime.fromisoformat('2022-12-01 12:00'),
                         prog.get_next_execution(from_date=datetime.fromisoformat('2022-12-01 11:00')))


if __name__ == '__main__':
    unittest.main()
