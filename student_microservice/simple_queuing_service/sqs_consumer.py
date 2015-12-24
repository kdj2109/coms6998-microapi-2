import boto3
import botocore.exceptions as bce
import sys
import os
from student_microservice.data_access_layer import dao as dao
from student_microservice.data_access_layer import config_dao as cdao
import time
import datetime
import ast
import json
from student_microservice.decoder import decimal_encoder as decimal_encoder

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))


class SQSConsumer:
    def __init__(self):


        self.sqs = boto3.resource('sqs',
                                  region_name='us-west-2',
                                  aws_access_key_id=id,
                                  aws_secret_access_key=key)

        self.in_queue = self.__get_queue('Student-Input')
        self.out_queue = self.__get_queue('Student-Output')
        self.dao = dao.DAO()
        self.cdao = cdao.ConfigDAO()

        while 1:
            now = datetime.datetime.now()
            print("Looking for messages at " + now.isoformat())

            for message in self.in_queue.receive_messages(MessageAttributeNames
                                                          =['RESTVerb', 'id']):
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
        print(message.message_attributes)

        if self.__bad_formatted_message(message):
            message.delete()
            return

        rest_verb = message.message_attributes.get('RESTVerb') \
            .get('StringValue')

        if rest_verb.upper() == 'GET':
            self.__process_get_request(message)
        elif rest_verb.upper() == 'POST':
            self.__process_post_request(message)
        elif rest_verb.upper() == 'PUT':
            self.__process_put_request(message)
        else:
            self.__process_delete_request(message)

        message.delete()

    def __bad_formatted_message(self, message):
        if self.__bad_formatted_message_attributes(message):
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
                                    MessageAttributes=message_attributes)

    def __bad_formatted_message_attributes(self, message):
        if message.message_attributes is None:
            return True

        if message.message_attributes.get('RESTVerb').get('StringValue') \
                is None:
            return True

        rest_verbs = ['GET', 'POST', 'PUT', 'DELETE']
        rest_verb = message.message_attributes.get('RESTVerb') \
            .get('StringValue')

        if any([rest_verb.upper() == rb for rb in rest_verbs]):
            return False

        return True

    def __bad_formatted_message_body(self, message_body):
        if message_body is None:
            return True

        try:
            json = ast.literal_eval(message_body)
        except SyntaxError:
            return True

        return False

    def __process_get_request(self, message):
        id = None
        print(message.message_attributes)
        if message.message_attributes.get('id') is not None:
            id = message.message_attributes.get('id').get('StringValue')

        response = self.dao.query(id)

        self.__send_message(response, message)

    def __process_post_request(self, message):
        if self.__bad_formatted_message_body(message.body):
            self.__send_bad_formatted_message(message)
            return

        if not self.__valid_json(ast.literal_eval(message.body), 'POST'):
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.add(ast.literal_eval(message.body))

        self.__send_message(response, message)

    def __process_put_request(self, message):
        id = self.__get_keys(message)

        if self.__bad_formatted_message_body(message.body) or id is None:
            self.__send_bad_formatted_message(message)
            return

        if not self.__valid_json(ast.literal_eval(message.body), 'PUT'):
            print('invalid json')
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.update(ast.literal_eval(message.body), id)

        self.__send_message(response, message)

    def __process_delete_request(self, message):
        id = self.__get_keys(message)

        if id is None:
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.delete(id)

        self.__send_message(response, message)

    def __get_keys(self, message):
        id = None

        if message.message_attributes.get('id') is not None:
            id = message.message_attributes.get('id').get('StringValue')

        return id

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

    def __valid_json(self, json_dict, method):
        schema = self.cdao.get_schema()

        for key, value in schema[0].items():
            # Dynamodb partition key
            if key == 'schema_id':
                continue

            # POST Json does not have to include a student_id
            if method == 'POST' and key == 'student_id':
                continue

            has_key = False

            # Determine if the key is in the json_dict
            if key in json_dict:
                v = json_dict[key]

                # Make sure the grade is K-12
                if key == 'grade' and (v < 0 or v > 12):
                    return False

                # Check if the value is correct
                if self.__correct_value(value, v):
                    has_key = True

            # Json format is invalid
            if not has_key and value[0] == 'Required':
                return False

        return True

    def __correct_value(self, value, v):
        if value[1] == 'String' and type(v) != str:
            return False

        if value[1] == 'Number' and (type(v) != int and type(v) != float):
            return False

        return True


consumer = SQSConsumer()