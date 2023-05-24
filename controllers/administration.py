import hashlib
import os
import datetime
import json
import time
import threading
from models import *
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file, send_from_directory
from flask_session import Session  # https://pythonhosted.org/Flask-Session
from mongoengine.queryset.visitor import Q
from datetime import timedelta, datetime

def administrationChange():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        user = User.objects(username=session["user"].get("name")).first()
        employees = Employee.objects().order_by("name")
        if(user["settings"]["administrator"] == 1):
            return render_template("administrationDelete.html", user=user, employees=employees)
        else:
            return "Access Denied"
    elif request.method == "POST":
        data = request.get_json()
        if data["selection"] == "employee":
            employee = str(data["name"])
            print(employee)
            employee = Employee.objects(name=employee).first()
            if employee:
                name, lastname = str(employee["name"]).split(" ", 1)
                employee_json = {"name": name, "lastname": lastname, "ezso": employee["ezso"], "location": employee["location"], "strm": str(employee["strm"])}
                return jsonify(employee_json)
            else:
                return jsonify({'error': 'Employee not found'})


def administration():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        user = User.objects(username=session["user"].get("name")).first()
        if(user["settings"]["administrator"] == 1):
            return render_template("administration.html", user=user)
        else:
            return "Access Denied"


def administrationSelect():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        user = User.objects(username=session["user"].get("name")).first()
        #users = User.objects(username__ne=user["username"]).all()
        users = User.objects().all()
        if(user["settings"]["administrator"] == 1):
            return render_template("administrationSelect.html", user=user, users=users)
        else:
            return "Access Denied"
    elif request.method == "POST":
        data = request.get_json()
        for user in data['checkedUsers']:
            User.objects(username=user).update_one(set__settings__administrator=1)
        for user in data['uncheckedUsers']:
            User.objects(username=user).update_one(set__settings__administrator=0)
        return jsonify({'message': 'Users updated successfully'})
    else:
        return "Invalid method"


def administrationLog():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        user = User.objects(username=session["user"].get("name")).first()
        if(user["settings"]["administrator"] == 1):
            return send_file(f"reverz_log.log", download_name=f"log.log", as_attachment=True)
        else:
            return "Access Denied"


def administrationChange():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    if request.method == "GET":
        user = User.objects(username=session["user"].get("name")).first()
        employees = Employee.objects().order_by("name")
        units = Unit.objects().all()
        if(user["settings"]["administrator"] == 1):
            return render_template("administrationChange.html", user=user, employees=employees, units=units)
        else:
            return "Access Denied"
    elif request.method == "POST":
        data = request.get_json()
        if data["selection"] == "check":
            print("no")
            employee = str(data["name"])
            employee = Employee.objects(name=employee).first()
            if employee:
                name, lastname = str(employee["name"]).split(" ", 1)
                employee_json = {"name": name, "lastname": lastname, "ezso": employee["ezso"], "location": employee["location"], "strm": str(employee["strm"])}
                return jsonify(employee_json)
            else:
                return jsonify({'error': 'Employee not found'})


def administrationChangeNow():
    if not checkSession():
        sessionAuthUri = session["flow"]["auth_uri"]
        return redirect(sessionAuthUri)
    else:
        data = request.get_json()
        name = f'{data["name"]} {data["lastname"]}'
        ezso = data["ezso"]
        print(data["strm"])
        employee = Employee.objects(ezso=ezso).update(set__name=name, set__strm=int(data["strm"]), set__ezso=data["ezso"], set__location=data["location"])
        if employee:
                return jsonify("ok", 200)
        else:
                return jsonify({'error': 'Employee not found'})