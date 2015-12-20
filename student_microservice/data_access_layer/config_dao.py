from student_microservice.database_access_layer import config_db_proxy as cdbp


class ConfigDAO:
    def __init__(self):
        self.db_proxy = cdbp.ConfigDBProxy()

    def get_schema(self):
        return self.db_proxy.get_schema()

    def add_fields(self, fields):
        return self.db_proxy.update(fields)

    def delete_field(self, field):
        return self.db_proxy.delete(field)