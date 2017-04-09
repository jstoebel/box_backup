# BOX Backup

By Jacob Stoebel

### Purpose

This is an example script for backing up to Box using the Box content API

### Set up

 * Install requirements: `pip install -r requirements.txt`
 * Configuration: You will need to create a json file called secrets.json with the following content:

        {
            "access_token": <your box api access token>,
            "client_id": <your client ID>,
            "client_secret": <your client secret>,
            "refresh_token": <your refresh token>
        }

 * For more details on authentication with the Box API see [this](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwjZ1obuj-TLAhXIuB4KHRDoDbwQFggdMAA&url=https%3A%2F%2Fdevelopers.box.com%2F&usg=AFQjCNEo1ZIH456h--L1cri3j8YcoF9TjQ&sig2=rs3pCNC-dnPhhNQmch_f2g).

### Usage

```
python main.py --src "/dir/to/backup" --dest "box_folder"
```

### How it works

This program will

 * Attempt to refresh its access token. If there is a failure, it will log the failure.
 * create a new, time stamped folder in the box folder you specified.
 * copy all items from the specified folder to the newly created box folder.
 * NOTE: The destination folder in box must be in the root folder. I would like to change this in the near future.
