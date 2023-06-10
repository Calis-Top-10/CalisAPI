import auth.auth as auth
from flask import Response
import json
from datastore.datastore import initClient, datastore
import datetime, uuid
from utils import response

client = initClient()

@auth.auth_required()
def whoami(request):
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps(request.user_info))

@auth.auth_required()
def login(request):

    email = request.user_info['user']

    #get user from datastore
    user_data = client.get(client.key('user', email))
    if(user_data == None):
        new_user = datastore.Entity(key=client.key('user', email))
        new_user['createdAt'] = datetime.datetime.utcnow()
        new_user['email'] = email
        new_user['children'] = {}
        client.put(new_user)

        return Response(status=200,
                        mimetype='application/json',
                        response=json.dumps(new_user, default=str))
    else:
        return Response(status=200,
                        mimetype='application/json',
                        response=json.dumps(user_data, default=str))

@auth.auth_required()    
def addChildren(request):
    # check content type
    if request.content_type.split(";")[0] != 'application/json':
        return Response(status=415,
                        mimetype='application/json',
                        response=json.dumps({"error": "Content-Type must be application/json"}))
    
    # get data from request
    data = request.get_json()
    childName = data.get('childName')
    childAge = data.get('childAge')

    email = request.user_info['user']

    if childName == None:
        return response.missing_field('childName')
    if childAge == None:
        return response.missing_field('childAge')

    user_data = client.get(client.key('user', email))
    if(user_data == None):
        return Response(status=404,
                        mimetype='application/json',
                        response=json.dumps({"error": "User not found, are you sure you are logged in?"}))
    else:
        # create children entity
        child = {}
        child['childName'] = childName
        child['yearOfBirth'] = datetime.datetime.now().year - int(childAge)
        child['photoUrl'] = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.istockphoto.com%2Fphotos%2Fbaby&psig=AOvVaw0QZ2Z2Q4Z3Q4Z3Q4Z3Q4Z3&ust=1614784750000000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4Z3Q4-8CFQAAAAAdAAAAABAD"
        child['createdAt'] = datetime.datetime.utcnow()

        childId = str(uuid.uuid4())
        # check if childId already exists
        while client.get(client.key('user_learning', childId)) != None:
            childId = str(uuid.uuid4())

        user_data['children'][childId] = child
        client.put(user_data)

        # create user learning entity
        user_learning = datastore.Entity(key=client.key('user_learning', childId))
        user_learning['childId'] = childId
        user_learning['email'] = email
        user_learning['completedLessonsObject'] = {}
        user_learning['tagScoring'] = {}
        user_learning['weeklyLearningIndex'] = {
            "integer": 0,
            "lastUpdated": datetime.datetime.utcnow()
        }

        client.put(user_learning)

        return Response(status=200,
                        mimetype='application/json',
                        response=json.dumps({
                            childId: child
                        }, default=str))