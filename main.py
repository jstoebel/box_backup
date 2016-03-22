__author__ = 'stoebelj'
from boxsdk import OAuth2, Client
import json

import sys
sys.path.insert(0, '.')
import token_refresh

def connect(secrets):
    """
    pre: none
    post: either connects to box account, if it fails, raises an error
    """

    token_refresh.main()     #refresh token
    with open(secrets, 'r') as secrets_file:
        secrets = json.load(secrets_file)
        oauth = OAuth2(
            client_id = secrets['client_id'],
            client_secret = secrets['client_secret'],
            access_token = secrets['access_token']
        )

    client = Client(oauth)
    return client

def find_folder(client, name):
    """
    finds the backup folder name, located in the root directory
    :param
        client: the box client
        name: name of folder to locate
    :return: the folder object, found in the parent directory, matching name
    """

    backup_folder = None
    offset = 0
    result_size = 100       #how many results in each request?
    while True:
        match = client.search('EDSdata_backup', result_size, offset)
        for m in match:
            if m.parent is None:    #items in the root folder will pass here.
                backup_folder = m
        if backup_folder is not None:
            break
        else:
            offset += result_size

    return backup_folder

def main():


    secrets = 'secrets.json'
    client = connect(secrets)
    backup_folder = find_folder(client, 'EDSdata_backup')

    #recirsivly upload!

if __name__ == '__main__':
    main()
