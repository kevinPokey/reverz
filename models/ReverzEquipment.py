from app import db

class ReverzEquipment(db.Document):
    giver = db.StringField()
    receiver = db.StringField()
    equipmentName = db.StringField()
    equipmentInvNum = db.StringField()
    loc = db.StringField()
    status = db.StringField()
    date = db.DateTimeField()
    reverzId = db.StringField()