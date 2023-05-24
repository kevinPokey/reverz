import hashlib
from models import *
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file, send_from_directory
from flask_session import Session  # https://pythonhosted.org/Flask-Session


def checkSession():
    if not session.get("user"):
        session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
        return False
    else:
        if session.get("user"):
            username = session.get("user").get("name")
            user = User.objects(username=username).first()

            if user is None:
                createUser(username)
                user = User.objects(username=user).first()
            return user
        else:
            return False



def write_log(user_ip, user_url, user_method):
    if "static" in user_url:
        return
    user = "No session"
    if session.get("user"):
        user = session.get("user").get("name")
    app.logger.info(f'INFO {str(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))}; IP_SRC: {user_ip}; SESSION: {user}; METHOD: {user_method}; REQUEST_URL:{user_url}')


def equipmentCheck():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)

    reverzJson = request.get_json()
    reverzId = reverzJson["id"]
    #goodbye = Reverz.objects(id=reverzId).first()
    goodbye2 = ReverzEquipment.objects(reverzId=reverzId).all()
    reverzJson = []
    for r in goodbye2:
        currentReverz = {"id": r["reverzId"], "issuer": r["giver"], "user": r["receiver"], "date": datetime.strftime(
            r["date"], "%d.%m.%Y"), "equipmentName": r["equipmentName"], "invNum": r["equipmentInvNum"], "status": r["status"], "loc": r["loc"]}
        reverzJson.append(currentReverz)

    return jsonify(reverzJson)


def showPdf(user):
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    currentUser = session["user"].get("name")
    if user == currentUser.replace(" ", "").lower():
        mongoEq = ReverzEquipment.objects(Q(giver=currentUser)).order_by('-date').first()
        mongoReverz = Reverz.objects(id=mongoEq["reverzId"]).first()
        receiver = mongoReverz["receiver"]["name"]
        reverz_date = mongoReverz["date"].strftime("%d-%m-%Y_%H.%M_") + str(mongoReverz["reverzCount"])

        return send_file(f"{user}/tmp.pdf", download_name=f"{receiver}_{reverz_date}.pdf", as_attachment=False)
    else:
        return "Access denied"


def home():
    #start = time.time()
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)

    if request.method == "GET":
        me = User.objects(username=session["user"].get("name")).first()
        sessionUser = session["user"].get("name")
        #end = time.time()
        #print(end - start)

        return render_template("home.html", user=me, sessionUser=sessionUser)