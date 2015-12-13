import random
import database_access_layer.db_proxy as db_proxy


class DAO:
    def __init__(self):
        self.db_proxy = db_proxy.DBProxy()

    def query(self, id=None):
        return self.db_proxy.query(id)

    def add(self, dict):
        if 'middle_name' not in dict:
            dict['id'] = self.__create_id(dict['first_name'],
                                          dict['last_name'])
        else:
            dict['id'] = self.__create_id(dict['first_name'],
                                          dict['last_name'],
                                          dict['middle_name'])

        return self.db_proxy.add(dict)

    def update(self, dict, grade, id):
        return self.db_proxy.update(dict, grade, id)

    def delete(self, grade, id):
        return self.db_proxy.delete(grade, id)

    def __create_id(self, first_name, last_name, middle_name=None):
        id = first_name[0].lower()
        number = str(random.randint(1000, 9999))

        if middle_name is None:
            id += last_name[0].lower() + number
        else:
            id += middle_name[0].lower() + last_name[0].lower() + number

        return id


