# BOX Backup.

By Jacob Stoebel

### Purpose ###

This is an example script for backing up to Box using the Box content API

### Set up###

 * Install requirements: `pip install requirements.txt`
 * Configuration: You will need to create a json file called secrets.json with the following content:

    {
        "access_token": <your box api access token>,
        "client_id": <your client ID>,
        "client_secret": <your client secret>,
        "email_address": <your email address (if you want to use email alerts)>,
        "password": <your email password>,
        "recipient": <who should receive email alerts if api auth fails? Either a string or array>,
        "refresh_token": <your refresh token>
    }

 * For more details on authentication with the Box API see [this](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwjZ1obuj-TLAhXIuB4KHRDoDbwQFggdMAA&url=https%3A%2F%2Fdevelopers.box.com%2F&usg=AFQjCNEo1ZIH456h--L1cri3j8YcoF9TjQ&sig2=rs3pCNC-dnPhhNQmch_f2g).

### Set up###

This program will

 * Attempt to refresh its access token. If there is a failure, it will log the failure send an email.
 * create a new, time stamped folder in the box folder you specified.
 * copy all items from the specified folder to the newly created box folder.