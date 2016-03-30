import calendar
import json
import os
import time

from boxsdk import OAuth2, Client
import boxsdk

import sys
sys.path.insert(0, '.')
import token_refresh

class ClientWrapper:

    def __init__(self, secrets):
        token_refresh.main(secrets)     #refresh token
        with open(secrets, 'r') as secrets_file:
            secrets = json.load(secrets_file)
            oauth = OAuth2(
                client_id = secrets['client_id'],
                client_secret = secrets['client_secret'],
                access_token = secrets['access_token']
            )

        self.client = Client(oauth)

        #CHANGE THIS TO THE DIRECTORY OF WHERE YOUR UPLOADS WILL GO.
        self._get_root_folder('EDSdata_backup')

    def _get_root_folder(self, name):
        """
        finds the backup folder name, located in the root directory
        :param
            name: name of folder to locate
        :return: the folder object, found in the parent directory, matching name is bound to object
            backup_root: the root directory of where all backups are kept (box folder)
        """
        backup_root = None
        offset = 0
        result_size = 100       #how many results in each request?
        while True:
            match = self.client.search('EDSdata_backup', result_size, offset)
            for m in match:
                if m.parent is None:    #items in the root folder will pass here.
                    backup_root = m
            if backup_root is not None:
                break
            else:
                offset += result_size

        self.backup_root = backup_root

    def _go_to(self, path):
        """
        walks to and/or creates path from starting folder
        :param starting_folder: box folder object
        :param path: list of directories
        :return: the box folder object that was created
        """

        current_folder = self.backup_root

        for p in path:
            #try to get make it. If we fail, navigate to it.
            try:
                current_folder = current_folder.create_subfolder(p)     #create the folder
            except boxsdk.exception.BoxAPIException, e:
                if e.status == 409:     #trying to make an item that exists.

                    #simply "cd" into that folder
                    current_folder = _find_in_pwd(current_folder, p, 'folder')
                else:
                    # we got some other error -> raise
                    raise e

        return current_folder

    def copy(self, copy_dir):
        """
        :return: copy_dir and all its contents are copied to the dest_folder
        """

        # self._copy_setup()  #creates folder for backups
        for dirname, child_dirs, files in os.walk(copy_dir):
            relative_path = os.path.relpath(dirname, copy_dir)      #get relative path from root directory
            relative_path_split = _splitpath(relative_path)

            if relative_path_split == ["."]: # special case for root directory
                box_folder = self.backup_root
            else:
                box_folder = self._go_to(relative_path_split)

            for f in files:
                uploaded = box_folder.upload(os.path.join(dirname, f), f, preflight_check=True)
                #copy all items in path to box_folder

def _find_in_pwd(folder, name, type):
    """
    find an item in the current box folder
    :param folder: box folder to search in
    :param name: name of item (string)
    :param type: type of item (folder or item)
    :return: return the item object if found, otherwise raise an exception
    """

    offset = 0
    limit = 100
    while True:
        items = folder.get_items(limit=limit, offset=offset)
        if not items:
            #nothing found!
            raise IndexError('Attempting to search with index beyond upper bound of folder.')
        for i in items:
            if i.name==name and i.type == type:
                return i
        #didn't find it
        offset += limit

def _splitpath(path):
    """
    found here: https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch04s16.html
    :param path: a file path
    :return: a list of directories composing path
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])    # pop the last directory, insert and repeat
    return allparts

def main():

    secrets = 'secrets.json' #define this file yourself and place it in the root directory.
    wrapper = ClientWrapper(secrets)

    #CHANGE THIS TO COPY WHAT EVER FOLDER YOU WANT.
    wrapper.copy('test_folder')

if __name__ == '__main__':
    main()
