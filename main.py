import argparse
import calendar
import inspect
import json
import os
import time

from boxsdk import OAuth2, Client
import boxsdk

import sys
sys.path.insert(0, '.')
import token_refresh

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

class ClientWrapper:

    def __init__(self, secrets, root):
        """
        :param secrets: location of secrets file
        :param root: the root back up folder in box to place any copies

        TODO: current root is assumed to live inside the top level fox folder (id=0). Generalize to allow for user
        to enter a path to a box folder anywhere in their tree
        """

        secrets_path = os.path.join(THIS_DIR, secrets)

        token_refresh.main(secrets_path)     #refresh token

        with open(secrets_path, 'r') as secrets_file:
            secrets = json.load(secrets_file)
            oauth = OAuth2(
                client_id = secrets['client_id'],
                client_secret = secrets['client_secret'],
                access_token = secrets['access_token']
            )

        self.client = Client(oauth)

        #CHANGE THIS TO THE DIRECTORY OF WHERE YOUR UPLOADS WILL GO.
        self._get_root_folder(root)

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
            match = self.client.search(name, result_size, offset)
            for m in match:
                if m.parent is None:    #items in the root folder will pass here.
                    backup_root = m
            if (backup_root is not None) or (not match):
                break
            else:
                offset += result_size

        if backup_root:
            # we found the folder!
            self.backup_root = backup_root
        else:
            # create the folder if it wasn't found
            self.backup_root = self.client.folder(folder_id=0).create_subfolder(name)

    def _go_to(self, path):
        """
        walks to and/or creates path from starting folder
        :param starting_folder: box folder object
        :param path: list of directories
        :return: the box folder object that was created
        """

        current_folder = self.backup_root

        for p in path:
            # try to make it. If we fail, navigate to it.
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

    def prep_copy(self, root_dir):
        """
        look over root directory and copy any directories not already added to box
        """
        self.root_dir = root_dir
        box_contents = _ls(self.backup_root)
        box_names = frozenset([i.name for i in box_contents if i.type == 'folder']) # all of the items in this folder in box

        archives = frozenset(os.listdir(root_dir)) # all of the archives in the dir to be backed up

        new_items = archives - box_names
        for i in new_items:
            print('coping {}...'.format(i))
            self._copy(os.path.join(root_dir, i))
            print('-> Done!')

    def _copy(self, copy_dir):
        """
        copy_dir is copied into backup_root
        copy_dir: path to dir to copy
        """
        for dirname, child_dirs, files in os.walk(copy_dir):
            relative_path = os.path.relpath(dirname, self.root_dir)
            relative_path_split = _splitpath(relative_path)
            box_folder = self._go_to(relative_path_split)
            for f in files:
                uploaded = box_folder.upload(os.path.join(dirname, f), f, preflight_check=True)

def _ls(folder):
    """
    folder: box_folder to list contents
    contents of folder are listed (list of box items)
    """

    offset = 0
    limit = 1000
    results = []
    while True:
        items = folder.get_items(limit=limit, offset=offset)
        if items:
            results += items
            offset += limit
        else:
            return results

def _find_in_pwd(folder, name, type):
    """
    find an item in the current box folder
    :param folder: box folder to search in
    :param name: name of item (string)
    :param type: type of item (folder or item)
    :return: return the item object if found, otherwise raise an exception
    """

    items = _ls(folder)
    for i in items:
        if i.name == name and i.type == type:
            return i

    #didn't find it!
    raise IndexError('Could not find {name} in {folder}'.format(name=name, folder=folder.name))

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

    parser = argparse.ArgumentParser(description='Archive to Box')

    parser.add_argument('--src', help='The directory to copy from.')
    parse.add_argument('--dest', help="The folder in box to copy to. Must be in root folder")
    args = parser.parse_args()

    secrets = 'secrets.json' #define this file yourself and place it in the root directory.
    wrapper = ClientWrapper(secrets, args.dest)

    wrapper.prep_copy(args.src)

if __name__ == '__main__':
    main()
