import random
import auth.auth as auth
from flask import Flask, Response, redirect, request, url_for
import json

from swagger.render import render_swagger_ui

from datastore.datastore import initClient, datastore
import datetime
import uuid
from utils import response

client = initClient()

# load functions
from functions.profile import whoami, login, addChildren
from functions.admin import insertLesson, insertLessons

"""
TODO: 
=============================================
PLEASE REFACTOR THIS CODE AND MAKE IT MODULAR
=============================================
"""



@auth.auth_required()
def getLessonSByType(request):

    lesson_type = request.args.get('lessonType')

    if lesson_type == None:
        return response.missing_field('lessonType')
    
    query = client.query(kind='lesson')
    query.add_filter('lessonType', '=', lesson_type)
    results = list(query.fetch())

    if len(results) == 0:
        return Response(status=404,
                        mimetype='application/json',
                        response=json.dumps({"error": "No lessons found"}))
    
    for lesson in results:
        questionsIds = lesson.get('questions')
        questions = []
        for questionId in questionsIds:
            question = client.get(client.key('question', questionId))
            questions.append(question)
        lesson['questions'] = questions
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps({"lessons": results}, default=str))


# update user learning
@auth.auth_required()
def updateUserLearning(request): 

    if request.content_type.split(";")[0] != 'application/json':
        return Response(status=415,
                        mimetype='application/json',
                        response=json.dumps({"error": "Content-Type must be application/json"}))
    import datetime

    data = request.get_json()
    child = data.get('childId')
    lesson = data.get('lessonId')
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y')
    attempts = data['attempts'] 
    #check if the child belong to this user
    userId = request.user_info['user']
    userData = client.get(client.key('user',userId))

    if userData == None:
        return Response (status=401,
                        mimetype='application/json',
                        response=json.dumps({'error': 'Strange, you are not registered. Maybe /login first and thn make some child if you know what I mean {ಠʖಠ}'}))

    if userData.get('children').get(child) == None:
        return Response (status=403,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child Id not found or this child does not belong to you'}))
                        
    childLearningData = client.get(client.key('user_learning', child))
    childLearningData['completedLessonsObject'][lesson]={
        'timestamp': data.get('timestamp'),
        'insertedAt': datetime.datetime.now().strftime('%d/%m/%Y'),
        'attempts': attempts
    }

    dateOfLearning = data.get('timestamp')
    lastUpdated = str(childLearningData.get('weeklyLearningIndex').get('lastUpdated'))
    # if last updated is last week
    if lastUpdated != None and lastUpdated != '' and lastUpdated != 'None':
        try:
            lastUpdated = datetime.datetime.strptime(lastUpdated, '%d/%m/%Y')
        except:
            lastUpdated = datetime.datetime.strptime(lastUpdated, '%Y-%m-%d %H:%M:%S.%f%z')
        if lastUpdated.isocalendar()[1] < datetime.datetime.strptime(dateOfLearning, '%d/%m/%Y').isocalendar()[1]:
            integer = 0
        elif lastUpdated.isocalendar()[1] == datetime.datetime.strptime(dateOfLearning, '%d/%m/%Y').isocalendar()[1]:
            integer = childLearningData.get('weeklyLearningIndex').get('integer')
        else:
            integer = 0


    try :
        # get which day of the week it is
        dayOfLearning = datetime.datetime.strptime(dateOfLearning, '%d/%m/%Y').weekday()
        integer = integer | 1 << dayOfLearning

        childLearningData['weeklyLearningIndex'] = {
            'integer': integer,
            'lastUpdated': dateOfLearning
        }
    except Exception as e:
        return Response(status=500,
                        mimetype='application/json',
                        response=json.dumps({"error": str(e)}))

    for attempt in attempts:
        questionEntity = client.get(client.key('question', attempt['questionId']))
        tags = questionEntity.get("tags")
        score = 1 if attempt['isCorrect'] else -1
        
        for tag in tags:
            try:
                childLearningData['tagScoring'][tag] += score   
            except KeyError:
                childLearningData['tagScoring'][tag] = score

    client.put(childLearningData)

    return Response (status=200,
                    mimetype='application/json',
                    response=json.dumps({"message":"all good"}))

#metode post report tidak disimpan di db
@auth.auth_required() 
def userReport(request):
    userid = request.user_info['user']
    child = request.args.get('childId')

    if child == None:
        return response.missing_field('childId')
    
    userData = client.get(client.key('user',userid))
    if userData == None:
        return Response (status=401,
                        mimetype='application/json',
                        response=json.dumps({'error': 'Strange, you are not registered. Maybe /login first and thn make some child if you know what I mean {ಠʖಠ}'}))
    
    if userData.get('children').get(child) == None:
        return Response (status=403,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child Id not found or this child does not belong to you'}))
    
    childData = client.get(client.key('user_learning', child))
    if childData == None:
        return Response (status=500,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child learning data not found, please contact developer'}))
    
    tags = childData.get('tagScoring')
    tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    #  get tags that have score less than 2
    lessonThatNeedHelp = [tag for tag in tags if tag[1] < 2]

    weeklyLearningIndex = childData.get('weeklyLearningIndex').get('integer')
    weeklyLearningIndex = bin(weeklyLearningIndex)[2:].zfill(7)
    weeklyLearning = {
        'monday': weeklyLearningIndex[-1] == '1',
        'tuesday': weeklyLearningIndex[-2] == '1',
        'wednesday': weeklyLearningIndex[-3] == '1',
        'thursday': weeklyLearningIndex[-4] == '1',
        'friday': weeklyLearningIndex[-5] == '1',
        'saturday': weeklyLearningIndex[-6] == '1',
        'sunday': weeklyLearningIndex[-7] == '1'
    }
    return Response(
        status=200,
        mimetype='application/json',
        response=json.dumps({
            "email": userid,
            "childId": child,
            "tag": lessonThatNeedHelp,
            "learningProgress": weeklyLearning
        })
    )


@auth.auth_required()
def updateChild(request):
    userid = request.user_info['user']
    data = request.get_json()

    childId = data.get('childId')
    childName = data.get('childName')
    childAge = data.get('childAge')

    if childId == None:
        return response.missing_field('childId')
    if childName == None:
        return response.missing_field('childName')
    if childAge == None:
        return response.missing_field('childAge')
    
    userData = client.get(client.key('user',userid))
    if userData == None:
        return Response (status=401,
                        mimetype='application/json',
                        response=json.dumps({'error': 'Strange, you are not registered. Maybe /login first and thn make some child if you know what I mean {ಠʖಠ}'}))
    
    if userData.get('children').get(childId) == None:
        return Response (status=403,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child Id not found or this child does not belong to you'}))
    
    childData = userData.get('children').get(childId)
    childData['childName'] = childName
    childData['childAge'] = childAge
    userData['children'][childId] = childData
    client.put(userData)

    return Response (status=200,
                    mimetype='application/json',
                    response=json.dumps({"message":f"{childId} updated"}))


# TODO: use this function in pubsub
# instead of deleting the child, we should just set the status to inactive
# and schedule delete after n days
@auth.auth_required()
def deleteChild(request):
    userId = request.user_info['user']
    data = request.get_json()
    childId = data.get('childId')
    if childId == None:
        return response.missing_field('childId')
    
    # delete user learning
    client.delete(client.key('user_learning', childId))

    # delete child from user
    userData = client.get(client.key('user',userId))
    if userData == None:
        return Response (status=401,
                        mimetype='application/json',
                        response=json.dumps({'error': 'Strange, you are not registered. Maybe /login first and thn make some child if you know what I mean {ಠʖಠ}'}))
    
    if userData.get('children').get(childId) == None:
        return Response (status=403,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child Id not found or this child does not belong to you'}))
    
    del userData['children'][childId]
    client.put(userData)

    return Response (status=200,
                    mimetype='application/json',
                    response=json.dumps({"message":f"{childId} deleted"}))

@auth.auth_required()
def personalLesson(request):
    childId = request.args.get('childId')
    userId = request.user_info['user']

    if childId == None:
        return response.missing_field('childId')
    
    userData = client.get(client.key('user', userId))
    if userData == None:
        return Response (status=401,
                        mimetype='application/json',
                        response=json.dumps({'error': 'Strange, you are not registered. Maybe /login first and thn make some child if you know what I mean {ಠʖಠ}'}))
    if userData.get('children').get(childId) == None:
        return Response (status=403,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child Id not found or this child does not belong to you'}))
    
    childData = client.get(client.key('user_learning', childId))
    if childData == None:
        return Response (status=500,
                        mimetype='application/json',
                        response=json.dumps({'error': 'child learning data not found, please contact developer'}))
    
    lessonObj = {
        "lessonId": "p_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f"),
        "lessonType": "personal",
        "questions": []
    }

    # get all tags
    tags = childData.get('tagScoring')
    tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    #  get tags that have score less than 3
    questionCount = 10
    while questionCount > 0:
        try:
            tag = tags.pop()
        except IndexError:
            break
        # get question from datastore based on tag
        query = client.query(kind='question')
        query.add_filter('tags', '=', tag[0])
        question = list(query.fetch())[0]

        lessonObj['questions'].append(question)
        questionCount -= 1

    return Response(
        status=200,
        mimetype='application/json',
        response=json.dumps(lessonObj)
    )





    


def docs(request):
    return Response(status=200,
                    mimetype='text/html',
                    response=render_swagger_ui('calisgateway.yaml'))

