import time
from datetime import datetime, timedelta

import config_manager
import download_manager
import process_utils

import programmation_persistence_manager
from programmation_class import Programmation

import logging

__cm = config_manager.ConfigManager()
__pu = process_utils.ProcessUtils(__cm)
__pm = programmation_persistence_manager.ProgrammationPersistenceManager()

programmation_interval = __cm.get_app_params().get('_programmation_interval')

enable_redis = False if __cm.get_app_params().get('_enable_redis') is not True else True


def run():
    logging.getLogger('programmation').info(f'New iteration : {datetime.now()}')

    purged_programmations = __pm.purge_all_past_programmations()

    if len(purged_programmations) > 0:
        logging.getLogger('programmation').info(f'{len(purged_programmations)} deleted outdated entries')

    all_programmations = __pm.get_all_enabled_programmations()

    jobs_to_check = __pu.find_job_with_programmation_end_date()

    for job in jobs_to_check:
        if job is not None and job.get('job').meta.get('programmation_end_date') < datetime.now():
            if job.get('job').meta.get('programmation_end_date') < datetime.now():
                logging.getLogger('programmation').info(
                    f"Programmation {job.get('job').meta.get('programmation_id')} stopped by daemon")
                __pu.terminate_redis_active_download(job.get('id'))

    for programmation in all_programmations:
        prog = Programmation(programmation=programmation)

        found_job = __pu.find_job_by_programmation_id(prog.id)

        must_be_restarted = prog.must_be_restarted()

        if found_job is None:
            next_execution = prog.get_next_execution()

            effective_duration = must_be_restarted
            if effective_duration is None and prog.recording_duration:
                effective_duration = prog.recording_duration

            if effective_duration is not None and prog.recording_stops_at_end:
                programmation_end_date = datetime.now().replace(second=0, microsecond=0) + timedelta(
                    minutes=effective_duration + 1)
            else:
                programmation_end_date = None

            if next_execution is not None:
                will_be_executed = next_execution < datetime.now() + timedelta(seconds=programmation_interval)
            else:
                will_be_executed = True

            if must_be_restarted is not None or will_be_executed:
                if must_be_restarted is not None:
                    effective_programmation_date = datetime.now()
                else:
                    effective_programmation_date = next_execution

                dm = download_manager.DownloadManager(__cm,
                                                      prog.url,
                                                      prog.presets,
                                                      prog.user_token,
                                                      programmation_id=programmation.get.id,
                                                      programmation_end_date=programmation_end_date,
                                                      programmation_date=effective_programmation_date,
                                                      programmation=programmation.get()
                                                      )

                if dm.get_api_status_code() != 400:
                    dm.process_downloads()


if __name__ == '__main__':
    __cm.init_logger(file_name='programmation_daemon.log')

    if not enable_redis:
        logging.getLogger('programmation').warning('Redis disabled, programmation daemon exited')
        exit()

    while True:
        run()
        time.sleep(programmation_interval)
