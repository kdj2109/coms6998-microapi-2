# COMS 6998 Project 2

# Requirements
The student microservice requires Python 3.

# Installation
1. Create a virtualenv environment in the top level directory (the directory that contains `student_microservice`.

    `$ virtualenv -p python3 venv`
2. Activate the virtualenv.
    
    `$ source venv/bin/activate`
2. Install the requirements using pip.

    `(venv) $ pip install -r requirements.txt`

# Operation
There are two servers/python scripts that must run:
* HTTP REST API
* SQS consumer

1. Enter the student microservice directory.

    `(venv) $ cd student_microservice`
2. Start the HTTP REST API server by running `rest_api.py` with a port parameter.

    `(venv) $ python REST_layer/rest_api.py PORT`
3. Start the SQS student consumer by running `sqs_consumer.py`
 
    `(venv) $ python simple_queuing_service/sqs_consumer.py`

# API
## REST

* `GET` /student : retrieve all students
* `GET` /student/{id} : retrieve student with {id}
* `POST` /student : add student
* `PUT` /student/{id} : update a student
* `DELETE` /student/{id} : delete a student

## SQS
You can CRUD operations through SQS. The REST verb and REST URL parameters are sent as message attributes. The HTTP 
request body is the SQS message body.

# Examples

## Student REST API
This assumes that the microservice is running on port 8000.

Note: When making update, delete, or create requests you must set the `Content-Type` header to `application/json`.

### Get all students
* Prototype: `GET http://localhost:8000/student`
* Example: `GET http://localhost:8000/student`

### Get a particular student
* Prototype: `GET http://localhost:8000/student/{id}`
* Example: `GET http://localhost:8000/student/2b31cefe-6cd1-4ca5-954e-e84ab7f31be7`

### Add a student
* Prototype: `POST http://localhost:8000/student`
* Example: `POST http://localhost:8000/student`
```
{
    "last_name": "Chan",
    "first_name": "Christopher",
    "grade": 11
}
```

The request returns a JSON object with a response like:
```
{
    "last_name": "Chan",
    "first_name": "Christopher",
    "grade": 11,
    "student_id": "62f46de3-be25-4f90-acac-cf9815b5b515"
}
```

You cannot create a student more than once. If you try to do so you will receive an error.

### Update a student
* Prototype: `PUT http://localhost:8000/student/{id}`
* Example: `PUT http://localhost:8000/student/2b31cefe-6cd1-4ca5-954e-e84ab7f31be7`

With the entire object:
```
{
    "last_name": "Jackson",
    "student_id": "2b31cefe-6cd1-4ca5-954e-e84ab7f31be7",
    "course": [
        "coms-e6998",
        "coms-w4170",
        "engi-e1006",
        "coms-w4710"
    ],
    "first_name": "Kyle",
    "grade": 12,
    "middle_name": "David"
}
```

### Remove a student
After creating a student, you can delete it by calling:
* Prototype: `DELETE http://localhost:8000/student/{id}`
* Example: `DELETE http://localhost:8000/student/2b31cefe-6cd1-4ca5-954e-e84ab7f31be7`

After you delete a particular student, you will receive an error message if the student no longer exists.

## Student config API

### Get the schema
* Prototype: `GET http://localhost:8000/student/admin/student_schema`

### Add a field to the schema
* Prototype: `POST http://localhost:8000/student/admin/configure`
* Example: `POST http://localhost:8000/student/admin/configure`
You can pass in `Required` or `Optional` and `String` or `Number`.

```
{
    "school_city": [
        "Required",
        "String"
    ]
}
```

### Delete a field from the schema
* Prototype: `DELETE http://localhost:8000/student/admin/configure/{field_name}`
* Example: `DELETE http://localhost:8000/student/admin/configure/school_address`

## SQS
For SQS operations you can use the AWS CLI. 

### Get students
`$ aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/714298587391/Student-Input --message-attributes '{"RESTVerb" : {"DataType":"String", "StringValue":"GET"}}' --message-body "{}"`

### Get a student
To get a student, you must pass an id message attribute.
`$ aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/714298587391/Student-Input --message-attributes '{"RESTVerb" : {"DataType":"String", "StringValue":"GET"}, "student_id" : {"DataType":"String", "StringValue":"2b31cefe-6cd1-4ca5-954e-e84ab7f31be7"}}' --message-body "{}"`