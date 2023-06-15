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
from functions.profile import whoami, login, addChildren, updateChild, deleteChild, getChildById
from functions.admin import insertLesson, insertLessons
from functions.lesson import getLessonSByType, personalLesson, question, lesson
from functions.userlearning import updateUserLearning, userlearning, userReport

def docs(request):
    return Response(status=200,
                    mimetype='text/html',
                    response=render_swagger_ui('calisgateway.yaml'))

