COMS 6998 Project 2

# API
## REST

* `GET` /student : retrieve all students
* `GET` /student/{id} : retrieve student with {id}
* `POST` /student : add student
* `PUT` /student/{id} : update a student
* `DELETE` /student/{id} : delete a student

## SQS

# Examples

## Student REST API
This assumes that the microservice is running on port 8000.

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