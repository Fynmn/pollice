import os, sys
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


model = Models() # instance of the Model Class


client = pymongo.MongoClient('localhost', 27017)
db = client.get_database('election-system-test')
user_records = db.users
admin_records = db.admin
candidates_records = db.candidates
candidates_records_copy = db.candidates_copy

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
            user_input = {'name': user, 'email': email, 'password': hashed, 'section': section}
            user_records.insert_one(user_input)
            
            user_data = user_records.find_one({"email": email})
            new_email = user_data['email']
            session["email"] = new_email
            session["section"] = section
            session["name"] = user
            session["voted"] = False
            
            return render_template('logged_in.html', email=new_email, section=section, user=user)
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

        email_found = user_records.find_one({"email": email}) # returns the document of the user
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
                session["voted"] = False
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
        # session.pop("email", None)
        # session.pop("name", None)
        # session.pop("section", None)
        session.clear()
        
        return redirect(url_for('login'))
    else:
        return redirect(url_for('create_account'))


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if "admin_username" in session:
        return redirect(url_for("viewCandidate"))

    else:
        return redirect(url_for("admin_login"))


@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    message = 'Please login to your account'
    if "admin_username" in session:
        return redirect(url_for("admin_panel"))

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
                if "admin_username" in session:
                    return redirect(url_for("admin_panel"))
                message = 'Wrong password'
                return render_template('admin_login.html', message=message)
        else:
            message = 'Username not found'
            return render_template('admin_login.html', message=message)
    return render_template('admin_login.html', message=message)


@app.route("/admin_panel", methods=["POST", "GET"])
def admin_panel():
    if "admin_username" in session:
        return redirect(url_for("viewCandidate"))
    else:
        return redirect(url_for("admin_login"))


@app.route("/admin_logout", methods=["POST", "GET"])
def admin_logout():
    if "admin_username" in session:
        session.pop("admin_username", None)
        return render_template("admin_loggedout.html")
    else:
        return render_template('admin_login.html')


@app.route("/admin/view", methods=["POST", "GET"])
def viewCandidate():
    from bson.json_util import dumps, loads
    result = list(model.pullCandidates())
    candidateA = []
    candidateB = []
            
    for i in result:
        if i.get("section") == "2A":
            candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'}}
            candidateA.append(candidate)
            
        elif i.get("section") == "2B":
            candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'}}
            candidateB.append(candidate)

    candidateA_list = []
    candidateB_list = []

    for i in range(len(candidateA)):
        candidateAItem = [candidateA[i]["id"], candidateA[i]["name"], "as", candidateA[i]["position"].title()]
        candidateA_list.append(" ".join(candidateAItem))
    
    for i in range(len(candidateB)):
        candidateBItem = [candidateB[i]["id"], candidateB[i]["name"], "as", candidateB[i]["position"].title()]
        candidateB_list.append(" ".join(candidateBItem))
    
    print(candidateA_list)
    print(candidateB_list)

    return render_template("admin_viewCan.html", candidateA=candidateA_list, candidateB=candidateB_list)


@app.route("/admin/add", methods=["POST", "GET"])
def addCandidate():
    if request.method == "POST":
        candidate_name = request.form.get("candidate_name")
        candidate_position = request.form.get("candidate_position")
        section = request.form.get("section")

        last_record = candidates_records.find().sort([('_id', -1)]).limit(1)
        id_num = int(last_record[0]['id']) + 1
        id = "00"+str(id_num)

        admin_add = {"id": id, 'section': section, "position" : candidate_position, "name" : candidate_name}
        candidates_records.insert_one(admin_add)

    return render_template("admin_addCan.html")


@app.route("/admin/update", methods=["POST", "GET"])
def updateCandidate():
    if request.method == "POST":
        candidate_id = request.form.get("candidate_id")
        candidate_name = request.form.get("candidate_name")
        candidate_position = request.form.get("candidate_position")
        section = request.form.get("section")

        updateRecordQuery = {"id":candidate_id}
        newvalues = { "$set": {"id": candidate_id, 'section': section, "position" : candidate_position, "name": candidate_name} }
        candidates_records.update_one(updateRecordQuery, newvalues)

    return render_template("admin_updateCan.html")


@app.route("/admin/delete", methods=["POST", "GET"])
def deleteCandidate():
    if request.method == "POST":
        candidate_id = request.form.get("candidate_id")
        
        deleteRecordQuery = {"id" : candidate_id}
        candidates_records.find_one_and_delete(deleteRecordQuery)
    
    return render_template("admin_deleteCan.html")


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
        section = session["section"]
        # print(voted)
        
        
        if section == "2B":
            list_of_2B_can = model.get2BList()
            # print(list_of_2B_can)
            chairperson = []
            secretary = []
            treasurer = []
            auditor = []
            business_manager = []
            representative = []

            for num, i in enumerate(list_of_2B_can):
                if i[1] == "chairperson":
                    chairperson.append(i[0])
                elif i[1] == "secretary":
                    secretary.append(i[0])
                elif i[1] == "treasurer":
                    treasurer.append(i[0])
                elif i[1] == "auditor":
                    auditor.append(i[0])
                elif i[1] == "business_manager":
                    business_manager.append(i[0])
                elif i[1] == "representative":
                    representative.append(i[0])

            if request.method == "POST":
                if "submit_btn" in request.form:
                        
                    chairperson_vote = request.form.get("chairperson")
                    secretary_vote = request.form.get("secretary")
                    treasurer_vote = request.form.get("treasurer")
                    auditor_vote = request.form.get("auditor")
                    business_manager_vote = request.form.get("business_manager")
                    representative_vote = request.form.get("representative")
                    session["voted"] = True
                    print("chairperson: ", chairperson_vote, "secretary: ", secretary_vote, "treasurer: ", treasurer_vote, "auditor: ", auditor_vote, "business_manager: ", business_manager_vote, "representative: ", representative_vote)
                        
                   

        elif section == "2A":
            list_of_2A_can = model.get2AList()
            # print(list_of_2A_can)
            chairperson = []
            secretary = []
            treasurer = []
            auditor = []
            business_manager = []
            representative = []

            for num, i in enumerate(list_of_2A_can):
                if i[1] == "chairperson":
                    chairperson.append(i[0])
                elif i[1] == "secretary":
                    secretary.append(i[0])
                elif i[1] == "treasurer":
                    treasurer.append(i[0])
                elif i[1] == "auditor":
                    auditor.append(i[0])
                elif i[1] == "business_manager":
                    business_manager.append(i[0])
                elif i[1] == "representative":
                    representative.append(i[0])
            
        
            if request.method == "POST":
                if "submit_btn" in request.form:
                    
                    chairperson_vote = request.form.get("chairperson")
                    secretary_vote = request.form.get("secretary")
                    treasurer_vote = request.form.get("treasurer")
                    auditor_vote = request.form.get("auditor")
                    business_manager_vote = request.form.get("business_manager")
                    representative_vote = request.form.get("representative")
                    session["voted"] = True
                    
                    print("chairperson: ", chairperson_vote, "secretary: ", secretary_vote, "treasurer: ", treasurer_vote, "auditor: ", auditor_vote, "business_manager: ", business_manager_vote, "representative: ", representative_vote)
                    
        return render_template('vote.html', user = user, chairperson=chairperson, secretary=secretary, treasurer=treasurer, auditor=auditor, business_manager=business_manager,representative=representative, voted=session["voted"])
    else:
        return redirect(url_for("login"))

# @app.get("/about")
# def about():
#     return render_template("about.html")