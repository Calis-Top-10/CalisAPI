import os 
# TODO: git archive --output=/tmp/calis-gcf-source.zip --format=zip HEAD
GOOGLE_CLIENT_IDS = os.environ.get('GOOGLE_CLIENT_IDS')
GOOGLE_CLIENT_IDS = GOOGLE_CLIENT_IDS.split(',')
GOOGLE_CLIENT_IDS.append('327782085729-eqlor5jbl9cv3c06b77np9ic8so0sl01.apps.googleusercontent.com') # for dev