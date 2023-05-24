from app import db

class Reverz(db.Document):
    giver = db.ReferenceField(User)
    receiver = db.ReferenceField(Employee)
    givenEq = db.EmbeddedDocumentListField(ImdbEquipment)
    receivedEq = db.EmbeddedDocumentListField(ImdbEquipment)
    givenLoc = db.StringField()
    receivedLoc = db.StringField()
    reverzCount = db.IntField(min_value=100)
    date = db.DateTimeField()
