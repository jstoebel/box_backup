__author__ = 'stoebelj'

from email.utils import formataddr
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import smtplib
import datetime

import os

import requests

def refresh(secrects_loc):
    """
    :param secrets: json string of secrets
    :return: new tokens are written to file
    """
    with open(secrects_loc, 'r') as secrets_file:
        secrets = json.load(secrets_file)

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': secrets['refresh_token'],
        'client_id': secrets['client_id'],
        'client_secret': secrets['client_secret']
    }

    url = 'https://api.box.com/oauth2/token'
    resp = requests.post(url, data=payload) #refresh the token

    try:
        resp.raise_for_status()     #raise an error if we get a bad response code
    except requests.HTTPError:
        raise requests.HTTPError('Bad request! Response: {r}'.format(r=resp.text))

    resp_data = json.loads(resp.text)

    #alter secrets
    secrets['access_token'] = resp_data['access_token']
    secrets['refresh_token'] = resp_data['refresh_token']

    #write new secrets to file
    with open(secrects_loc, 'w') as secrets_in:
        json.dump(secrets, secrets_in, indent=4, sort_keys=True)

    print "tokens refreshed!"

def EmailConnect(password, recipiant):
    '''Connects to email server and returns connection object.'''

    url = 'smtp.office365.com'
    mail_cnxn = smtplib.SMTP(url, 587)
    mail_cnxn.starttls()
    mail_cnxn.ehlo()
    mail_cnxn.login(recipiant, password)
    return mail_cnxn

def TestCnxnOpen(cnxn):
    """
    test that the mail connection is open.
    :param cnxn:
    :return:
    """
    try:
        status = cnxn.noop()[0]
    except smtplib.SMTPServerDisconnected:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False

def alert_fail(msg, password, recipiant):
    """
    logs an alert
    :return:
    """
    mail_cnxn = EmailConnect(password, recipiant)
    html_text = MIMEText(msg, 'html')
    email = MIMEMultipart('alternative')
    email.attach(html_text)
    sender = formataddr((str(Header(u'Jacob Stoebel', 'utf-8')), recipiant))
    email['Subject'] = "[EDS_dashboard] Box backup failed"
    email['From'] = sender
    email['To'] = recipiant
    mail_cnxn.sendmail(recipiant, recipiant, email.as_string())

def log_fail(log_loc, msg):
    """
    logs the failure
    """
    with open(log_loc, 'a') as log_writter:
        log_writter.write(msg)

def main(secrects_loc):

    try:
        refresh(secrects_loc)
    except requests.exceptions.HTTPError:

        with open(secrects_loc, 'r') as secrets_file:
            secrets = json.load(secrets_file)
        msg = """[{time_stamp}]
    Connection to Box failed! Please manually enter tokens and try again. Back up will not occur as normal until this is fixed!

""".format(time_stamp=str(datetime.datetime.now()))
        log_fail('log.txt', msg)

if __name__ == '__main__':
    main()
