import boto3
import botocore.exceptions as bce
import sys
import os
from student_microservice.data_access_layer import config_dao as cdao
import time
import datetime
import ast
import json
from student_microservice.decoder import decimal_encoder as decimal_encoder

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class SQSSchemaConsumer:
    def __init__(self):


        self.sqs = boto3.resource('sqs',
                                  region_name='us-west-2',
                                  aws_access_key_id=id,
                                  aws_secret_access_key=key)

        self.in_queue = self.__get_queue('Student-Input')
        self.out_queue = self.__get_queue('Student-Output')
        self.dao = cdao.ConfigDAO()

        while 1:
            now = datetime.datetime.now()
            print("Looking for messages at " + now.isoformat())

            for message in self.in_queue.receive_messages(MessageAttributeNames
                                                          =['Schema']):
                self.__process_message(message)

            time.sleep(20)

    def __get_queue(self, queue_name):
        try:
            return self.sqs.get_queue_by_name(QueueName=queue_name)
        except bce.ClientError:
            return self.sqs.create_queue(QueueName=queue_name)

    def __process_message(self, message):
        now = datetime.datetime.now()
        print("Processing message at " + now.isoformat())
        print(message)

        if self.__bad_formatted_message(message):
            message.delete()
            return

        action = message.message_attributes.get('Schema') \
            .get('StringValue')

        if action.upper() == 'GET SCHEMA':
            self.__process_get(message)
        elif action.upper() == 'ADD FIELDS':
            self.__process_post(message)
        else:
            self.__process_delete(message)

        message.delete()

    def __bad_formatted_message(self, message):
        if self.__bad_formatted_message_attributes(message):
            return True

        return False

    def __bad_formatted_message_attributes(self, message):
        if message.message_attributes is None:
            return True

        if message.message_attributes.get('Schema').get('StringValue') \
                is None:
            return True

        actions = ['ADD FIELDS', 'DELETE FIELD', 'GET SCHEMA']
        action = message.message_attributes.get('Schema') \
            .get('StringValue')

        if any([action.upper() == act for act in actions]):
            return False

        return True

    def __process_get(self, message):
        response = self.dao.get_schema()

        self.__send_message(response, message)

    def __process_post(self, message):
        if self.__bad_formatted_message_body(message.body):
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.add_fields(ast.literal_eval(message.body))

        self.__send_message(response, message)

    def __process_delete(self, message):
        if message.body is None:
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.delete_field(message.body)

        self.__send_message(response, message)

    def __send_message(self, response, message):
        now = datetime.datetime.now()

        print("Sending message at " + now.isoformat())
        print(response)

        message_body = json.dumps(response[0],
                                  indent=4,
                                  cls=decimal_encoder.DecimalEncoder)

        message_attributes = {
            'HTTPStatusCode': {
                'StringValue': str(response[1]),
                'DataType': 'Number'
            },
            'Correlation_Id': {
                'StringValue': message.message_id,
                'DataType': 'String'
            }
        }

        self.out_queue.send_message(MessageBody=message_body,
                                    MessageAttributes=message_attributes)

    def __bad_formatted_message_body(self, message_body):
        if message_body is None:
            return True

        try:
            json = ast.literal_eval(message_body)
        except SyntaxError:
            return True

        if not self.__valid_fields(json):
            return True

        return False

    def __send_bad_formatted_message(self, message):
        message_body = 'The following message: ' + message.message_id + \
                        ' could not be processed because the format is ' \
                        'incorrect.'

        message_attributes = {
            'HTTPStatusCode': {
                'StringValue': '400',
                'DataType': 'Number'
            },
            'Correlation_Id': {
                'StringValue': message.message_id,
                'DataType': 'String'
            }
        }

        self.out_queue.send_message(MessageBody=message_body,
                                    MessageAttribute=message_attributes)

    def __valid_fields(self, json):
        for value in json.values():
            if type(value) is dict:
                return self.__valid_fields(value)
            if value[0].upper() != 'REQUIRED' and value.upper() != 'OPTIONAL':
                return False
            if value[1].upper() != 'STRING' and value[1].upper() != 'NUMBER':
                return False

        return True

sqs_schema_consumer = SQSSchemaConsumer()