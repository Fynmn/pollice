import pymongo
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

    
class Models:
                # Function that gets candidates from database and returns them in dictionary format
    def getCandidates(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates 
        chairperson = candidates_records.distinct("chairperson")
        secretary = candidates_records.distinct("secretary")
        treasurer = candidates_records.distinct("treasurer")
        auditor = candidates_records.distinct("auditor")
        business_manager = candidates_records.distinct("business_manager")
        representative = candidates_records.distinct("representative")

        candidates = {"chairperson": chairperson, "secretary": secretary, "treasurer": treasurer, "auditor": auditor, "business_manager": business_manager, "representative": representative}

        return candidates

    #Function that gets candidates from database
    def pullCandidates(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates
        result = candidates_records.find()

        listOfCandidates = []
                    
        for i in result:
            candidate = {k: i[k] for k in i.keys() - {'_id'} - {'id'} - {'course'} - {'section'}}
            listOfCandidates.append(candidate)
            
        
        candidates_list = []

        for i in range(len(listOfCandidates)):
            candidateItem = [listOfCandidates[i]["name"], listOfCandidates[i]["position"], listOfCandidates[i]["party"]]
            candidates_list.append(candidateItem)
            
        return candidates_list


    
    
    def deleteCandidate(self):
        pass


    # Function that returns name and position of candidates from 2B
    def get2BList(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates

        result = candidates_records.find()

        candidateB = []
                    
        for i in result:
            if i.get("section") == "2B":
                candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'} - {'id'}}
                candidateB.append(candidate)
            
            candidateB_list = []

        for i in range(len(candidateB)):
            candidateBItem = [candidateB[i]["name"], candidateB[i]["position"]]
            candidateB_list.append(candidateBItem)
            
        return candidateB_list
    

    def get2AList(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates

        result = candidates_records.find()

        candidateA = []
                    
        for i in result:
            if i.get("section") == "2A":
                candidate = {k: i[k] for k in i.keys() - {'section'} - {'_id'} - {'id'}}
                candidateA.append(candidate)
            
        candidateA_list = []

        for i in range(len(candidateA)):
            candidateAItem = [candidateA[i]["name"], candidateA[i]["position"]]
            candidateA_list.append(candidateAItem)
            
        return candidateA_list
    
    # Function that gets the voted value from the databse and returns it
    def getVoted(self, name):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        users_records = db.users

        voted = users_records.find_one({'name': name})

        for i,j in voted.items():
            if i == 'voted':
                if j == False:
                    print("False")
                    return False
                elif j == True:
                    print("True")
                    return True
                else:
                    print("can't find value")
    
    #function that gets object id by name
    def getIDbyName(self, name):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        user_records = db.users

        record = user_records.find_one({'name' : name})

        return record.get('_id')

    
    def pullListOfCandidates(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates

        result = candidates_records.find()

        return result


    

    

