import auth.auth as auth
from flask import Flask, Response, redirect, request, url_for
import json

from config import GOOGLE_CLIENT_ID


@auth.auth_required()
def whoami(request):
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps(request.user_info))