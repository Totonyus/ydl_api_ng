import logging
import os
import pathlib
import re

import psutil

from params import ydl_api_hooks


class ProcessUtils:
    def __init__(self, config_manager):
        self.__cm = config_manager

    def get_active_downloads_list(self):
        children_process = psutil.Process().children(recursive=True)

        active_downloads_list = []
        for child in children_process:
            active_download = {
                'command_line': f'{child.cmdline()}',
                'filename': self.get_current_download_file_destination(child.cmdline()),
                'pid': child.pid,
                'create_time': child.create_time()
            }

            active_downloads_list.append(active_download)

        return active_downloads_list

    def get_current_download_file_destination(self, cmdline):
        regex = r'\'file:(.*\/)(.*)\''

        match = re.search(regex, f'{cmdline}')

        part_filename = f'{match.group(1)}{match.group(2)}'
        filename = part_filename.rstrip('.part')

        path = match.group(1)
        filename_stem = pathlib.Path(filename).stem
        extension = pathlib.Path(filename).suffix

        return {
            'part_filename': part_filename,
            'filename': filename,
            'path': path,
            'filename_stem': filename_stem,
            'extension': extension,
            'full_filename': f'{filename_stem}{extension}'
        }

    def is_a_child_process(self, pid):
        children_process = psutil.Process().children(recursive=True)

        is_child = False

        for child in children_process:
            if child.pid == pid:
                is_child = True

        return is_child

    def get_child_object(self, pid):
        children_process = psutil.Process().children(recursive=True)

        for child in children_process:
            if child.pid == pid:
                return child

        return None

    def terminate_active_download(self, pid):
        child = self.get_child_object(int(pid))

        if child is not None:
            logging.getLogger('process_utils').info(f'PID {pid} will be terminated')

            child.terminate()
            filename_info = self.get_current_download_file_destination(child.cmdline())

            filesize = os.path.getsize(filename_info.get('part_filename'))
            os.rename(filename_info.get('part_filename'), filename_info.get('filename'))  # renaming file to remove the .part

            filename_info['file_size'] = filesize

            if callable(getattr(ydl_api_hooks, 'post_termination_handler', None)):
                ydl_api_hooks.post_termination_handler(self.__cm, filename_info)

            return filename_info
        else:
            logging.getLogger('process_utils').error(f'PID {pid} does not exist or does not belong to the application')

        return None

    def terminate_all_active_downloads(self):
        logging.getLogger('process_utils').info('All active downloads are being terminated')

        informations = []
        for download in self.get_active_downloads_list():
            pid = download.get('pid')
            informations.append(self.terminate_active_download(pid))

        return informations
