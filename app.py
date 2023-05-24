import os
import datetime
import ssl
import app_config
import msal
import requests
import logging
import logging.config
import numpy as np
from controllers import *
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file, send_from_directory
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from flask_mongoengine import MongoEngine
from mongoengine.queryset.visitor import Q
from werkzeug.utils import secure_filename
from waitress import serve


# HTTPS
# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https

# DIGITAL SIGNATURES
# https://www.thepythoncode.com/article/sign-pdf-files-in-python

# OTHER TUTORIALS
# https://www.rikvoorhaar.com/python-docx/
# https://www.youtube.com/watch?v=VZzWzRVXPcQ
# https://coolors.co/palette/ef476f-ffd166-06d6a0-118ab2-073b4c
# https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/

# PYTHON MONGODB GUIDE
# --- General guide ---
# https://stackabuse.com/guide-to-flask-mongoengine-in-python/
# --- Querying guide ---
# https://docs.mongoengine.org/guide/querying.html
# https://www.statology.org/mongodb-query-date-range/
# https://www.youtube.com/watch?v=i0jhdr0OD7E

# DEPLOYMENT
# https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c


IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.secret_key = "work_hard"
app.permanent_session_lifetime = timedelta(minutes=120)
app.config.from_object(app_config)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=False,
)
app.config['MONGODB_SETTINGS'] = {
    'db': 'DB',
    'host': 'mongodb://user:passwd@ip:port/DB?authSource=DB'
}
Session(app)
db = MongoEngine()
db.init_app(app)


from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})
logging.basicConfig(filename='reverz_log.log', level=logging.INFO, format=f'%(message)s')


@app.before_request
def before_request():
    ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    write_log(ip_addr, request.base_url, request.method)




@app.route("/equipmentCheck/", methods=["POST"])
def equipmentCheckRoute():
    return equipmentCheck()

@app.route("/deleteReverz/", methods=["POST"])
def deleteReverzRoute():
    return deleteReverz()

@app.route("/signatureExample/", methods=["GET"])
def signatureExampleRoute():
    return signatureExample()

@app.route("/", methods=["GET"])
def homeRoute():
    return home()

@app.route("/generated/<user>", methods=["GET"])
def showPdfRoute(user):
    return showPdf(user)

@app.route("/download/pdf/<user>/<id>", methods=["GET"])
def downloadPdfRoute(user, id):
    return downloadPdf(user, id)

@app.route("/reverz/", methods=["GET", "POST"])
def reverzRoute():
    return reverz()




@app.route("/addEquipment/", methods=["GET", "POST"])
def addEquipmentRoute():
    return addEquipment()

@app.route("/add/", methods=["GET", "POST"])
def add():
    return add()

@app.route("/addEquipment/type/", methods=["GET", "POST"])
def addEquipmentTypeRoute():
    return addEquipmentType()

@app.route("/addEquipment/producer/", methods=["GET", "POST"])
def addEquipmentProducerRoute():
    return addEquipmentProducerRoute()

@app.route("/addUser/", methods=["GET", "POST"])
def addUserRoute():
    return addUser()



@app.route("/search/", methods=["GET", "POST"])
def searchRoute():
    return search()

@app.route("/reverzShow/<reverz_id>")
def reverzShowRoute(reverz_id):
    return reverzShow(reverz_id)

@app.route("/settings/")
def settingsRoute():
    return settings()

@app.route("/settings/change/", methods=["POST"])
def changeSettingsRoute():
    return changeSettings()

@app.route("/download/csv/")
def downloadCsvRoute():
    return downloadCsv()



@app.route("/administration")
def administrationRoute():
    return administration()

@app.route("/administration/change", methods=["GET", "POST"])
def administrationChangeRoute():
    return administrationChange()
            
@app.route("/administration/change/user", methods=["POST"])
def administrationChangeNowRoute():
    return administrationChangeNow()

@app.route("/administration/delete", methods=["GET", "POST"])
def administrationDeleteRoute():
    return administrationChange()
    
@app.route("/administration/select", methods=["GET", "POST"])
def administrationSelectRoute():
    return administrationSelect()
    
@app.route("/administration/log")
def administrationLogRoute():
    return administrationLog()





@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("home"))

@app.route("/logout/")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("home", _external=True))

@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template


class CustomProxyFix(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['HTTP_HOST'] = 'url'
        environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)

app.wsgi_app = CustomProxyFix(app.wsgi_app)


if __name__ == "__main__":
    #app.run(debug=True)
    serve(app, host='localhost', port=5000, url_scheme='https')
