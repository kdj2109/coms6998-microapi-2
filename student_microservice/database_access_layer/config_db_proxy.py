import boto3
import botocore.exceptions as bce


"""
**********************Possible additions to the code***************************

    1. Does not update object after deleting or adding fields.
    2. Chris --> i think it adds --> checking into deleting

*******************************************************************************
"""


class ConfigDBProxy:
    def __init__(self):
        id = ''
        key = ''

        self.dynamodb = boto3.resource('dynamodb',
                                       region_name='us-west-2',
                                       aws_access_key_id=id,
                                       aws_secret_access_key=key)

        try:
            self.table = self.dynamodb.Table('Student-Schema')
            self.table.table_status  # Check if the table is active
        except bce.ClientError:
            self.__create_table()
            self.__create_initial_schema()

    def get_schema(self):
        response = self.table.get_item(
            Key={
                'schema_id': 'student_schema'
            }
        )

        return response['Item'], 200

    def update(self, fields):
        schema = self.get_schema()

        new_schema = self.__update_schema(fields, schema[0])
        self.table.put_item(Item=new_schema)

        return new_schema, 200

    def delete(self, field):
        schema = self.get_schema()

        return self.__delete_field(field, schema[0])

    def __create_table(self):
        self.dynamodb.create_table(
            TableName='Student-Schema',
            KeySchema=[
                {
                    'AttributeName': 'schema_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'schema_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def __create_initial_schema(self):
        student_schema = {
            'first_name': ['Required', 'String'],
            'last_name': ['Required', 'String'],
            'grade': ['Required', 'Number'],
            'student_id': ['Required', 'String'],
            'schema_id': 'student_schema'
        }

        self.table.put_item(Item=student_schema)

    def __update_schema(self, fields, schema):
        for key, value in fields.items():
            if key not in schema:
                schema[key] = value

        return schema

    def __delete_field(self, field, schema):
        for key in schema:
            if key == field:
                del schema[key]

                self.table.put_item(Item=schema)

                return field + ' deleted.', 200

        return 'Field not found in the schema.', 404









