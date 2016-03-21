__author__ = 'stoebelj'
from boxsdk import OAuth2, Client
import json
import requests

import sys
sys.path.insert(0, '.')
import token_refresh

class ClientWrapper(object):

    def __init__(self, secrets):
        """
        secrets: location of a json file containing:
            client_id
            client_secret
            access_token
            refresh_token
        post:
            instantiates a Client object
        """

        self.secrets = secrets
        token_refresh.main()     #refresh token

        with open(self.secrets, 'r') as secrets_file:
            secrets = json.load(secrets_file)
            oauth = OAuth2(
                client_id = secrets['client_id'],
                client_secret = secrets['client_secret'],
                access_token = secrets['access_token']
            )

        self.client = Client(oauth)


def connect():
    """
    pre: none
    post: either connects to box account, if it fails, raises an error
    """
    with open('secrets.json', 'r') as secrets_file:
        secrets = json.load(secrets_file)
        oauth = OAuth2(
            client_id = secrets['client_id'],
            client_secret = secrets['client_secret'],
            access_token = secrets['access_token']
        )

    client = Client(oauth)

    print client.user(user_id='me').get()['login']

def main():

    secrets = 'secrets.json'
    cw = ClientWrapper(secrets)
    print cw.client.user(user_id='me').get()['login']

if __name__ == '__main__':
    main()