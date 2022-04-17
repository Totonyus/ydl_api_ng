import logging
import os
import pathlib
import re

import psutil


def get_active_downloads_list():
    children_process = psutil.Process().children(recursive=True)

    active_downloads_list = []
    for child in children_process:
        active_download = {
            'command_line': f'{child.cmdline()}',
            'filename': get_current_download_file_destination(child.cmdline()),
            'pid': child.pid,
            'create_time': child.create_time()
        }

        active_downloads_list.append(active_download)

    return active_downloads_list


def get_current_download_file_destination(cmdline):
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
    }


def is_a_child_process(pid):
    children_process = psutil.Process().children(recursive=True)

    is_child = False

    for child in children_process:
        if child.pid == pid:
            is_child = True

    return is_child


def get_child_object(pid):
    children_process = psutil.Process().children(recursive=True)

    for child in children_process:
        if child.pid == pid:
            return child

    return None


def terminate_active_download(pid):
    child = get_child_object(int(pid))

    if child is not None:
        logging.getLogger('process_utils').info(f'PID {pid} will be terminated')

        child.terminate()
        filename_info = get_current_download_file_destination(child.cmdline())

        new_name = f'{filename_info.get("path")}{filename_info.get("filename_stem")}_terminated{filename_info.get("extension")}'

        os.rename(filename_info.get('part_filename'), new_name)  # renaming file to remove the .part
        return pid
    else:
        logging.getLogger('process_utils').error(f'PID {pid} does not exist or does not belong to the application')

    return None


def terminate_all_active_downloads():
    logging.getLogger('process_utils').info('All active downloads are being terminated')

    pids = []
    for download in get_active_downloads_list():
        pid = download.get('pid')
        pids.append(terminate_active_download(pid))

    return pids
