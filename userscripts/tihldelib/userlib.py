# coding: utf-8
import os
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import call

import pymysql
import shutil

from tihldelib.ipahttp import ipa

__author__ = 'Harald Floor Wilhelmsen'


def get_external_email_body(username, password):
    """
    Returns a formatted email-body, intended to be sent to new members of TIHLDE after the enrollment party.
    :param username: the username of the recipient
    :param password: the password of the recipient
    :return: The formatted body-text
    """
    body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på " \
           "brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: " \
           "http://tihlde.org/lover/brukerreglement.htm \n\n" \
           "Her har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell " \
           "for adressen din http://{0}.tihlde.org og masse annet snacks. " \
           "For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\n" \
           "Du kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\n" \
           "Brukernavn: {0}\nPassord: {1}\n\n" \
           "Du vil bli bedt om å skifte passord ved første innlogging, det kan endres senere med kommando 'passwd'. " \
           "Dette passordet blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på " \
           "http://tihlde.org/ . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\n" \
           "Mvh\ndrift@tihlde.org"
    return body.format(username, password)


def get_tihlde_email_body(username):
    """
    Returns a formatted email-body, intended to be sent to the newly created colargol-user's @tihlde email-address
     after the enrollment-party.
    :param username: username of the new colargol-user
    :return: The formatted body-text
    """
    body = "Hei og velkommen til Tihlde! \n\n" \
           "Du har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, " \
           "samt webhotell for adressen din http://{0}.tihlde.org og masse annet snacks.\n\n" \
           "Om du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til " \
           "sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"
    return body.format(username)


def is_root():
    return os.geteuid() == 0


def get_group_info(group_name):
    user_groups = {'students': {'homedir_base': '/home/students', 'gid_lx': 1007, 'gid_sql': 7, 'quota': '10G'},
                   'drift': {'homedir_base': '/home/staff', 'gid_lx': 1010, 'gid_sql': 10, 'quota': '100G'},
                   'hs': {'homedir_base': '/home/hs', 'gid_lx': 1006, 'gid_sql': 6, 'quota': '10G'},
                   'xhs': {'homedir_base': '/home/hs', 'gid_lx': 1012, 'gid_sql': 12, 'quota': '10G'}}
    return user_groups[group_name]


def generate_password(password_length):
    """
    Generates a password with lower and upper case letters and numbers.
    :param password_length: Length of the password
    :return: The generated password as a string
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    nums = string.digits
    pw = []
    for i in range(password_length):
        lower_index = random.randint(0, len(lower) - 1)
        pw.append(lower[lower_index])

    for i in range(int(password_length / 2)):
        upper_index = random.randint(0, len(upper) - 1)
        pwindex = random.randint(0, password_length - 1)
        pw[pwindex] = upper[upper_index]

    for i in range(int(password_length / 4)):
        num_index = random.randint(0, len(nums) - 1)
        pwindex = random.randint(0, password_length - 1)
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


def get_ipa_api_if_not_exists(api):
    if not api:
        return get_ipa_api()
    return api


def format_home_basedir(homedir_base):
    if homedir_base[-1] != '/':
        homedir_base += '/'
    return homedir_base


def add_user_ipa(username, firstname, lastname, groupid, homedir_base, course=None, email=None, password=None,
                 api=None):
    """
    Adds a single user to ipa
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

    homedir_base = format_home_basedir(homedir_base)

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
    """
    Returns a connection-object to a MySQL database.
    :param host: host with database
    :param username: username to authenticate towards mysql
    :param password: password to authenticate towards mysql
    :param database_name: name of database
    :param charset: charset of communications between you and the database. Should not be overridden.
    :return: The connection object
    """
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
        smtp_obj = smtplib.SMTP(smtp_host)
        smtp_obj.sendmail(sender, recipient, text)
    except smtplib.SMTPException as error:
        return 'Error: unable to send email to "{0}". Error-msg:\n{1}'.format(recipient, error)


def user_get(username, api=None):
    """
    Gets a user from the given ipa api-object.
    :param username: username of the user to get
    :param api: Api towards the ipa-server. Should be overriden if this method should be used more than once.
            If None is given this method will create it's own api-object
    :return: A dictionary with response-data from IPA. You can use @user_exists_from_output with this output-
            object to find if a user exists.
    """
    if not api:
        api = get_ipa_api()
    return api.user_find(username)


def user_exists_from_output(user_get_output):
    """
    Returns True or False representing if a user exists or not, based on output from @user_get.
    :param user_get_output: Output from @user_get
    :return: True if the user exists. False otherwise
    """
    return user_get_output['result']['summary'] != '0 users matched'


def user_exists(username, api=None):
    """
    Uses @user_get and @user_exists_from_output to figure out the given user exists.
    :param username: username of the user to check
    :param api: api towards ipa. If not overridden a new api-object will be created towards ipa1.tihlde.org
            for each call of this method.
    :return: True if the user exists. False otherwise
    """
    api = get_ipa_api_if_not_exists(api)
    return user_exists_from_output(user_get(username, api))


def make_home_dir(homedir_base, username, uid, linux_groupid):
    homedir_base = format_home_basedir(homedir_base)
    new_home_dir = homedir_base + username
    # if dir exists, do nothing
    if os.path.exists(new_home_dir):
        return 'Dir already exists'

    # else, copy /etc/skel to /home/students/<username>
    shutil.copytree('/etc/skel', new_home_dir)
    # chown <uid>:<gid> /home/students/<username>
    call(['chown', '-R', uid + ':' + str(linux_groupid), new_home_dir])
    # chmod 700 /home/students/<username>
    os.chmod(path=new_home_dir, mode=0o700)


def set_quota(uid, quota_value):
    """
    Sets the quota for the given user to the given GB value.
    :param uid: Username of the user to set quota for
    :param quota_value: quota value
    :return: 'ok' if everything went well. None if not.
    """
    if is_root():
        call(['zfs', 'set', 'userquota@{0}={1}'.format(uid, quota_value), ' tank/home'])
        return 'ok'
    else:
        return None
