from app import db

class EquipmentType(db.Document):
    name = db.StringField()

def createEquipmentType(name):
    equipmentType = EquipmentType(name=name)
    return equipmentType.save()