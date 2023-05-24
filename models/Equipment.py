from app import db


class Equipment(db.Document):
    name = db.StringField()

def createEquipment(name):
    equipment = Equipment(name=name)
    return equipment.save()