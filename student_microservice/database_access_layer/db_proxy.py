import boto3
import botocore.exceptions as bce


class DBProxy:
    def __init__(self):
        id = 'AKIAIIWDDOJN5HGP7FVQ'
        key = 'oLXoh8jYr6RKmLuzOl/DzBDxSSFmmntqsu5ATf4z'

        self.dynamodb = boto3.resource('dynamodb',
                                       region_name='us-west-2',
                                       aws_access_key_id=id,
                                       aws_secret_access_key=key)

        try:
            self.table = self.dynamodb.Table('Students')
            self.table.table_status
        except bce.ClientError:
            self.__create_table()

    def query(self, id=None):
        try:
            response = self.table.scan()
        except bce.ClientError as e:
            return str(e), 500

        if len(response['Items']) == 0:
            return 'There are no students in the K-12 database.', 404

        if id is not None:
            for item in response['Items']:
                if item['student_id'] == id:
                    return item, 200

            return 'Student ' + id + ' was not found.', 404

        return response['Items'], 200

    def add(self, dict):
        if self.__item_exists(dict['student_id']):
            return 'You are attempting to overwrite an existing student.', 409

        self.table.put_item(Item=dict)

        return dict, 201

    def update(self, dict, id):
        if not self.__item_exists(id):
            return 'The student ' + id + ' does not exist.', 404

        item = self.__get_item(id)

        update_expression = self.__create_update_expression(dict, item)
        expression_attribute_values = \
            self.__create_expression_attribute_values(dict)

        self.table.update_item(
            Key={
                'student_id': id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        dict['student_id'] = id

        return dict, 200

    def delete(self, id):
        if not self.__item_exists(id):
            return 'The student ' + id + ' does not exist.', 404

        self.table.delete_item(
            Key={
                'student_id': id
            }
        )

        return 'Student ' + id + ' deleted.', 200

    def __create_table(self):
        self.dynamodb.create_table(
            TableName='Students',
            KeySchema=[
                {
                    'AttributeName': 'student_id',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'student_id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def __item_exists(self, id):
        response = self.__get_item(id)

        if response is None:
            return False

        return True

    def __get_item(self, id):
        response = self.table.get_item(
            Key={
                'student_id': id
            }
        )

        if 'Item' in response:
            return response['Item']

        return None

    def __create_update_expression(self, dict, item):
        set_expression = self.__create_set_expression(dict, item)
        remove_expression = self.__create_remove_expression(dict, item)

        if remove_expression == 'REMOVE ':
            return set_expression[:-2]

        # Why is remove_expression truncated by 2 characters?
        return set_expression[:-2] + ' ' + remove_expression
        #return set_expression[:-2] + ' ' + remove_expression[:-2]

    def __create_set_expression(self, dict, item):
        set_expression = 'SET '

        for key, value in dict.items():
            if key == 'student_id':
                continue

            set_expression += str(key) + '=:' + str(key) + ', '

        return set_expression

    def __create_remove_expression(self, dict, item):
        remove_expression = 'REMOVE '

        for key, value in item.items():
            if key not in dict:
                remove_expression += key

        return remove_expression

    def __create_expression_attribute_values(self, dict):
        expression_attribute_values = {}

        for key, value in dict.items():
            if key == 'student_id':
                continue

            expression_attribute_values[':' + key] = value

        return expression_attribute_values
