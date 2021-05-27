import os
import sys
import re
import datetime as dt
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    make_response,
    abort,
    jsonify,
    session,
    flash)
import pymongo
import bcrypt
from pymongo import collection
from app import app
from app.helpers import *
from app.forms import *
from app.models import *


model = Models()  # instance of the Model Class


client = pymongo.MongoClient('localhost', 27017)
db = client.get_database('election-system-test')
user_records = db.users
admin_records = db.admin
candidates_records = db.candidates
candidates_records_copy = db.candidates_copy
user_records = db.users
vote_records = db.votes

user_created = False

voted = False


@app.errorhandler(404)
def resource_not_found(e):
    return render_template('404.html'), 404


@app.route("/", methods=['post', 'get'])
def create_account():
    global voted
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    elif request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        course = request.form.get("course")
        section = request.form.get("section")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = user_records.find_one({"name": user})
        email_found = user_records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('create_account.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('create_account.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('create_account.html', message=message)
        if len(password1) < 6:
            message = 'The length of password should be at least 6 characters long'
            return render_template('create_account.html', message=message)
        if not any([char.isupper() for char in password1]):
            message = 'The password should have atleast one uppercase letter'
            return render_template('create_account.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email,
                'password': hashed, 'course' : course, 'section': section, 'voted': False}
            user_records.insert_one(user_input)

            user_data = user_records.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = new_email
            session["section"] = section
            session["name"] = user
            # session["voted"] = False

            return render_template('logged_in.html', email=new_email, user=user)
    return render_template('create_account.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        section = session["section"]
        user = session["name"]
        return render_template('logged_in.html', email=email, section=section, user=user)
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=["POST", "GET"])
def login():
    global voted
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # returns the document of the user
        email_found = user_records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            section_val = email_found['section']
            user_val = email_found['name']
            # print(email_val)
            # print(section_val)
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["section"] = section_val
                session["name"] = user_val
                # session["voted"] = False
                print(voted)

                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.clear()

        return redirect(url_for('login'))
    else:
        return redirect(url_for('create_account'))


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if "admin_username" in session:
        return redirect(url_for("admin_panel"))

    else:
        return redirect(url_for("admin_login"))


@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    message = 'Please login to your account'
        # return redirect(url_for("admin_panel"))

    if request.method == "POST":
        username = request.form.get("admin_username")
        password = request.form.get("admin_password")

        username_found = admin_records.find_one({"username": username})
        session["admin_username"] = username

        if username_found:
            username_val = username_found['username']
            passwordcheck = username_found['password']

            if passwordcheck:
                session["admin_username"] = username_val

                return redirect(url_for('admin_panel'))
            else:
                    # if "admin_username" in session:
                    #     return redirect(url_for("admin_panel"))
                message = 'Wrong password'
                return render_template('admin_login.html', message=message)
        else:
            message = 'Username not found'
            return render_template('admin_login.html', message=message)
    return render_template('admin_login.html', message=message)


@app.route("/admin_panel", methods=["POST", "GET"])
def admin_panel():
    if "admin_username" in session:
        return redirect(url_for("addCandidate"))
    else:
        return redirect(url_for("admin_login"))


# @app.route("/admin_logout", methods=["POST", "GET"])
# def admin_logout():
#     if "admin_username" in session:
#         session.pop("admin_username", None)
#         return render_template("admin_loggedout.html")
#     else:
#         return render_template('admin_login.html')


@app.route("/admin_logout", methods=["POST", "GET"])
def admin_logout():
    if "admin_username" in session:
        session.clear()

        return redirect(url_for('admin_panel'))
    else:
        return redirect(url_for('admin_login'))


@app.route("/admin/view", methods=["POST", "GET"])
def viewCandidate():
    if "admin_username" in session:
        from bson.json_util import dumps, loads
        result = list(model.pullListOfCandidates())
        print(result)

        party1 = []
        party2 = []
        party3 = []

        for i in result:
            if i.get("party") == "party1":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party1.append(candidate)
            elif i.get("party") == "party2":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party2.append(candidate)
            elif i.get("party") == "party3":
                candidate = {k: i[k] for k in i.keys() - {'party'} - {'_id'}}
                party3.append(candidate)

        party1_list = []
        party2_list = []
        party3_list = []

        for i in range(len(party1)):
            party1Item = [party1[i]["id"], party1[i]["name"],
                "as", party1[i]["position"].title()]
            party1_list.append(" ".join(party1Item))

        for i in range(len(party2)):
            party2Item = [party2[i]["id"], party2[i]["name"],
                "as", party2[i]["position"].title()]
            party2_list.append(" ".join(party2Item))

        for i in range(len(party3)):
            party3Item = [party3[i]["id"], party3[i]["name"],
                "as", party3[i]["position"].title()]
            party3_list.append(" ".join(party3Item))

        print(party1_list)
        print(party2_list)
        print(party3_list)
        # return render_template("admin_viewCan.html")

        return render_template("admin_viewCan.html", party1=party1_list, party2=party2_list, party3=party3_list)
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/add", methods=["POST", "GET"])
def addCandidate():
    if "admin_username" in session:
        if request.method == "POST":
            candidate_name = request.form.get("candidate_name")
            candidate_position = request.form.get("candidate_position")
            candidate_party = request.form.get("candidate_party")
            candidate_course = request.form.get("candidate_course")
            candidate_year = request.form.get("candidate_year")

            last_record = candidates_records.find().sort([('_id', -1)]).limit(1)
            id_num = int(last_record[0]['id']) + 1
            id = "00"+str(id_num)

            admin_add = {"id": id, 'party': candidate_party, 'course': candidate_course,
                'year': candidate_year, "position": candidate_position, "name": candidate_name}
            candidates_records.insert_one(admin_add)

        return render_template("admin_addCan.html")
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/update", methods=["POST", "GET"])
def updateCandidate():
    if "admin_username" in session:
        if request.method == "POST":
            candidate_id = request.form.get("candidate_id")
            candidate_name = request.form.get("candidate_name")
            candidate_position = request.form.get("candidate_position")
            candidate_party = request.form.get("candidate_party")
            candidate_course = request.form.get("candidate_course")
            candidate_year = request.form.get("candidate_year")

            updateRecordQuery = {"id": candidate_id}
            newvalues = {"$set": {"id": candidate_id, 'party': candidate_party, 'course': candidate_course,
                'year': candidate_year, "position": candidate_position, "name": candidate_name}}
            candidates_records.update_one(updateRecordQuery, newvalues)

        return render_template("admin_updateCan.html")
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin/delete", methods=["POST", "GET"])
def deleteCandidate():
    if "admin_username" in session:
        if request.method == "POST":
            candidate_id = request.form.get("candidate_id")

            deleteRecordQuery = {"id": candidate_id}
            candidates_records.find_one_and_delete(deleteRecordQuery)

        return render_template("admin_deleteCan.html")
    
    else:
        return redirect(url_for("admin_login"))


@app.route("/base", methods=["POST", "GET"])
def base():
    return render_template("base6.html")


# @app.post("/vote")
# def vote1():
#     global voted
#     if "email" in session:
#         user = session["name"]
#         section = session["section"]


@app.route("/vote", methods=["POST", "GET"])
def vote():
    global voted
    if "email" in session:
        user = session["name"]

        if request.method == "GET":
            if model.getVoted(str(user)):
                voted = True

            else:
                voted = False
        

        listOfCandidates = model.pullCandidates()
        chairperson = []
        vice_chairperson = []
        secretary = []
        assistant_secretary = []
        treasurer = []
        assistant_treasurer = []
        auditor = []
        assistant_auditor = []
        business_manager = []
        assistant_business_manager = []
        representative1 = []
        representative2 = []

        x = 0
        while x == 0:
            for num, i in enumerate(listOfCandidates):
                if i[1] == "chairperson":
                    chairperson.append(i[0])
                elif i[1] == "vice_chairperson":
                    vice_chairperson.append(i[0])
                elif i[1] == "secretary":
                    secretary.append(i[0])
                elif i[1] == "assistant_secretary":
                    assistant_secretary.append(i[0])
                elif i[1] == "treasurer":
                    treasurer.append(i[0])
                elif i[1] == "assistant_treasurer":
                    assistant_treasurer.append(i[0])
                elif i[1] == "auditor":
                    auditor.append(i[0])
                elif i[1] == "assistant_auditor":
                    assistant_auditor.append(i[0])
                elif i[1] == "business_manager":
                    business_manager.append(i[0])
                elif i[1] == "assistant_business_manager":
                    assistant_business_manager.append(i[0])
                elif i[1] == "representative1":
                    representative1.append(i[0])
                elif i[1] == "representative2":
                    representative2.append(i[0])
            x = 1


            if request.method == "POST":
                if "submit_btn" in request.form:
                    chairperson_vote = request.form.get("chairperson")
                    vice_chairperson_vote = request.form.get("vice_chairperson")
                    secretary_vote = request.form.get("secretary")
                    assistant_secretary_vote = request.form.get("assistant_secretary")
                    treasurer_vote = request.form.get("treasurer")
                    assistant_treasurer_vote = request.form.get("assistant_treasurer")
                    auditor_vote = request.form.get("auditor")
                    assistant_auditor_vote = request.form.get("assistant_auditor")
                    business_manager_vote = request.form.get("business_manager")
                    assistant_business_manager_vote = request.form.get("assistant_business_manager")
                    representative1_vote = request.form.get("representative1")
                    representative2_vote = request.form.get("representative2")

                    candidate_id = model.getIDbyName(str(user))
                    updateRecordQuery = {"_id": candidate_id}
                    newvalues = {"$set": {"voted": True}}
                    user_records.update_one(updateRecordQuery, newvalues)

                    votes_add = {"name": str(user), "chairperson": chairperson_vote, "vice_chairperson" : vice_chairperson_vote, "secretary" : secretary_vote, "assistant_secretary" : assistant_secretary_vote, "treasurer" : treasurer_vote, "assistant_treasurer" : assistant_treasurer_vote, "auditor":
                          auditor_vote, "assistant_auditor" : assistant_auditor_vote, "business_manager" : business_manager_vote, "assistant_business_manager" : assistant_business_manager_vote, "representative1" : representative1_vote, "representative2" :representative2_vote}
                    
                    vote_records.insert_one(votes_add)

                    if model.getVoted(str(user)):
                        voted = True
                    else:
                        voted = False
                    
                    print("chairperson: ", chairperson_vote, "vice_chairperson: ", vice_chairperson_vote, "secretary: ", secretary_vote, "assistant_secretary: ", assistant_secretary_vote, "treasurer: ", treasurer_vote, "assistant_treasurer: ", assistant_treasurer_vote, "auditor: ",
                          auditor_vote, "assistant_auditor: ", assistant_auditor_vote, "business_manager: ", business_manager_vote, "assistant_business_manager: ", assistant_business_manager_vote, "representative1: ", representative1_vote, "representative2: ", representative2_vote)



        return render_template('vote.html', user = user, chairperson=chairperson, vice_chairperson=vice_chairperson, secretary=secretary, assistant_secretary=assistant_secretary, treasurer=treasurer, assistant_treasurer=assistant_treasurer, auditor=auditor, assistant_auditor=assistant_auditor, business_manager=business_manager, assistant_business_manager=assistant_business_manager, representative1=representative1, representative2=representative2, voted=voted)
    else:
        return redirect(url_for("login"))


@app.route("/about", methods=["POST", "GET"])
def about():
    return render_template("about.html")
