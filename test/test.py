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
        self.wrapper = backup_main.ClientWrapper(self.secrets_loc, 'backup_test')

    def tearDown(self):
        """
        delete the test folder
        """
        self.wrapper.backup_root.delete()

    def testConstructor(self):
        """
        tests that:
            the ClientWrapper is instantiated
            self.backup_root is created
            self.current_root is created
        """
        self.assertIs(type(self.wrapper.client), client.Client)
        self.assertIs(type(self.wrapper.backup_root), folder.Folder)
        self.assertIs(type(self.wrapper.backup_root), folder.Folder)

    def testcopy(self):
        """
        tests:
            tests that folder was copied exactly into box.
        """

        copy_dir = 'test_root' # relative to pwd
        self.wrapper.prep_copy(copy_dir)

        #walk through the backup folder and confirm that everything matches the target backup folder
        for dirname, child_dirs, files in os.walk(copy_dir):
            relative_path = os.path.relpath(dirname, copy_dir)      #get relative path from root directory
            relative_path_split = backup_main._splitpath(relative_path)

            # get the coorsponding box folder
            box_folder = self.wrapper.backup_root   # starting with the root folder

            for child in relative_path_split:
                if child != ".": # ASSUMPTION: no loose files in the root directory.
                    box_folder = backup_main._find_in_pwd(box_folder, child, 'folder')

            all_contents = backup_main._ls(box_folder)

            box_items = [i.name for i in all_contents if i.type == 'file']
            box_items.sort()
            self.assertEqual(box_items, sorted(files))

    def testcopy_has_existing(self):
        """
        attempts the same as above except one archive will already be in Box
        if no error is raised the test has passed!
        """

        # set up, upload archive1
        self.wrapper.prep_copy('test_root/archive1')
        self.wrapper.prep_copy('test_root')

class TokenRefreshTest(unittest.TestCase):

    def setUp(self):
        self.secrets_loc = '../secrets.json'
        # self.wrapper = backup_main.ClientWrapper(self.secrets_loc)

    def tearDown(self):
        pass

    def testRefresh(self):
        """
        tests that the tokens were successfully refreshed
        """
        with open(self.secrets_loc) as secrets_first:
            secrets_pre = secrets_first.read()

        token_refresh.refresh(self.secrets_loc)
        with open(self.secrets_loc) as secrets_second:
            secrets_post = secrets_second.read()

        self.assertNotEqual(secrets_pre, secrets_post)

    def testLog_fail(self):
        """
        tests that the log file is successfully changed
        :return:
        """

        #first create the log file if it doesn't exist
        test_log_loc = 'test_log.txt'

        with open(test_log_loc, 'w+') as log_handle:
            log_pre = log_handle.read()

        token_refresh.log_fail(test_log_loc, 'spam') #run the function

        with open(test_log_loc, 'rw+') as log_handle_post:
            log_post = log_handle_post.read()
            self.assertNotEqual(log_pre, log_post)
            log_handle_post.write(log_pre)
            # log_handle_post.truncate()
            self.assertEqual(log_handle_post.read(), log_pre) # make sure log was rolled back



if __name__ == '__main__':

    test_classes_to_run = [ClientWrapperTest, TokenRefreshTest]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)