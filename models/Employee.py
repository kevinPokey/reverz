from app import db

class Employee(db.Document):
    name = db.StringField()
    ezso = db.StringField()
    strm = db.IntField()
    location = db.StringField(default="")


def createEmployee(name, ezso, strm, location):
    employee = Employee(name=name, ezso=ezso, strm=strm, location=location)
    return employee.save()