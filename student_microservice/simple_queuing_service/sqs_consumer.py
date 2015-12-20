import boto3
import botocore.exceptions as bce
from student_microservice.data_access_layer import dao as dao
import time
import ast
import json
from student_microservice.decoder import decimal_encoder as decimal_encoder

"""
**********************Possible additions to the code***************************

    1. Can change the subscription from 'RESTVerb'
    2. Does not currently handle schema change requests -- I would create
       a new SQS consumer for this.

*******************************************************************************
"""


class SQSConsumer:
    def __init__(self):
        id = 'AKIAIIWDDOJN5HGP7FVQ'
        key = 'oLXoh8jYr6RKmLuzOl/DzBDxSSFmmntqsu5ATf4z'

        self.sqs = boto3.resource('sqs',
                                  region_name='us-west-2',
                                  aws_access_key_id=id,
                                  aws_secret_access_key=key)

        self.in_queue = self.__get_queue('Student-Input')
        self.out_queue = self.__get_queue('Student-Output')
        self.dao = dao.DAO()

        self.in_queue.send_message(MessageBody='test', MessageAttributes={
            'RESTVerb': {
                'StringValue': 'GET',
                'DataType': 'String'
            }
        })

        while 1:
            for message in self.in_queue.receive_messages(MessageAttributeNames
                                                          =['RESTVerb']):
                self.__process_message(message)

            time.sleep(10)

    def __get_queue(self, queue_name):
        try:
            return self.sqs.get_queue_by_name(QueueName=queue_name)
        except bce.ClientError:
            return self.sqs.create_queue(QueueName=queue_name)

    def __process_message(self, message):
        if self.__bad_formatted_message(message):
            message.delete()
            return

        rest_verb = message.message_attributes.get('RESTVerb')\
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
            }
        }

        self.out_queue.send_message(MessageBody=message_body,
                                    MessageAttributeS=message_attributes)

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

        if message.message_attributes.get('id') is not None:
            id = message.message_attributes.get('id').get('StringValue')

        response = self.dao.query(id)

        self.__send_message(response)

    def __process_post_request(self, message):
        if self.__bad_formatted_message_body(message.message_body):
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.add(message.message_body)

        self.__send_message(response)

    def __process_put_request(self, message):
        id, grade = self.__get_keys(message)

        if self.__bad_formatted_message_body(message.message_body) \
                or id is None or grade is None :
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.update(message.message_body, grade, id)

        self.__send_message(response)

    def __process_delete_request(self, message):
        id, grade = self.__get_keys(message)

        if grade is None or id is None:
            self.__send_bad_formatted_message(message)
            return

        response = self.dao.delete(grade, id)

        self.__send_bad_formatted_message(response)

    def __get_keys(self, message):
        id, grade = None, None

        if message.message_attributes.get('id') is not None:
            id = message.message_attributes.get('id').get('StringValue')

        if message.message_attributes.get('grade') is not None:
            grade = message.message_attributes.get('grade').get('StringValue')

        return id, grade

    def __send_message(self, response):
        print(response)
        message_body = json.dumps(response[0],
                                  indent=4,
                                  cls=decimal_encoder.DecimalEncoder)

        message_attributes = {
            'HTTPStatusCode': {
                'StringValue': str(response[1]),
                'DataType': 'Number'
            }
        }

        self.out_queue.send_message(MessageBody=message_body,
                                    MessageAttributes=message_attributes)

