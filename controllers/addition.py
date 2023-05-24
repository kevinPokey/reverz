import hashlib
from models import *
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file, send_from_directory
from flask_session import Session  # https://pythonhosted.org/Flask-Session

def addEquipment():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        producers = Producer.objects().all()
        equipmentTypes = EquipmentType.objects().all()
        return render_template("addEquipment.html", producers=producers, equipmentTypes=equipmentTypes)
    elif request.method == "POST":

        # Da se prikaže flash mora vsebovati substring "je bila"/"ni bila"
        if createEquipment(request.form["tip"] + " " + request.form["znamka"] + " " + request.form["model"]) != None:
            flash("Tip opreme je bil uspešno dodan")
        else:
            flash("Prišlo je do napake. Tip opreme ni bil dodan")

        return redirect(url_for("home"))


def add():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        producers = Producer.objects().all()
        equipmentTypes = EquipmentType.objects().all()
        units = Unit.objects().all()
        me = User.objects(username=session["user"].get("name")).first()
        return render_template("add.html", producers=producers, equipmentTypes=equipmentTypes, units=units, user=me)


def addEquipmentType():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        return render_template("addEquipmentType.html")
    elif request.method == "POST":

        # Da se prikaže flash mora vsebovati substring "je bil"/"ni bil"
        if createEquipmentType(request.form["type"]) is not None:
            flash("Oprema je bila uspešno dodana")
        else:
            flash("Prišlo je do napake. Oprema ni bila dodana")
        return redirect(url_for("home"))


def addEquipmentProducer():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        return render_template("addProducer.html")
    elif request.method == "POST":

        # Da se prikaže flash mora vsebovati substring "je bil"/"ni bil"
        if createProducer(request.form["producer"]) is not None:
            flash("Proizvajalec opreme je bil uspešno dodan")
        else:
            flash("Prišlo je do napake. Proizvajalec opreme ni bil dodan")
        return redirect(url_for("home"))


def addUser():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        units = Unit.objects().all()
        me = User.objects(username=session["user"].get("name")).first()
        return render_template("addUser.html", units=units, user=me)
    elif request.method == "POST":
        units = Unit.objects().all()
        unit = Unit.objects(number=request.form["enota"]).first()
        print(request.form["enota"])

        # Da se prikaže flash mora vsebovati substring "je bil"/"ni bil"
        if createEmployee(request.form["ime"] + " " + request.form["priimek"], request.form["ezso"], unit.number, request.form["location"]) != None:
            flash("Uporabnik je bil uspešno dodana")
        else:
            flash("Prišlo je do napake. uporabnik ni bil dodan")

        producers = Producer.objects().all()
        equipmentTypes = EquipmentType.objects().all()
        units = Unit.objects().all()
        me = User.objects(username=session["user"].get("name")).first()
        return render_template("add.html", producers=producers, equipmentTypes=equipmentTypes, units=units, user=me)
