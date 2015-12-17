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
            self.table = self.dynamodb.Table('Finance-Students')
            self.table.table_status
        except bce.ClientError:
            self.__create_table()

    def query(self, id=None):
        try:
            response = self.table.scan()
        except bce.ClientError as e:
            return str(e), 500

        if len(response['Items']) == 0:
            return 'There are no students in the finance database.', 404

        if id is not None:
            for item in response['Items']:
                if item['id'] == id:
                    return item, 200

            return 'Student ' + id + ' was not found.', 404

        return response['Items'], 200

    def add(self, dict):
        if self.__item_exists(dict['tenant'], dict['id']):
            return 'You are attempting to overwrite an existing student.', 409

        self.table.put_item(Item=dict)

        return dict, 201

    def update(self, dict, tenant, id):
        if not self.__item_exists(tenant, id):
            return 'The student ' + id + ' does not exist.', 404

        item = self.__get_item(tenant, id)

        update_expression = self.__create_update_expression(dict, item)
        expression_attribute_values = \
            self.__create_expression_attribute_values(dict)

        self.table.update_item(
            Key={
                'tenant': tenant,
                'id': id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        return dict, 200

    def delete(self, tenant, id):
        if not self.__item_exists(tenant, id):
            return 'The student ' + id + ' does not exist.', 404

        self.table.delete_item(
            Key={
                'tenant': tenant,
                'id': id
            }
        )

        return 'Student ' + id + ' deleted.', 204

    def __create_table(self):
        self.dynamodb.create_table(
            TableName='Students',
            KeySchema=[
                {
                    'AttributeName': 'tenant',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'id',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'tenant',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    def __item_exists(self, tenant, id):
        response = self.__get_item(tenant, id)

        if response is None:
            return False

        return True

    def __get_item(self, tenant, id):
        response = self.table.get_item(
            Key={
                'tenant': tenant,
                'id': id
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

        return set_expression[:-2] + ' ' + remove_expression[:-2]

    def __create_set_expression(self, dict, item):
        set_expression = 'SET '

        for key, value in dict.items():
            if key == 'id' or key == 'tenant':
                continue

            set_expression += str(key) + '=:' + str(key) + ', '

        return set_expression

    def __create_remove_expression(self, dict, item):
        remove_expression = 'Remove '

        for key, value in item.items():
            if key not in dict:
                remove_expression += key

        return remove_expression

    def __create_expression_attribute_values(self, dict):
        expression_attribute_values = {}

        for key, value in dict.items():
            if key == 'tenant' or key == 'id':
                continue

            expression_attribute_values[':' + key] = value

        return expression_attribute_values







