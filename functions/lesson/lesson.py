from datastore.datastore import initClient, datastore
import auth.auth as auth
from flask import Response
import json, datetime
from utils import response

client = initClient()


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

