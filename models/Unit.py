from app import db


class Unit(db.Document):
    name = db.StringField()
    number = db.IntField()

def createUnit(name, number):
    unit = Unit(name=name, number=number)
    return unit.save()