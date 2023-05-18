import auth.auth as auth
from flask import Flask, Response, redirect, request, url_for
import json
@auth.auth_required()
def whoami(request):
    return Response(status=200,
                    mimetype='application/json',
                    response=json.dumps(request.user_info))