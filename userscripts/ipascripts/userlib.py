# coding: utf-8
import os
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pymysql

from userscripts.ipascripts.ipahttp import ipa

__author__ = 'Harald Floor Wilhelmsen'


def is_root():
    return os.geteuid() == 0


def generate_password(pwlen):
    """
    Generates a password with lower and upper case letters and numbers.
    :param pwlen: Length of the password
    :return: The generated password as a string
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    nums = string.digits
    pw = []
    for i in range(pwlen):
        lower_index = random.randint(0, len(lower) - 1)
        pw.append(lower[lower_index])

    for i in range(int(pwlen / 2)):
        upper_index = random.randint(0, len(upper) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = upper[upper_index]

    for i in range(int(pwlen / 4)):
        num_index = random.randint(0, len(nums) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = nums[num_index]
    return ''.join(pw)


def get_ipa_api(uri='ipa1.tihlde.org'):
    """
    Create an api towards ipa with the given uri.
    :param uri: Uri towards an ipa-server. Will be ipa1.tihlde.org if left at None
    :return: The api
    """
    api = ipa(uri, sslverify=True)
    # username, password(second line of ipa-admin password-file)
    api.login('admin', open("/home/staff/drift/passord/ipa-admin").readlines()[1].replace('\n', '').strip())
    return api


def add_user_ipa(username, firstname, lastname, groupid, homedir_base, course=None, email=None, password=None,
                 api=None):
    """
    Adds a single user to ipa and apache
    :param homedir_base: the directory to place this user's home in. Example: /home/students/
    :param password: The password of the new user. If null, one will be generated using @generate_password
    :param api: API towards FREEIPA. This method assumes a login-request has been successful towards the IPA-server.
            If None, an ipa api object will be created towards ipa1.tihlde.org, and a login-request will be sent.
            If adding more than one user, you should get the api first, using the method @get_ipa_api and pass it
            in to all your method-calls.
    :return: The password and user id of the created user in an array; [uid, pw]
    """
    if not api:
        api = get_ipa_api()

    if not password:
        password = generate_password(12)

    if not homedir_base[-1] == '/':
        homedir_base += '/'

    gecos = str(firstname) + ' ' + str(lastname) + ' ,' + str(email) + ' ,' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": groupid,
            "homedirectory": homedir_base + username
        }

    response = api.user_add(username, info)
    error_response = response['error']
    if error_response:
        return
    return [response['result']['result']['uidnumber'], password]


def mysql_connect(host, username, password, database_name, charset='utf8'):
    return pymysql.connect(host=host,
                           user=username,
                           password=password,
                           database=database_name,
                           charset=charset)


def add_user_apache(username, groupid, apache_conn=None, apache_cursor=None, commit_and_close=True):
    """
    Inserts a single user into the apache database
    :param username: The username of the user to add to the database
    :param groupid: Group id of the new user. In sql style. E. g. students us '7'
    :param apache_conn: PyMySQL connection object. If None a new one will be created
    :param apache_cursor: PyMySQL cursor-object. If None a new one will be
    :param commit_and_close: Set to False if this method should NOT commit the query and
            close the cursor and connection to the database. Default if True
    :return: None if successful. An error-message if not.
    """
    if not apache_cursor:
        if not apache_conn:
            apache_pw = open("/home/staff/drift/passord/db-apache").readline().rstrip('\n')
            apache_conn = mysql_connect("localhost", "apache", apache_pw, "apache")
        apache_cursor = apache_conn.cursor()
    try:
        apache_cursor.execute(
            "INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) "
            "VALUES (NULL, '{0}', '{1}', 'false', 'false', 'false', '');".format(username, str(groupid)))
        if commit_and_close:
            apache_conn.commit()
            apache_cursor.close()
            apache_conn.close()
        return
    except pymysql.Error as err:
        return 'Error when pushing user {0} to the apache database:\n{1}' \
            .format(username, err)


def send_email(recipient, subject, body, sender='drift@tihlde.org', smtp_host='localhost'):
    """
    Sends an email with the given data to the given recipient.
    :param recipient: Recipient email address
    :param subject: Subject of the email
    :param body: Body of the email
    :param sender: Email address of the sender
    :param smtp_host: Host to send the email with. Standard is 'localhost'
    :return: None if successful. Error-msg if not.
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    text = msg.as_string()
    try:
        smtpObj = smtplib.SMTP(smtp_host)
        smtpObj.sendmail(sender, recipient, text)
    except smtplib.SMTPException as error:
        return 'Error: unable to send email to "{0}". Error-msg:\n{1}'.format(recipient, error)


def user_get(username, api=None):
    if not api:
        api = get_ipa_api()
    api.user_find(username)
