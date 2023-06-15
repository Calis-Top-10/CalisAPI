from flask import Response, redirect, request, url_for
import requests
import json
# decorator for functions that require authentication
from google.oauth2 import id_token
from google.auth.transport import requests

from config import GOOGLE_CLIENT_IDS

def auth_required():
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            # check if Authorization header is present
            if 'X-Forwarded-Authorization' in request.headers:
                token = request.headers['X-Forwarded-Authorization']
            elif 'Authorization' in request.headers:
                token = request.headers['Authorization']
            else:
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps({
                                    'error': 'Missing Authorization header'
                                })
                                )
            # check if Authorization header is valid
            token_type = token.split(' ')[0]
            if token_type != 'Bearer':
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps({
                                    'error': 'Invalid Authorization header'
                                })
                                )
            # check if token is valid
            try:
                token_info = id_token.verify_oauth2_token(
                    token.split(' ')[1], requests.Request())
                print(token_info)
                if token_info['aud'] not in GOOGLE_CLIENT_IDS: #second one is for dev
                    raise ValueError('Wrong recipient. You are not authenticated through registered Calis app or website.')
                
            except Exception as e:
                print(json.dumps(token))
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps({
                                    'error': str(e)
                                })
                                )
            user = token_info['email']
            user_info = {
                'user': user,
                'name': token_info['name'],
                'picture': token_info['picture']
            }
            args[0].user_info = user_info
            return func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required():
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            if request.user_info['user'] not in ["c169dsx2787@bangkit.academy"]:
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps({
                                    'error': 'You are not an admin'
                                })
                                )
            return func(*args, **kwargs)
        return wrapper  
    return decorator
