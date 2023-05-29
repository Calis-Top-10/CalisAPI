from flask import Response
import json

def missing_field(field):
    return Response(status=400,
                    mimetype='application/json',
                    response=json.dumps({"error": f"{field} is required"}))