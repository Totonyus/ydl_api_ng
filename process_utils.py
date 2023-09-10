import logging
import rq
from redis import Redis
from rq import Worker, Queue
from rq.command import send_kill_horse_command
from rq.job import Job
import os
import signal
import psutil
import re
import pathlib
import inspect
from mergedeep import merge

import download_manager
from params import ydl_api_hooks


class ProcessUtils:
    def __init__(self, config_manager):
        self.__cm = config_manager

        if self.__cm.get_app_params().get('_enable_redis') is not None and self.__cm.get_app_params().get(
                '_enable_redis') is True:
            self.redis = Redis(host=self.__cm.get_app_params().get('_redis_host'),
                               port=self.__cm.get_app_params().get('_redis_port'))
            self.queue = Queue('ydl_api_ng', connection=self.redis)
            self.registries = {'pending_job': self.queue,
                               'started_job': self.queue.started_job_registry,
                               'finished_job': self.queue.finished_job_registry,
                               'failed_job': self.queue.failed_job_registry,
                               'deferred_job': self.queue.deferred_job_registry,
                               'scheduled_job': self.queue.scheduled_job_registry,
                               'canceled_job': self.queue.canceled_job_registry,
                               }
            self.programmation_registries = {
                'pending_job': self.queue,
                'started_job': self.queue.started_job_registry,
            }

        else:
            self.redis = None
            self.queue = None
            self.registries = None

    def terminate_active_download(self, id, background_tasks=None):
        if self.redis is None or (self.redis is not None and self.redis is False):
            return self.terminate_basic_active_download(id, background_tasks=background_tasks)
        else:
            return self.terminate_redis_active_download(id, background_tasks=background_tasks)

    def terminate_basic_active_download(self, pid, background_tasks=None):
        child = self.get_child_object(int(pid))

        if child is not None:
            logging.getLogger('process_utils').info(f'PID {pid} will be terminated')

            child.terminate()
            filename_info = self.get_current_download_file_destination(child.cmdline())

            if background_tasks is not None:
                background_tasks.add_task(self.ffmpeg_terminated_file, filename_info=filename_info)
            else:
                self.ffmpeg_terminated_file(filename_info=filename_info)

            if callable(getattr(ydl_api_hooks, 'post_termination_handler', None)):
                ydl_api_hooks.post_termination_handler(self.__cm, filename_info)

            return filename_info
        else:
            logging.getLogger('process_utils').error(f'PID {pid} does not exist or does not belong to the application')

        return None

    def find_ffmpeg_filename_info(self, job):
        child_process = psutil.Process(job.get('worker').pid).children(recursive=True)

        for process in child_process:
            if process.name() == "ffmpeg":
                info = self.get_current_download_file_destination(process.cmdline())
                return process.pid, info

        return None, None

    def find_ffmpeg_filename_info_by_pid(self, pid):
        child_process = psutil.Process(pid).children(recursive=True)

        for process in child_process:
            if process.name() == "ffmpeg":
                info = self.get_current_download_file_destination(process.cmdline())
                return process.pid, info

        return None, None

    def terminate_redis_download_by_programmation_id(self, programmation_id=None, *args, **kwargs):
        found_job = self.find_job_by_programmation_id(programmation_id)
        self.terminate_redis_active_download(found_job.get('id'))

    def terminate_redis_active_download(self, search_job_id, background_tasks=None):
        job = self.find_in_running(search_job_id)

        if job is not None:
            ffmpeg_killed = False
            process_pid, filename_info = self.find_ffmpeg_filename_info(job)

            job_object = {
                'id': job.get('id'),
                'preset': job.get('preset'),
                'download_manager': job.get('download_manager'),
                'worker': job.get('worker'),
                'job': job.get('job'),
            }

            if filename_info is not None:
                ffmpeg_killed = True
                os.kill(process_pid, signal.SIGINT)

                try:
                    job.get('job').meta['filename_info'] = filename_info
                    job.get('job').meta['terminated'] = True
                    job.get('job').save()
                    job.get('job').refresh()

                    if background_tasks is not None:
                        background_tasks.add_task(self.ffmpeg_terminated_file, filename_info=filename_info)
                    else:
                        self.ffmpeg_terminated_file(filename_info=filename_info)

                    if callable(getattr(ydl_api_hooks, 'post_redis_termination_handler', None)):
                        ydl_api_hooks.post_redis_termination_handler(job_object.get('download_manager'), filename_info)


                except FileNotFoundError as e:
                    logging.getLogger('process_utils').error(e)
                    pass

                logging.getLogger('process_utils').info(f'ffmpeg process killed : {process_pid}')

            if not ffmpeg_killed:
                send_kill_horse_command(self.redis, job.get('worker').name)

                if callable(getattr(ydl_api_hooks, 'post_redis_termination_handler', None)):
                    ydl_api_hooks.post_redis_termination_handler(job_object.get('download_manager'), None)

                logging.getLogger('process_utils').info(f"Job stopped on worker {job.get('worker').name}")

                if inspect.getfullargspec(ydl_api_hooks.post_download_handler).varkw is not None:
                    ydl_api_hooks.post_download_handler(job.get('preset'), job.get('download_manager'),
                                                        job.get('download_manager').get_current_config_manager(),
                                                        job.get('job').meta.get('downloaded_files'), job=job)
                else:
                    ydl_api_hooks.post_download_handler(job.get('preset'), job.get('download_manager'),
                                                        job.get('download_manager').get_current_config_manager(),
                                                        job.get('job').meta.get('downloaded_files'))

            return self.sanitize_job(job_object)
        else:
            job = self.find_job_by_id(search_job_id)

            if job is None:
                return None

            try:
                job.get('job').cancel()
                job.get('job').delete()
            except rq.exceptions.InvalidJobOperation:
                job.get('job').delete()

            return self.sanitize_job(job)

    def terminate_all_active_downloads(self, background_tasks=None):
        if self.redis is None:
            return self.terminate_all_basic_active_downloads(background_tasks=background_tasks)
        else:
            return self.terminate_all_redis_active_downloads(background_tasks=background_tasks)

    def terminate_all_basic_active_downloads(self, background_tasks=None):
        logging.getLogger('process_utils').info('All active downloads are being terminated')

        informations = []
        for download in self.get_active_downloads_list():
            pid = download.get('pid')
            informations.append(self.terminate_active_download(pid, background_tasks=background_tasks))

        return informations

    def terminate_all_redis_active_downloads(self, background_tasks=None):
        stopped = []
        for worker in self.get_workers_info():
            if worker.get('job') is not None:
                job = worker.get('job').get('job')
                stopped.append(self.terminate_redis_active_download(job.id, background_tasks=background_tasks))
        return stopped

    def get_active_downloads_list(self):
        if self.redis is None:
            return self.get_basic_active_downloads_list()
        else:
            return self.get_redis_active_downloads_list()

    def get_basic_active_downloads_list(self):
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

    def sanitize_registry(self, registry):
        sanitized = []
        jobs = self.get_jobs_from_registry(registry)

        for job in jobs:
            sanitized_job = self.sanitize_job(job)
            sanitized.append(sanitized_job)

        return sanitized

    def sanitize_job(self, job):
        return {
            'id': job.get('id'),
            'preset': self.__cm.sanitize_config_object_section(job.get('preset')).get_all(),
            'download_manager': job.get('download_manager').get_api_return_object(),
            'job': self.sanitize_job_object(job.get('job')),
        }

    def sanitize_job_object(self, job):
        if job is None:
            return None

        sanitize_object = {
            'status': job.get_status(refresh=True),
            'result': job.result,
            'enqueued_at': job.enqueued_at,
            'started_at': job.started_at,
            'ended_at': job.ended_at,
            'exc_info': job.exc_info,
            'last_heartbeat': job.last_heartbeat,
            'worker_name': job.worker_name,
            'meta': job.meta
        }

        return sanitize_object

    def sanitize_workers_list(self, workers):
        sanitized_workers = []
        for worker in workers:
            sanitizer_worker = {
                'name': worker.get('name'),
                'hostname': worker.get('hostname'),
                'pid': worker.get('pid'),
                'state': worker.get('state'),
                'last_heartbeat': worker.get('last_heartbeat'),
                'birth_date': worker.get('birth_date'),
                'successful_job_count': worker.get('successful_job_count'),
                'failed_job_count': worker.get('failed_job_count'),
                'total_working_time': worker.get('total_working_time'),
                'job': None,
            }

            current_job = worker.get('current_job')
            if current_job is not None:
                sanitizer_worker['job'] = self.sanitize_job({
                    'id': current_job.id,
                    'preset': current_job.args[0],
                    'download_manager': current_job.args[1],
                    'job': current_job
                })

            sanitized_workers.append(sanitizer_worker)

        return sanitized_workers

    def get_redis_active_downloads_list(self):
        return {
            'started_job': self.sanitize_registry('started_job'),
            'pending_job': self.sanitize_registry('pending_job')
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

    def get_jobs_from_registry(self, registry):
        jobs = []

        for job_id in self.registries.get(registry).get_job_ids():
            try:
                job = Job.fetch(job_id, connection=self.redis)

                jobs.append({
                    'id': job.id,
                    'registry': registry,
                    'preset': job.args[0],
                    'download_manager': job.args[1],
                    'job': job
                })
            except rq.exceptions.NoSuchJobError:
                pass

        return jobs

    def clear_registry(self, registry):
        cleared_jobs_ids = []

        for job_id in self.registries.get(registry).get_job_ids():
            try:
                job = Job.fetch(job_id, connection=self.redis)
                cleared_jobs_ids.append(job.id)

                job.cancel()
            except rq.exceptions.InvalidJobOperation:
                job.delete()
            except rq.exceptions.NoSuchJobError:
                pass

        return cleared_jobs_ids

    def clear_all_but_pending_and_started(self):
        self.clear_registry('finished_job')
        self.clear_registry('failed_job')
        self.clear_registry('deferred_job')
        self.clear_registry('scheduled_job')
        self.clear_registry('canceled_job')

    def get_all_jobs(self):
        jobs = {}
        for registry in self.registries:
            jobs[registry] = self.get_jobs_from_registry(registry)

        return jobs

    def get_workers_info(self):
        workers = []
        for worker in Worker.all(self.redis):
            worker_object = {
                'name': worker.name,
                'hostname': worker.hostname,
                'pid': worker.pid,
                'queues': worker.queues,
                'state': worker.state,
                'current_job': worker.get_current_job(),
                'last_heartbeat': worker.last_heartbeat,
                'birth_date': worker.birth_date,
                'successful_job_count': worker.successful_job_count,
                'failed_job_count': worker.failed_job_count,
                'total_working_time': worker.total_working_time,
                'worker': worker
            }

            current_job = worker_object.get('current_job')
            if current_job is not None:
                worker_object['job'] = {
                    'id': current_job.id,
                    'preset': current_job.args[0],
                    'download_manager': current_job.args[1],
                    'job': current_job
                }

                pid, current_job.meta['filename_info'] = self.find_ffmpeg_filename_info_by_pid(worker.pid)

            workers.append(worker_object)

        return workers

    def find_job_by_id(self, searched_job_id):
        for registry in self.registries:
            for job_id in self.registries.get(registry).get_job_ids():
                if job_id == searched_job_id:
                    try:
                        job = Job.fetch(job_id, connection=self.redis)
                        return {
                            'id': job.id,
                            'registry': registry,
                            'preset': job.args[0],
                            'download_manager': job.args[1],
                            'job': job
                        }
                    except rq.exceptions.NoSuchJobError:
                        return None
        return None

    def find_job_with_programmation_end_date(self):
        jobs = []
        for registry in ["pending_job", "started_job"]:
            for job_id in self.registries.get(registry).get_job_ids():
                try:
                    job = Job.fetch(job_id, connection=self.redis)

                    if job.meta.get('programmation_end_date') is not None:
                        jobs.append({
                            'id': job.id,
                            'registry': registry,
                            'preset': job.args[0],
                            'download_manager': job.args[1],
                            'job': job
                        })
                except rq.exceptions.NoSuchJobError:
                    return None
        return jobs

    def find_job_by_programmation_id(self, programmation_id=None, *args, **kwargs):
        for registry, content in self.programmation_registries.items():
            for job_id in content.get_job_ids():
                job = Job.fetch(job_id, connection=self.redis)

                if job.meta.get('programmation_id') == programmation_id:
                    return {
                        'id': job.id,
                        'registry': registry,
                        'preset': job.args[0],
                        'download_manager': job.args[1],
                        'job': job
                    }
        return None

    def find_in_running(self, search_job_id):
        for worker in Worker.all(self.redis):
            current_job = worker.get_current_job()
            if current_job is not None and current_job.id == search_job_id:
                return {
                    'id': current_job.id,
                    'preset': current_job.args[0],
                    'download_manager': current_job.args[1],
                    'worker': worker,
                    'job': current_job
                }
        return None

    def get_current_download_file_destination(self, cmdline):
        regex = r'\'file:(.*\/)(.*)\''

        match = re.search(regex, f'{cmdline}')

        part_filename = f'{match.group(1)}{match.group(2)}'
        filename = part_filename.removesuffix('.part')

        path = match.group(1)
        filename_stem = pathlib.Path(filename).stem
        extension = pathlib.Path(filename).suffix

        try:
            file_size = os.path.getsize(part_filename)
        except FileNotFoundError:
            try:
                file_size = os.path.getsize(filename)
            except FileNotFoundError:
                file_size = 0

        return {
            'part_filename': part_filename,
            'filename': filename,
            'path': path,
            'filename_stem': filename_stem,
            'extension': extension,
            'full_filename': f'{filename_stem}{extension}',
            'file_size': file_size
        }

    def get_queue_content(self, registry):
        sanitized_jobs = {}

        if registry == 'all':
            registries = self.get_all_jobs()
        elif registry == 'workers':
            registries = self.sanitize_workers_list(self.get_workers_info())
            return registries
        elif self.registries.get(registry) is None:
            return None
        else:
            registries = {registry: self.get_jobs_from_registry(registry)}

        for r in registries:
            sanitized_jobs[r] = self.sanitize_registry(r)

        return sanitized_jobs

    def relaunch_failed(self, job_id, user_token=None):
        try:
            job = Job.fetch(job_id, connection=self.redis)
        except rq.exceptions.NoSuchJobError:
            return 404, None

        preset = job.args[0].get_all()
        preset['ignoreerrors'] = False

        downloads_state = {}
        launched_downloads = []

        downloaded_files = job.meta.get('downloaded_files')
        if downloaded_files is not None:
            downloads_state = download_manager.DownloadManager.get_downloaded_files_info(
                job.meta.get('downloaded_files'))

        for video_id in downloads_state:
            download_object = downloads_state.get(video_id)
            if download_object.get('error_downloads') > 0:
                url = download_object.get('downloads')[0].get('info_dict').get('webpage_url')

                dm = download_manager.DownloadManager(self.__cm, url, None, user_token, {'presets': [preset]},
                                                      ignore_post_security=True, relaunch_failed_mode=True)
                dm.process_downloads()

                launched_downloads.append(dm.get_api_return_object())

        return 200, launched_downloads

    def relaunch_job(self, job_id, user_token):
        try:
            job = Job.fetch(job_id, connection=self.redis)
        except rq.exceptions.NoSuchJobError:
            return 404, None

        preset = job.args[0].get_all()
        dm = job.args[1]

        dm = download_manager.DownloadManager(self.__cm, dm.url, None, user_token, {'presets': [preset]},
                                              ignore_post_security=True)

        if dm.get_api_status_code() != 400:
            dm.process_downloads()

        return dm.get_api_status_code(), dm.get_api_return_object()

    def ffmpeg_terminated_file(self, filename_info=None, *args, **kwargs):
        try:
            os.rename(filename_info.get('part_filename'), filename_info.get('filename'))
        except Exception as e:
            logging.getLogger('process_utils').error(f'{filename_info.get("part_filename")} : {e}')

        return filename_info

    def update_active_download_metadata(self, id=None, metadata=None, *args, **kwargs):
        found_job = self.find_in_running(search_job_id=id)

        if found_job is None:
            return None

        try:
            job = Job.fetch(found_job.get('id'), connection=self.redis)
        except rq.exceptions.NoSuchJobError:
            return None

        job.meta = merge(job.meta, metadata)
        job.save()
        job.refresh()

        return self.sanitize_job(self.find_job_by_id(searched_job_id=id))
