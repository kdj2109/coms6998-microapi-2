import random
import database_access_layer.db_proxy as db_proxy
import uuid


class DAO:
    def __init__(self):
        self.db_proxy = db_proxy.DBProxy()

    def query(self, id=None):
        return self.db_proxy.query(id)

    def add(self, dict):
        if 'student_id' not in dict:
            dict['student_id'] = self.__create_id()

        return self.db_proxy.add(dict)

    def update(self, dict, id):
        return self.db_proxy.update(dict, id)

    def delete(self, id):
        return self.db_proxy.delete(id)

    def __create_id(self):
        return str(uuid.uuid4())



