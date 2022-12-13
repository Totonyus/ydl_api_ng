import copy
import logging

import defaults
import uuid
from tinydb import TinyDB, Query
from cronsim import CronSim
from datetime import datetime, timedelta


class ProgrammationManager:
    def __init__(self, database_file=None, *args, **kwargs):
        self.__database_file = database_file if database_file is not None else 'database.json'

        self.__db = TinyDB(self.__database_file)
        self.__scheduled_jobs_table = self.__db.table('scheduled_jobs', cache_size=0)

    @staticmethod
    def generate_identifier(*args, **kwargs):
        return f'{uuid.uuid4()}'

    # Add values that wasn't provided in request
    def generate_programmation(self, source_programmation=defaults.programmation_object_default, programmation=None,
                               *args, **kwargs):
        full_programmation = copy.deepcopy(source_programmation)

        for entry, value in programmation.items():
            if entry == 'planning':
                for planning_entry, planning_value in value.items():
                    full_programmation[entry][planning_entry] = planning_value
            else:
                full_programmation[entry] = value

        full_programmation['id'] = self.generate_identifier()

        return full_programmation

    def add_programmation(self, programmation=None, *args, **kwargs):
        generated_programmation = self.generate_programmation(programmation=programmation)
        programmation_validation_result = self.validate_programmation(generated_programmation)

        if len(programmation_validation_result) != 0:
            return programmation_validation_result, None
        else:
            self.__scheduled_jobs_table.insert(generated_programmation)
            return programmation_validation_result, generated_programmation

    def validate_programmation(self, programmation=None, *args, **kwargs):
        errors_list = []

        date_controls = ['recurrence_start_date', 'recurrence_end_date', 'recording_start_date']

        for field in date_controls:
            if programmation.get('planning').get(field) is not None:
                try:
                    datetime.fromisoformat(programmation.get('planning').get(field))
                except Exception as error:
                    errors_list.append(
                        {'field': field, 'value': programmation.get('planning').get(field), 'error': f'{error}'})

        if programmation.get('url') is None or programmation.get('url') == '':
            errors_list.append({'field': 'url', 'error': 'url is empty'})

        if type(programmation.get('planning').get('recording_stops_at_end')) != bool:
            errors_list.append({'field': 'recording_stops_at_end', 'error': 'must be a boolean'})

        if type(programmation.get('enabled')) != bool:
            errors_list.append({'field': 'enabled', 'error': 'must be a boolean'})

        if programmation.get('presets') is not None and type(programmation.get('presets')) != list:
            errors_list.append({'field': 'presets', 'error': 'must be None or list'})

        if programmation.get('planning').get('recording_duration') is not None:
            if type(programmation.get('planning').get('recording_duration')) != int:
                errors_list.append({'field': 'recording_duration', 'error': 'must be None or int'})
            if type(programmation.get('planning').get('recording_duration')) == int and programmation.get(
                    'planning').get('recording_duration') < 1:
                errors_list.append(
                    {'field': 'recording_duration', 'value': programmation.get('planning').get('recording_duration'),
                     'error': 'must be greater than 0'})

        if programmation.get('planning').get('recurrence_cron') is not None and programmation.get('planning').get(
                'recording_start_date') is not None:
            errors_list.append({'field': 'recurrence_cron', 'error': 'cannot be use with recording_start_date field'})
            errors_list.append({'field': 'recording_start_date', 'error': 'cannot be use with recurrence_cron field'})

        try:
            if programmation.get('planning').get('recurrence_cron') is not None:
                cron = CronSim(programmation.get('planning').get('recurrence_cron'), datetime.now())

                if programmation.get('planning').get('recurrence_start_date') is None:
                    programmation.get('planning')['recurrence_start_date'] = datetime.isoformat(next(cron), sep=' ')

        except Exception as e:
            errors_list.append(
                {'field': 'recurrence_cron', 'value': programmation.get('planning').get('recurrence_cron'),
                 'error': f'{e}'})

        return errors_list

    def get_all_programmations(self, *args, **kwargs):
        return self.__scheduled_jobs_table.all()

    def get_all_enabled_programmations(self, *args, **kwargs):
        return self.__scheduled_jobs_table.search(Query().enabled == True)

    def get_programmation_by_id(self, id=None, *args, **kwargs):
        result = self.__scheduled_jobs_table.search(Query().id == id)
        return result if len(result) != 0 else None

    def get_programmation_by_url(self, url=None, *args, **kwargs):
        result = self.__scheduled_jobs_table.search(Query().url == url)
        return result if len(result) != 0 else None

    def delete_programmation_by_id(self, id=None, *args, **kwargs):
        ret = self.get_programmation_by_id(id=id)
        self.__scheduled_jobs_table.remove(Query().id == id)
        return ret

    def delete_programmation_by_url(self, url=None, *args, **kwargs):
        ret = self.get_programmation_by_url(url=url)
        self.__scheduled_jobs_table.remove(Query().url == url)

        return ret

    def get_all_from_date(self, from_date=None, *args, **kwargs):
        from_date = datetime.now() if from_date is None else from_date

        all_programmations = self.get_all_programmations()
        programmations = []

        for programmation in all_programmations:
            end_date = self.get_end_date(programmation)
            if end_date is not None and from_date > end_date:
                programmations.append(programmation)

        return programmations

    def get_end_date(self, programmation=None, *args, **kwargs):
        planning = programmation.get('planning')

        recording_start_date = planning.get('recording_start_date')
        recording_duration = planning.get('recording_duration')
        recurrence_cron = planning.get('recurrence_cron')
        recurrence_start_date = planning.get('recurrence_start_date')
        recurrence_end_date = planning.get('recurrence_end_date')

        end_date = None

        if planning is None:
            return None

        if recurrence_end_date is None and recording_start_date is not None and recording_duration is not None:
            end_date = datetime.fromisoformat(recording_start_date) + timedelta(minutes=recording_duration)

        elif recurrence_end_date is None and recording_start_date is not None:
            end_date = datetime.fromisoformat(recording_start_date)

        elif recurrence_end_date is not None and recurrence_cron is not None:
            end_date = datetime.fromisoformat(recurrence_start_date)

            cron = CronSim(recurrence_cron, datetime.fromisoformat(recurrence_start_date))
            next_iteration = next(cron)

            while next_iteration < datetime.fromisoformat(recurrence_end_date):
                end_date = next_iteration
                next_iteration = next(cron)

            if recording_duration is not None:
                end_date = end_date + timedelta(minutes=recording_duration)

        elif recurrence_end_date is not None and recording_duration is not None:
            end_date = datetime.fromisoformat(recurrence_end_date) + timedelta(minutes=recording_duration)

        elif recurrence_end_date is not None:
            end_date = datetime.fromisoformat(recurrence_end_date)

        return end_date

    def update_programmation_by_id(self, id=None, programmation=None, *args, **kwargs):
        stored_programmation = self.get_programmation_by_id(id)[0]

        if stored_programmation is None:
            return None

        changed_programmation = self.generate_programmation(source_programmation=stored_programmation,
                                                            programmation=programmation)
        validation_result = self.validate_programmation(programmation=changed_programmation)
        changed_programmation['id'] = stored_programmation.get('id')

        if len(validation_result) != 0:
            return validation_result, None
        else:
            self.__scheduled_jobs_table.update(changed_programmation, Query().id == stored_programmation.get('id'))
            return validation_result, changed_programmation

    def purge_all_past_programmations(self, from_date=None, *args, **kwargs):
        from_date = datetime.now() if from_date is None else from_date

        programmations = self.get_all_from_date(from_date=from_date)

        for programmation in programmations:
            self.delete_programmation_by_id(programmation.get('id'))

        return programmations

    def get_next_execution(self, programmation=None, from_date=None, *args, **kwargs):
        from_date = datetime.now() if from_date is None else from_date
        planning = programmation.get('planning')

        recording_start_date = planning.get('recording_start_date')
        recurrence_cron = planning.get('recurrence_cron')
        recurrence_start_date = planning.get('recurrence_start_date')

        next_iteration = None
        if recording_start_date is not None:
            next_iteration = datetime.fromisoformat(recording_start_date)

        if recurrence_cron is not None:
            cron = CronSim(recurrence_cron, from_date - timedelta(minutes=1))

            next_iteration = next(cron)

            while next_iteration < datetime.fromisoformat(recurrence_start_date):
                next_iteration = next(cron)

        # If None, must launch it immediately
        return next_iteration

    def must_be_restarted(self, programmation=None, from_date=None, *args, **kwargs):
        from_date = datetime.now() if from_date is None else from_date
        planning = programmation.get('planning')

        recording_start_date = planning.get('recording_start_date')
        recording_duration = planning.get('recording_duration')
        recurrence_cron = planning.get('recurrence_cron')
        recurrence_start_date = planning.get('recurrence_start_date')

        if recording_duration is None:
            return None
        elif recording_start_date is not None:
            start_date = datetime.fromisoformat(recording_start_date)
        elif recurrence_start_date is not None and recording_duration is not None:
            start_date = next(CronSim(recurrence_cron, from_date - timedelta(minutes=recording_duration)))
        else:
            return None

        if start_date < from_date < start_date + timedelta(minutes=recording_duration):
            return int((start_date + timedelta(minutes=recording_duration) - from_date).seconds / 60)
        else:
            return None
