from app import db

class Producer(db.Document):
    name = db.StringField()