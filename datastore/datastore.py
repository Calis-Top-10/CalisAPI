from google.cloud import datastore

def initClient():
    global client
    client = datastore.Client.from_service_account_json('datastore/cfds_sa.json')

    return client