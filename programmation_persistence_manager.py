from tinydb import TinyDB, Query
from datetime import datetime
from programmation_class import Programmation


class ProgrammationPersistenceManager:
    def __init__(self, database_file=None, *args, **kwargs):
        self.__database_file = database_file if database_file is not None else 'data/database.json'

        self.__db = TinyDB(self.__database_file)
        self.__scheduled_jobs_table = self.__db.table('scheduled_jobs', cache_size=0)

    def add_programmation(self, programmation=None, *args, **kwargs):
        if self.get_programmation_by_id(id=programmation.id) is not None:
            programmation.errors.append({'field': 'id', 'error': 'a programmation with this id aleady exists'})

        if len(programmation.errors) != 0:
            return None

        self.__scheduled_jobs_table.insert(programmation.get())
        return programmation

    def get_all_programmations(self, *args, **kwargs):
        return self.__scheduled_jobs_table.all()

    def get_all_enabled_programmations(self, *args, **kwargs):
        return self.__scheduled_jobs_table.search(Query().enabled == True)

    def get_programmation_by_id(self, id=None, json=False, *args, **kwargs):
        result = self.__scheduled_jobs_table.search(Query().id == id)

        if json:
            ret = result[0] if len(result) != 0 else None
        else:
            ret = Programmation(programmation=result[0], id=result[0].get('id')) if len(result) != 0 else None

        return ret

    def get_programmation_by_url(self, url=None, *args, **kwargs):
        result = self.__scheduled_jobs_table.search(Query().url == url)
        return result if len(result) != 0 else None

    def delete_programmation_by_id(self, id=None, *args, **kwargs):
        ret = self.get_programmation_by_id(id=id, json=True)
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
            programmation_object = Programmation(programmation=programmation, id=programmation.get('id'))

            end_date = programmation_object.get_end_date()
            if end_date is not None and from_date > end_date:
                programmations.append(programmation)

        return programmations

    def update_programmation_by_id(self, id=None, programmation=None, *args, **kwargs):
        stored_programmation = self.get_programmation_by_id(id, json=True)

        if stored_programmation is None:
            return None

        effective_id = programmation.get('id')

        if effective_id is None:
            effective_id = stored_programmation.get('id')

        changed_programmation = Programmation(source_programmation=stored_programmation,
                                              programmation=programmation, id=effective_id)
        validation_result = changed_programmation.errors

        if effective_id != stored_programmation.get('id') and self.get_programmation_by_id(id=changed_programmation.id) is not None:
            validation_result.append({'field': 'id', 'error': 'a programmation with this id aleady exists'})

        if len(validation_result) == 0:
            self.__scheduled_jobs_table.update(changed_programmation.get(),
                                               Query().id == stored_programmation.get('id'))

        return changed_programmation

    def purge_all_past_programmations(self, from_date=None, *args, **kwargs):
        from_date = datetime.now() if from_date is None else from_date

        programmations = self.get_all_from_date(from_date=from_date)

        for programmation in programmations:
            self.delete_programmation_by_id(programmation.get('id'))

        return programmations
