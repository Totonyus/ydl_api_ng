import copy
import unittest

import requests

import config_manager
import download_manager


class TestActualParametersFile(unittest.TestCase):
    config_manager = config_manager.ConfigManager()

    def test_app(self):
        self.assertEqual(80, self.config_manager.get_app_params().get('_listen_port'))
        self.assertIsNot(True, self.config_manager.get_app_params().get('_dev_mode'))
        self.assertFalse(self.config_manager.get_app_params().get('_enable_users_management'))
        self.assertEqual('0.0.0.0', self.config_manager.get_app_params().get('_listen_ip'))
        self.assertFalse(self.config_manager.get_app_params().get('_allow_dangerous_post_requests'))


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
        self.assertEqual('videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s', self.config_manager.get_preset_params('DEFAULT').get('outtmpl').get('default'))
        self.assertEqual('videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s', self.config_manager.get_preset_params('SHARE').get('outtmpl').get('default'))
        self.assertNotEqual('/home/videos/%(webpage_url_domain)s/%(title)s_(%(height)s).%(ext)s', self.config_manager.get_preset_params('DEFAULT').get('outtmpl').get('default'))
        self.assertFalse(self.config_manager.get_preset_params('playlist').get('noplaylist'))
        self.assertTrue(self.config_manager.get_preset_params('DEFAULT').get('noplaylist'))

    def test_app(self):
        self.assertEqual('/download', self.config_manager.get_app_params().get('_api_route_download'))
        self.assertTrue(self.config_manager.get_app_params().get('_unit_test'))
        self.assertIsNotNone(self.config_manager.get_app_params().get('_enable_users_management'))

    def test_user(self):
        self.assertIsNotNone(self.config_manager.get_user_param_by_token('dad_super_password'))
        self.assertIsNone(self.config_manager.get_user_param_by_token('doggo_super_password'))
        self.assertIsNone(self.config_manager.get_user_param_by_token('dad_super_password').get('doesnotexists'))
        self.assertEqual('./downloads/symlink_to_dad_home/', self.config_manager.get_user_param_by_token('dad_super_password').get('paths').get('home'))

    def test_auth(self):
        self.assertEqual('Totonyus', self.config_manager.get_auth_params('DAILYMOTION').get('username'))
        self.assertEqual('is_this_site_still_running_fr_?', self.config_manager.get_auth_params('DAILYMOTION').get('password'))


class TestUtils(unittest.TestCase):
    config_manager = config_manager.ConfigManager('params/params.sample.ini')

    def test_get_presets(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=OWCK3413Wuk', None, None)

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

    def test_is_from_playlist(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', None, None)
        self.assertTrue(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2', None, None)
        self.assertTrue(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertFalse(dm.check_if_from_playlist())

        dm = download_manager.DownloadManager(self.config_manager, 'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertIsNone(dm.check_if_from_playlist())

    def test_is_video(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', None, None)
        self.assertFalse(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2', None, None)
        self.assertTrue(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertTrue(dm.check_if_video())

        dm = download_manager.DownloadManager(self.config_manager, 'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertIsNone(dm.check_if_video())

    def test_can_be_checked(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')
        playlist_preset = self.config_manager.get_preset_params('PLAYLIST')

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', None, None)
        self.assertFalse(dm.can_url_be_checked(default_preset))
        self.assertTrue(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y&list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&index=2', None, None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertFalse(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertFalse(dm.presets[0].get('ignoreerrors'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://twitter.com/Totonyus/status/1471896525617909760', None, None)
        self.assertTrue(dm.can_url_be_checked(default_preset))
        self.assertTrue(dm.presets[0].get('ignoreerrors'))

    def test_get_permission(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'dad_super_password')
        self.assertIsInstance(dm.is_user_permitted(True), config_manager.SectionConfig)

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'doggo_super_password')
        self.assertFalse(dm.is_user_permitted(True))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertFalse(dm.is_user_permitted(True))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'dad_super_password')
        self.assertIsNone(dm.is_user_permitted(False))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'doggo_super_password')
        self.assertIsNone(dm.is_user_permitted(False))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertIsNone(dm.is_user_permitted(False))

    def test_get_preset_for_user(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'totonyus_super_password')
        self.assertEqual(['fr', 'en'], dm.get_preset_for_user(copy.deepcopy(default_preset)).get('subtitleslangs'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'totonyus_super_password')
        self.assertEqual('./downloads/', dm.get_preset_for_user(copy.deepcopy(default_preset)).get('paths').get('home'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'totonyus_super_password')
        self.assertEqual('DEFAULT', dm.get_preset_for_user(copy.deepcopy(default_preset)).get('_name'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'dad_super_password')
        self.assertEqual(['en'], dm.get_preset_for_user(copy.deepcopy(default_preset)).get('subtitleslangs'))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, 'dad_super_password')
        self.assertEqual('./downloads/symlink_to_dad_home/', dm.get_preset_for_user(copy.deepcopy(default_preset)).get('paths').get('home'))

    def test_simulate(self):
        default_preset = self.config_manager.get_preset_params('DEFAULT')

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', None, None)
        self.assertTrue(dm.simulate_download(default_preset))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UfErWGjj95', None, None)
        self.assertFalse(dm.simulate_download(default_preset))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj', None, None)
        self.assertIsNone(dm.simulate_download(default_preset))

    @unittest.skip
    def test_process_download(self):
        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', ['DEFAULT'], None)
        self.assertTrue(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', ['AUDIO'], None)
        self.assertTrue(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5dUErWGjj95', ['AUDIO'], None)
        self.assertFalse(dm.process_download(dm.presets[0]))

        dm = download_manager.DownloadManager(self.config_manager, 'https://www.youtube.com/watch?v=5UErWGjj95Y', ['AUDIO'], 'dad_super_password')
        self.assertTrue(dm.process_download(dm.presets[0]))

    def test_sanitize(self):
        self.config_manager.get_user_param_by_token('dad_super_password'),
        self.assertEqual('dad_super_password', self.config_manager.get_user_param_by_token('dad_super_password').get('_token'))

        self.assertIsNone(self.config_manager.sanitize_config_object(self.config_manager.get_all_users_params()).get('DAD').get('_token'))


@unittest.skip
class TestAPI(unittest.TestCase):
    base_url = "http://localhost:5011/download"

    def test_download(self):
        self.assertEqual(401, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk').status_code)
        self.assertEqual(202, requests.get(f'{self.base_url}?url=https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&token=dad_super_password').status_code)
        self.assertEqual(200, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password').status_code)
        self.assertEqual(401, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=mom_super_password').status_code)
        self.assertEqual(400, requests.get(f'{self.base_url}?url=&token=dad_super_password').status_code)
        self.assertEqual(422, requests.get(f'{self.base_url}?token=dad_super_password').status_code)
        self.assertEqual(200, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd').status_code)
        self.assertEqual(200, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=totonyus_super_password&presets=hd').status_code)
        self.assertEqual(200, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio').status_code)
        self.assertEqual(200, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=HD,AUDIO').status_code)
        self.assertEqual(206, requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio,4k').status_code)

    def test_download_info(self):
        request_json = requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password&presets=hd,audio,4k').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(2, request_json.get('presets_found'))
        self.assertEqual(1, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(2, request_json.get('passed_checks'))
        self.assertEqual('HD', request_json.get('downloads')[0].get('_name'))
        self.assertEqual('AUDIO', request_json.get('downloads')[1].get('_name'))

        request_json = requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=fdsOWCK3413Wuk&token=dad_super_password&presets=4K,8K').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertTrue(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(2, request_json.get('presets_not_found'))
        self.assertEqual(1, request_json.get('failed_checks'))
        self.assertEqual(0, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))

        request_json = requests.get(f'{self.base_url}?url=https://www.youtube.com/watch?v=OWCK3413Wuk&token=dad_super_password').json()

        self.assertTrue(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(0, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(1, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))

        request_json = requests.get(f'{self.base_url}?url=https://www.youtube.com/playlist?list=PL8Zccvo5Xlj53ESRIn2Q4lg2DvKIB92sj&token=dad_super_password').json()

        self.assertFalse(request_json.get('all_downloads_checked'))
        self.assertFalse(request_json.get('no_preset_found'))
        self.assertEqual(0, request_json.get('presets_found'))
        self.assertEqual(0, request_json.get('presets_not_found'))
        self.assertEqual(0, request_json.get('failed_checks'))
        self.assertEqual(1, request_json.get('passed_checks'))
        self.assertEqual('DEFAULT', request_json.get('downloads')[0].get('_name'))


if __name__ == '__main__':
    unittest.main()
