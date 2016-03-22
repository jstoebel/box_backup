
import calendar
import json
import os
import sys
import time

from boxsdk import OAuth2, Client

import sys
sys.path.insert(0, '.')
import token_refresh

class ClientWrapper:

    def __init__(self, secrets):
        token_refresh.main()     #refresh token
        with open(secrets, 'r') as secrets_file:
            secrets = json.load(secrets_file)
            oauth = OAuth2(
                client_id = secrets['client_id'],
                client_secret = secrets['client_secret'],
                access_token = secrets['access_token']
            )

        self.client = Client(oauth)
        # self._get_root_folder('EDSdata_backup')

    def _get_root_folder(self, name):
        """
        finds the backup folder name, located in the root directory
        :param
            name: name of folder to locate
        :return: the folder object, found in the parent directory, matching name is bound to object
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

        dir_name = "backup_{}".format(calendar.timegm(time.gmtime()))
        print "attempting to make destination folder in Box:", dir_name
        self.current_backup = backup_root.create_subfolder(dir_name)


    def _go_to(self, path):
        """
        walks to and/or creates path from starting folder
        :param starting_folder: box folder object
        :param path: list of directories
        :return: the box folder object that was created
        """

        folder = self.current_backup
        for p in path:
            #try to get it, or create it
            _is_in_folder(folder, p)



            #grab an existing folder
            # folder = folder.create_subfolder(p)     #create the folder
        return folder

    def copy(self, copy_dir):
        """
        :return: copy_dir and all its contents are copied to the dest_folder
        """

        # self._copy_setup()  #creates folder for backups
        for dirname, child_dirs, files in os.walk(copy_dir):
            relative_path = os.path.relpath(dirname, copy_dir)      #get relative path from root directory
            relative_path_split = _splitpath(relative_path)
            if relative_path_split != ["."]: # unless files are located in the root directory
                box_folder = self._go_to(relative_path_split)

        # # creates folder structure /L1/L2/L3
        # client.folder(folder_id='0').create_subfolder('L1').create_subfolder('L2').create_subfolder('L3')

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

def _is_in_folder(parent, child):
    """

    :param parent: box folder
    :param child: string of folder
    :return: returns if folder with child name is in parent folder
    """

    print parent.get_items(limit=100, offset=0)

def main():

    secrets = 'secrets.json'
    client = ClientWrapper(secrets)
    # client.copy("./test_folder")
    items = client.client.folder(folder_id='0').get_items(limit=100, offset=0)

    names = [i.name for i in items]
    print names

if __name__ == '__main__':
    main()
