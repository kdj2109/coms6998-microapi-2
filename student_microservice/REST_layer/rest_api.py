from flask import Flask, request
import argparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from student_microservice.data_access_layer import dao
import json
from student_microservice.decoder import decimal_encoder
from student_microservice.data_access_layer import config_dao as cd

# Create instance of application to receive requests from server
app = Flask(__name__)

# Name of the microservice
microservice_name = 'student'

app_dao = dao.DAO()
app_config_dao = cd.ConfigDAO()

decimal_decoder = decimal_encoder.DecimalEncoder

@app.route('/')
def hello():
    return "Hello World"

@app.route('/' + microservice_name, methods=['GET'])
@app.route('/' + microservice_name + '/<id>', methods=['GET'])
def get(id=None):
    """Gets all of the students if id is None and the student with the id"""

    response = app_dao.query(id)

    # HTTP code sent from dao indicates an error
    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name, methods=['POST'])
def post():
    """Posts a new student"""

    json_dict = request.get_json()

    # The request did not come with a Json
    if json_dict is None:
        return bad_request('Json object was not sent with request.')

    # POST
    method = request.method

    # Checks the Json object against the student schema
    if not valid_json(json_dict, method):
        return bad_request('Invalid student format.')

    response = app_dao.add(json_dict)

    # HTTP code sent from dao indicates an error
    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/<id>', methods=['PUT'])
def put(id):
    """Edits a student object -- entire student object with deleted, edited,
    and/or additional fields must be sent with the request"""

    json_dict = request.get_json()

    # The request did not come with a Json
    if json_dict is None:
        return bad_request('Json object was not sent with request.')

    # PUT
    method = request.method

    # Checks the Json object against the student schema
    if not valid_json(json_dict, method):
        return bad_request('Invalid student format.')

    response = app_dao.update(json_dict, id)

    # HTTP code sent from dao indicates an error
    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/<id>', methods=['DELETE'])
def delete(id):
    """Deletes the student with the given id"""

    response = app_dao.delete(id)

    return response


@app.route('/' + microservice_name + '/admin/student_schema', methods=['GET'])
def get_schema():
    """Gets the current student schema"""

    response = app_config_dao.get_schema()

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/admin/configure', methods=['POST'])
def add_fields():
    """Adds the fields in the Json of the request to the student schema"""

    json_dict = request.get_json()

    # The request did not come with a Json
    if json_dict is None:
        return bad_request('Json object was not sent with request.')

    # Checks if the fields in the Json are correctly formatted
    if not valid_fields(json_dict):
        return bad_request('Configuring json is incorrect.')

    response = app_config_dao.add_fields(json_dict)

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/admin/configure/<field>',
           methods=['DELETE'])
def delete_field(field):
    """Deletes the field from the student schema"""

    # student_id is the key in Dynamodb
    if field == 'student_id':
        return bad_request('You cannot delete the key.')

    return app_config_dao.delete_field(field)


def valid_fields(json_dict):
    """A valid field consists of an array of length 2:

    Index 1: 'Required' or 'Optional'
    Index 2: 'String' or 'Number'

    **********************Possible additions to the code***********************

    1. Index 2 can possibly more object types (list, etc.)

    ***************************************************************************
    """

    for value in json_dict.values():
        if type(value) is dict:
            return valid_fields(value)
        if value[0].upper() != 'REQUIRED' and value[0].upper() != 'OPTIONAL':
            return False
        if value[1].upper() != 'STRING' and value[1].upper() != 'NUMBER':
            return False

    return True


def valid_json(json_dict, method):
    """Checks if the Json sent with the POST or PUT request is valid

    **********************Possible additions to the code***********************

    1. Does not handle if the field is a dict

    ***************************************************************************
    """

    # Gets the student schema, index 0 is the schema, index 1 is the HTTP code
    schema = app_config_dao.get_schema()

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
            if key == 'grade' and 0 >= v >= 12:
                return False

            # POST Json does not have to include a student_id
            if method == 'POST' and key == 'student_id':
                continue

            # Check if the value is correct
            if correct_value(value, v):
                has_key = True
                break

        # Json format is invalid
        if not has_key and value[0] == 'Required':
            return False

    return True


def correct_value(value, v):
    """Determines if the values are correct

    **********************Possible additions to the code***********************

    1. Additional object types

    ***************************************************************************
    """

    if value[1] == 'String' and type(v) != str:
        return False

    if value[1] == 'Number' and (type(v) != int and type(v) != float):
        return False

    return True


@app.errorhandler(404)
def page_not_found(e):
    return e, 404


@app.errorhandler(400)
def bad_request(e):
    return e, 400

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="The port number to launch.")
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=int(port), debug=True)
