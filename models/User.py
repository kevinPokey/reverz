from app import db


class User(db.Document):
    username = db.StringField()
    settings = db.EmbeddedDocumentField(Settings)

def createUser(username):
    user = User(username=username, settings=Settings())
    os.system(f"mkdir {username.replace(' ', '').lower()} && cp reverzTemplateBoth.docx reverzTemplateIzdana.docx reverzTemplateVrnjena.docx {username.replace(' ', '').lower()}")

    return user.save()