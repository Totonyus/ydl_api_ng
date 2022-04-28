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
from params import ydl_api_hooks


class ProcessUtils:
    def __init__(self, config_manager):
        self.__cm = config_manager

        if self.__cm.get_app_params().get('_enable_redis') is not None and self.__cm.get_app_params().get('_enable_redis') is True:
            self.redis = Redis()
            self.queue = Queue('ydl_api_ng', connection=self.redis)
            self.registries = {'pending_job': self.queue,
                               'started_job': self.queue.started_job_registry,
                               'finished_job': self.queue.finished_job_registry,
                               'failed_job': self.queue.failed_job_registry,
                               'deferred_job': self.queue.deferred_job_registry,
                               'scheduled_job': self.queue.scheduled_job_registry,
                               'canceled_job': self.queue.canceled_job_registry,
                               }

            # self.update_registries()
        else:
            self.redis = None
            self.queue = None
            self.registries = None

    def terminate_active_download(self, id):
        if self.redis is None:
            return self.terminate_basic_active_download(id)
        else:
            return self.terminate_redis_active_download(id)

    def terminate_basic_active_download(self, pid):
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

    def terminate_redis_active_download(self, search_job_id):
        job = self.find_in_running(search_job_id)

        if job is not None:
            child_process = psutil.Process(job.get('worker').pid).children(recursive=True)

            job_object = {
                'id': job.get('id'),
                'preset': job.get('preset'),
                'download_manager': job.get('download_manager'),
                'worker': job.get('worker'),
                'state': 'stopped'
            }

            ffmpeg_killed = False
            for process in child_process:
                if process.name() == "ffmpeg":
                    ffmpeg_killed = True
                    filename_info = self.get_current_download_file_destination(process.cmdline())
                    os.kill(process.pid, signal.SIGINT)

                    try:
                        filesize = os.path.getsize(filename_info.get('part_filename'))
                        os.rename(filename_info.get('part_filename'), filename_info.get('filename'))  # renaming file to remove the .part

                        filename_info['file_size'] = filesize

                        if callable(getattr(ydl_api_hooks, 'post_redis_termination_handler', None)):
                            ydl_api_hooks.post_redis_termination_handler(job_object.get('download_manager'), filename_info)
                    except FileNotFoundError:
                        pass

            if not ffmpeg_killed:
                send_kill_horse_command(self.redis, job.get('worker').name)

            return self.sanitize_job(job_object)
        return None

    def terminate_all_active_downloads(self):
        if self.redis is None:
            return self.terminate_all_basic_active_downloads()
        else:
            return self.terminate_all_redis_active_downloads()

    def terminate_all_basic_active_downloads(self):
        logging.getLogger('process_utils').info('All active downloads are being terminated')

        informations = []
        for download in self.get_active_downloads_list():
            pid = download.get('pid')
            informations.append(self.terminate_active_download(pid))

        return informations

    def terminate_all_redis_active_downloads(self):
        stopped = []
        for worker in self.get_workers_info():
            if worker.get('current_job_info') is not None:
                job = worker.get('current_job_info').get('job')
                self.terminate_redis_active_download(job.id)
                stopped.append(self.sanitize_job(worker.get('current_job_info')))
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
            'download_manager': job.get('download_manager').get_api_return_object()
        }

    def get_redis_active_downloads_list(self):
        # self.update_registries()
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
            job = Job.fetch(job_id, connection=self.redis)
            jobs.append({
                'id': job.id,
                'registry': registry,
                'preset': job.args[0],
                'download_manager': job.args[1]
            })

        return jobs

    def clear_registry(self, registry):
        cleared_jobs_ids = []

        for job_id in self.registries.get(registry).get_job_ids():
            job = Job.fetch(job_id, connection=self.redis)
            cleared_jobs_ids.append(job.id)

            try:
                job.cancel()
            except rq.exceptions.InvalidJobOperation:
                pass

            job.delete()

        # self.update_registries()
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
                worker_object['current_job_info'] = {
                    'id': current_job.id,
                    'preset': current_job.args[0],
                    'download_manager': current_job.args[1],
                    'job': current_job
                }

            workers.append(worker_object)

        return workers

    def find_job_by_id(self, searched_job_id):
        for registry in self.registries:
            for job_id in self.registries.get(registry).get_job_ids():
                if job_id == searched_job_id:
                    job = Job.fetch(job_id, connection=self.redis)
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
                    'worker': worker
                }
        return None

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

    def get_queue_content(self, registry):
        sanitized_jobs = {}

        if registry == 'all':
            registries = self.get_all_jobs()
        elif self.registries.get(registry) is None:
            return None
        else:
            registries = {registry: self.get_jobs_from_registry(registry)}

        for r in registries:
            sanitized_jobs[r] = self.sanitize_registry(r)

        return sanitized_jobs
