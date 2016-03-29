import os
import sys
import unittest

from boxsdk import client, folder

sys.path.insert(0, '..')
import main as backup_main
import token_refresh

class ClientWrapperTest(unittest.TestCase):

    def setUp(self):
        self.secrets_loc = '../secrets.json'
        self.wrapper = backup_main.ClientWrapper(self.secrets_loc)

    def tearDown(self):
        """
        delete the current_folder
        """
        self.wrapper.current_backup.delete()

    # def _go_to(self, child):
    #     """
    #     go to the immediate child folder of name dir
    #     self.current_folder is changed
    #     """
    #
    #     folder = self.wrapper._find_in_pwd(dir)


    def testConstructor(self):
        """
        tests that:
            the ClientWrapper is instantiated
            self.backup_root is created
            self.current_root is created
        """
        self.assertIs(type(self.wrapper.client), client.Client)
        self.assertIs(type(self.wrapper.backup_root), folder.Folder)
        self.assertIs(type(self.wrapper.current_backup), folder.Folder)

    def test_copy(self):
        """
        tests:
            tests that folder was copied exactly into box.
        """

        copy_dir = 'test_folder'
        self.wrapper.copy(copy_dir)

        #walk through the backup folder and confirm that everything matches the target backup folder
        for dirname, child_dirs, files in os.walk(copy_dir):
            relative_path = os.path.relpath(dirname, copy_dir)      #get relative path from root directory
            relative_path_split = backup_main._splitpath(relative_path)

            #get the coorsponding box folder
            box_folder = self.wrapper.current_backup

            for child in relative_path_split:
                if child != ".":
                    box_folder = backup_main._find_in_pwd(box_folder, child, 'folder')

            #get items in box folder
            all_contents = []
            limit = 100
            offset = 0
            while True:
                results = box_folder.get_items(limit=limit, offset=offset)
                if results:
                    all_contents += results
                    offset += limit
                else:
                    break

            box_items = [i.name for i in all_contents if i.type == 'file']
            box_items.sort()
            self.assertEqual(box_items, sorted(files))

class TokenRefreshTest(unittest.TestCase):

    def setUp(self):
        self.secrets_loc = '../secrets.json'
        # self.wrapper = backup_main.ClientWrapper(self.secrets_loc)

    def tearDown(self):
        pass

    def test_refresh(self):
        """
        tests that the tokens were successfully refreshed
        """
        with open(self.secrets_loc) as secrets_first:
            secrets_pre = secrets_first.read()

        token_refresh.refresh(self.secrets_loc)
        with open(self.secrets_loc) as secrets_second:
            secrets_post = secrets_second.read()

        self.assertNotEqual(secrets_pre, secrets_post)

    def test_log_fail(self):
        """
        tests that errors are successfully logged
        :return:
        """

        

if __name__ == '__main__':
    main(sys.argv)
