import auth.auth as auth
from flask import Flask, Response, redirect, request, url_for
import json

from config import GOOGLE_CLIENT_ID
from swagger.render import render_swagger_ui

from datastore.datastore import initClient, datastore
import datetime
import uuid
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
    if request.content_type != 'application/json':
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
@auth.auth_required()
@auth.admin_required()    
def insertLesson(request):
    if request.content_type != 'application/json':
        return Response(status=415,
                        mimetype='application/json',
                        response=json.dumps({"error": "Content-Type must be application/json"}))
    
    data = request.get_json()

    # top properties
    lessonType = data.get('lessonType')
    lessonLevel = int(data.get('lessonLevel'))
    lessonId = str(uuid.uuid4())
    questions = data.get('questions')

    if lessonType == None:
        return response.missing_field('lessonType')
    if lessonLevel == None:
        return response.missing_field('lessonLevel')
    if questions == None:
        return response.missing_field('questions')
    try:
        questions[0]
    except Exception as e:
        return Response(status=400,
                        mimetype='application/json',
                        response=json.dumps({"error": "[-] " + str
                                             (e)}))
    
    # create lesson entity
    lesson_entity = datastore.Entity(key=client.key('lesson', lessonId))
    lesson_entity['lessonId'] = lessonId
    lesson_entity['lessonType'] = lessonType
    lesson_entity['lessonLevel'] = lessonLevel
    questionIds = []

    try:
        for question in questions:
            new_question = {}
            new_question['questionId'] = str(uuid.uuid4())
            new_question['questionType'] = question['type']
            new_question['tags'] = [] if question.get('tags') == None else question['tags']
            question.pop('type', None)
            question.pop('tags', None)
            question.pop('id', None)

            new_question['questionDetails'] = question

            # insert to datastore
            new_question_entity = datastore.Entity(key=client.key('question', new_question['questionId']))
            new_question_entity['questionId'] = new_question['questionId']
            new_question_entity['questionType'] = new_question['questionType']
            new_question_entity['questionDetails'] = new_question['questionDetails']
            new_question_entity['tags'] = new_question['tags']
            client.put(new_question_entity)

            questionIds.append(new_question['questionId'])

        lesson_entity['questions'] = questionIds
        client.put(lesson_entity)

    except Exception as e:
        return Response(status=500,
                        mimetype='application/json',
                        response=json.dumps({"error": str(e)}))
    
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps({
                        lessonId: lesson_entity
                    }, default=str))


@auth.auth_required()
@auth.admin_required()  
def insertLessons(request):
    if request.content_type != 'application/json':
        return Response(status=415,
                        mimetype='application/json',
                        response=json.dumps({"error": "Content-Type must be application/json"}))
    
    data = request.get_json()

    lessons = data.get('lessons')

    if lessons == None:
        return response.missing_field('lessons')
    
    try:
        lessons[0]
    except:
        return Response(status=400,
                        mimetype='application/json',
                        response=json.dumps({"error": "lessons must be a valid JSON object"}))
    totalLessons = 0
    lessonIds = {}
    for lesson in lessons:
        # top properties
        lessonType = lesson.get('lessonType')
        lessonLevel = int(lesson.get('lessonLevel'))
        lessonId = str(uuid.uuid4())
        questions = lesson.get('questions')

        if lessonType == None:
            return response.missing_field('lessonType')
        if lessonLevel == None:
            return response.missing_field('lessonLevel')
        if questions == None:
            return response.missing_field('questions')
        try:
            questions[0]
        except:
            return Response(status=400,
                            mimetype='application/json',
                            response=json.dumps({"error": "questions must be a valid JSON object"}))
        
        # create lesson entity
        lesson_entity = datastore.Entity(key=client.key('lesson', lessonId))
        lesson_entity['lessonId'] = lessonId
        lesson_entity['lessonType'] = lessonType
        lesson_entity['lessonLevel'] = lessonLevel
        questionIds = []

        lessonIds[lessonId] = len(questions)
        try:
            for question in questions:
                new_question = {}
                new_question['questionId'] = str(uuid.uuid4())
                new_question['questionType'] = question['type']
                new_question['tags'] = [] if question.get('tags') == None else question['tags']
                question.pop('type', None)
                question.pop('tags', None)
                question.pop('id', None)

                new_question['questionDetails'] = question


                # insert to datastore
                new_question_entity = datastore.Entity(key=client.key('question', new_question['questionId']))
                new_question_entity['questionId'] = new_question['questionId']
                new_question_entity['questionType'] = new_question['questionType']
                new_question_entity['questionDetails'] = new_question['questionDetails']
                new_question_entity['tags'] = new_question['tags']
                client.put(new_question_entity)

                questionIds.append(new_question['questionId'])

            lesson_entity['questions'] = questionIds
            client.put(lesson_entity)

            totalLessons += 1

        except Exception as e:
            return Response(status=500,
                            mimetype='application/json',
                            response=json.dumps({"error": str(e)}))
        
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps({"message": f"{totalLessons} lesson(s) inserted successfully",
                                         "lessonIds": lessonIds}, default=str))


def docs(request):
    return Response(status=200,
                    mimetype='text/html',
                    response=render_swagger_ui('calisgateway.yaml'))

