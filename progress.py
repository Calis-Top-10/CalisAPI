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
def raporku(request):
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps(request.user_data))

@auth.auth_required()
# Definisikan endpoint API untuk menghasilkan laporan
@app.route('/generate-report', methods=['POST'])
def generate_report():

    data = request.get_json()

    'email': data.get['email']
    'user_id': data.get['user_id'],
    'lessonCompleted': data.get['lesson_id'],
    'weeklyLearning': {
        senin: True
        selasa: False
        rabu: True
        kamis: True
        jumat: False
    }

    if not email or not user_id or not lessonCompleted or not weeklyLearning:
        return jsonify({'error': 'Data is not complete.'}), 400

    #laporan
    report = {
        'email': email,
        'user_id': user_id,
        'lessonsCompleted': [lesson_id],
        'weeklyLearning': weeklyLearning
    }

    # Mengembalikan laporan sebagai respons dalam format JSON
    return jsonify(report), 200




def docs(request):
    return Response(status=200,
                    mimetype='text/html',
                    response=render_swagger_ui('calisgateway.yaml'))

