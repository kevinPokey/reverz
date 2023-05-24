import hashlib
import os
import datetime
import json
import time
import re
from models import *
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file, send_from_directory
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from mongoengine.queryset.visitor import Q
from datetime import timedelta, datetime

def search():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        producers = Producer.objects().all()
        equipmentTypes = EquipmentType.objects().all()
        issuers = User.objects().all()
        employees = Employee.objects().all()
        warehouses = Warehouse.objects().all()
        me = User.objects(username=session["user"].get("name")).first()
        # regex = re.compile(loc)
        # reverzThing = Reverz.objects(givenLoc=regex).all()
        return render_template("search.html", producers=producers, equipmentTypes=equipmentTypes, issuers=issuers, employees=employees, warehouses=warehouses, user=me)
    elif request.method == "POST":
        inputFields = request.get_json()

        invNum = inputFields["invNum"]
        status = inputFields["status"]
        warehouse = inputFields["warehouse"]
        issuer = inputFields["issuer"]
        user = inputFields["user"]
        type = inputFields["type"]
        producer = inputFields["producer"]
        model = inputFields["model"]
        dateStart = inputFields["dateStart"]
        dateEnd = inputFields["dateEnd"]
        toCSV = inputFields["toCSV"]

        regex = re.compile('.*')

        if invNum == "":
            invNum = re.compile('.*')
        else:
            invNum = re.compile("^" + inputFields["invNum"] + "$")
        if status == "Izberi...":
            status = re.compile('.*')
        if warehouse == "Izberi...":
            warehouse = re.compile('.*')
        elif status == "A":
            warehouse == "t5435432532tr353425" #Nekaj kar v bazi ne obstaja (ker nemore biti in A in skladišče)
        else:
            status = "S"
        if issuer == "Izberi...":
            issuer = re.compile('.*')
        if user == "Izberi...":
            user = re.compile('.*')
        if type == "Izberi...":
            type = '.*'
        else:
            type = f'{type}.*'
        if producer == "Izberi...":
            producer = '.*'
        else:
            producer = f'.*{producer}.*'
        if model == "":
            model = '.*'
        else:
            model = f'.* {model}'
        if dateStart == "":
            dateStart = "01.01.2000"
        if dateEnd == "":
            dateEnd = "01.01.2999"

        equipmentRegex = re.compile(f"{type}{producer}{model}$")
        #print(equipmentRegex)

        dateEnd = datetime.strptime(dateEnd, "%d.%m.%Y")
        dateEnd = dateEnd + timedelta(days=1)
        pageStart = 17 * (int(inputFields["page"]) - 1)
        pageEnd = 17 * int(inputFields["page"])
        maxPage = 0
        equipmentCount = 0
        reverzListGiven = None

        if not toCSV:
            reverzListGiven = ReverzEquipment.objects[pageStart:pageEnd]((Q(receiver=user)) & (Q(giver=issuer)) & (Q(equipmentInvNum=invNum)) & (Q(status=status)) & (
                Q(equipmentName=equipmentRegex)) & ((Q(loc=warehouse))) & (Q(date__gte=datetime.strptime(dateStart, "%d.%m.%Y"))) & (Q(date__lte=dateEnd))).all().order_by('-date')

        else:
            reverzListGiven = ReverzEquipment.objects((Q(receiver=user)) & (Q(giver=issuer)) & (Q(equipmentInvNum=invNum)) & (Q(status=status)) & (
                Q(equipmentName=equipmentRegex)) & ((Q(loc=warehouse))) & (Q(date__gte=datetime.strptime(dateStart, "%d.%m.%Y"))) & (Q(date__lte=dateEnd))).all().order_by('-date')
        # print(reverzListGiven)

        equipmentCount = ReverzEquipment.objects((Q(receiver=user)) & (Q(giver=issuer)) & (Q(equipmentInvNum=invNum)) & (Q(status=status)) & (
            Q(equipmentName=equipmentRegex)) & ((Q(loc=warehouse))) & (Q(date__gte=datetime.strptime(dateStart, "%d.%m.%Y"))) & (Q(date__lte=dateEnd))).count()
        maxPage = math.ceil(equipmentCount / 17)

        reverzJson = []
        counter = 0
        for r in reverzListGiven:
            counter = counter + 1
            currentReverz = {"id": r["reverzId"], "issuer": r["giver"], "user": r["receiver"], "date": datetime.strftime(
                r["date"], "%d.%m.%Y"), "equipmentName": r["equipmentName"], "invNum": r["equipmentInvNum"], "status": r["status"], "maxPage": maxPage, "equipmentCount": equipmentCount}
            reverzJson.append(currentReverz)
            if counter >= 17:
                break

        #print(toCSV)
        sessionUser = session["user"].get("name").replace(" ", "").lower()

        if toCSV:
            with open(f"{sessionUser}/reverz.csv", mode='w', encoding='utf-8-sig') as csv_file:
                spawn_write = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                spawn_write.writerow(['Inventarna št.', 'Oprema', 'Status', 'Lokacija', 'Datum', 'Uporabnik', 'Izdajatelj', 'Reverz št.'])
                for r in reverzListGiven:
                    tmp = Reverz.objects(id=r["reverzId"]).first()
                    reverzCount = tmp["reverzCount"]
                    spawn_write.writerow([r["equipmentInvNum"], r["equipmentName"], r["status"], r["loc"], datetime.strftime(r["date"], "%d.%m.%Y"), r["receiver"], r["giver"], reverzCount])
            csv_file.close()

        #print(reverzJson)
        return jsonify(reverzJson)


def reverzShow(reverz_id):
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)  
    if request.method == "GET":
        mongoReverz = Reverz.objects(id=reverz_id).first()
        #sessionUser = session["user"].get("name")
        #me = User.objects(username=sessionUser).first()
        #print(mongoReverz["givenEq"])
        #return render_template("reverzShow.html", mongoReverz=mongoReverz, sessionUser=session["user"].get("name").replace(" ", "").lower(), user=me)
        receiver = mongoReverz["receiver"]["name"]
        reverz_date = mongoReverz["date"].strftime("%d-%m-%Y_%H.%M_") + str(mongoReverz["reverzCount"])
        return send_file(f"log/{reverz_id}.pdf", download_name=f"{receiver}_{reverz_date}.pdf", as_attachment=False)


def downloadCsv():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    else:
        sessionUser = session["user"].get("name").replace(" ", "").lower()
        return send_file(f"{sessionUser}/reverz.csv", download_name='reverz.csv')


def downloadPdf(user, id):
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    currentUser = session["user"].get("name")
    if user == currentUser.replace(" ", "").lower():
        mongoReverz = Reverz.objects(id=id).first()
        receiver = mongoReverz["receiver"]["name"]
        reverz_date = mongoReverz["date"].strftime("%d-%m-%Y_%H.%M_") + str(mongoReverz["reverzCount"])
        return send_file(f"{user}/tmp.pdf", download_name=f"{receiver}_{reverz_date}.pdf", as_attachment=True)
    else:
        return "Access denied"