from flask import Flask, request
import argparse
import data_access_layer.dao as dao
import json
import decoder.decimal_encoder as decimal_decoder

# Create instance of application to receive requests from server
app = Flask(__name__)

# Name of the microservice
microservice_name = 'finance'

app_dao = dao.DAO()

decimal_decoder = decimal_decoder.DecimalEncoder


@app.route('/' + microservice_name, methods=['GET'])
@app.route('/' + microservice_name + '/<id>', methods=['GET'])
def get(id=None):
    response = app_dao.query(id)

    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name, methods=['POST'])
def post():
    json_dict = request.get_json()

    if not valid_json(json_dict):
        return bad_request('Invalid finance student format.')

    response = app_dao.add(json_dict)

    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/<tenant>/<id>', methods=['PUT'])
def put(tenant, id):
    json_dict = request.get_json()

    if not valid_json(json_dict):
        return bad_request('Invalid finance student format.')

    response = app_dao.update(json_dict, tenant, id)

    if response[1] > 299:
        return response

    return json.dumps(response[0], indent=4, cls=decimal_decoder), response[1]


@app.route('/' + microservice_name + '/<tenant>/<id>', methods=['DELETE'])
def delete(tenant, id):
    response = app_dao.delete(tenant, id)

    return response


def valid_json(json_dict):
    if all(key in json_dict for key in ('first_name', 'last_name', 'tenant')):
        if 0 <= int(json_dict['tenant']) <= 12:
            return True

    return False


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
