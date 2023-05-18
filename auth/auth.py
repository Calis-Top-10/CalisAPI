from flask import Response, redirect, request, url_for
import requests
import json
# decorator for functions that require authentication


def auth_required():
    def decorator(func):
        def wrapper(*args, **kwargs):
            request = args[0]
            # check if Authorization header is present
            if 'Authorization' not in request.headers:
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps({
                                    'error': 'Missing Authorization header'
                                })
                                )
            # check if Authorization header is valid
            token = request.headers['Authorization']
            user_info = get_user_info(token)
            if 'email' not in user_info:
                return Response(status=401,
                                mimetype='application/json',
                                response=json.dumps(user_info)
                                )
            args[0].user_info = user_info
            return func(*args, **kwargs)
        return wrapper
    return decorator

# get user email from token


def get_user_info(token):
    # request to google api to get user info
    response = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': token,
                 'Content-Type': 'application/json'
                 }
    )
    # return user email
    return response.json()
