import auth.auth as auth
from flask import Flask, Response, redirect, request, url_for
import json

from config import GOOGLE_CLIENT_ID
from swagger.render import render_swagger_ui

@auth.auth_required()
def whoami(request):
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps(request.user_info))

def docs(request):
    return Response(status=200,
                    mimetype='text/html',
                    response=render_swagger_ui('calisgateway.yaml'))