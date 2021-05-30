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
    # A Function that gets candidates from database and returns them in dictionary format
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

    # A Function that gets candidates from database
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


    # A Function that returns name and position of candidates from 2B
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
    
    # A Function that gets the voted value from the databse and returns it
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
    
    # A Function that gets object id by name
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

    
    # A Function that grabs the votes documents and
    # candidates documents in or database and then
    # returns a dictionary of votes
    # {position: [name, party, votes], position : [name, party, votes]}



    def getVotes(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        votes_records = db.votes
        candidates_records = db.candidates

        candidate_list = candidates_records.find()
        candidate_description = [] #[name, party, votes]
        total = []

        votes = {} # {position: [name, party, votes], position : [name, party, votes]}

        for i in candidate_list:
            for key, value in i.items():
                if key == "name":
                    

                    list_position = i["position"].split("_")
                    position = " ".join(list_position).title()

                    # candidate_description = [i["name"], i["party"]]
                    # candidate_description.append(votes_records.count_documents({i["position"] : i["name"]})/float(votes_records.count_documents({}))*100)
                    
                    # votes = {position: []}
                    # votes[position].append(candidate_description)
                    votes = {position: []}
                    # votes[position].append(i["position"])
                    votes[position].append(i["name"])
                    votes[position].append(i["party"])
                    votes[position].append(str(int((votes_records.count_documents({i["position"] : i["name"]})/float(votes_records.count_documents({}))*100))) + "%")

                    total.append(votes)
        
        print(total)
            
                
        return total
    

    def getPositions(self):
        client = pymongo.MongoClient('localhost', 27017)
        db = client.get_database('election-system-test')
        candidates_records = db.candidates

        candidates = candidates_records.find()

        positions = []
        positions_parsed = []

        for i in candidates:
            if i["position"] not in positions:
                # list_position = i["position"].split("_")
                # position = " ".join(list_position).title()
                # positions.append(position)
                positions.append(i["position"])
            else:
                pass
        
        for i in positions:
            list_positions = i.split("_")
            parsed_list = " ".join(list_positions).title()
            positions_parsed.append(parsed_list)

        return positions_parsed


    

    

