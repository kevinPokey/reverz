from app import db

class ImdbEquipment(db.EmbeddedDocument):
    invNum = db.StringField()
    equipment_id = db.ReferenceField(Equipment)