# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import shutil
import smtplib
import string
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import call

import pymysql
from ipahttp import ipa

external_email_body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: http://tihlde.org/lover/brukerreglement.htm \n\nHer har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://{0}.tihlde.org og masse annet snacks. For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\nDu kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\nBrukernavn: {0}\nPassord: {1}\n\nDu vil bli bedt om å skifte passord ved første innlogging, det kan endres senere med kommando 'passwd'. Dette passordet blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på http://tihlde.org/ . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\nMvh\ndrift@tihlde.org"

tihlde_email_body = "Hei og velkommen til Tihlde! \n\nDu har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://{0}.tihlde.org og masse annet snacks.\n\nOm du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"

sql_groupid = 7
linux_groupid = 1007
log_file_path = '/var/log/brukerscript.log'
ipa_log_file_path = '/var/log/brukerscript.ipa.log'
error_log_file_path = '/var/log/brukerscript.error.log'


def generate_password():
    pwlen = 12
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


def log(entry, file=log_file_path, print_entry=True):
    if print_entry:
        print(entry)
    with open(file, 'a') as log_file:
        log_file.write(entry + '\n')


def send_email(recipient, body):
    # recipient = "harald_fw@live.no"

    sender = 'drift@tihlde.org'
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Brukerkonto på Colargol"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    text = msg.as_string()
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, recipient, text)
        log('Successfully sent email to "' + recipient + '"')
    except smtplib.SMTPException as error:
        log('Error: unable to send email to "' + recipient + '". Error-msg logged to error-log')
        log("Error-msg when sending mail to {0}\n{1}".format(recipient, error), file=error_log_file_path,
            print_entry=False)


def add_single_user(api, username, firstname, lastname, course, email, password):
    gecos = str(firstname) + ' ' + str(lastname) + ' ,' + str(email) + ' ,' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": linux_groupid,
            "homedirectory": "/home/students/" + username
        }

    response = api.user_add(username, info)
    error_response = response['error']
    if error_response:
        log('An error occured when calling IPA for user {0}. Logged to ipa log file'.format(username))
        log(json.dumps(error_response), file=ipa_log_file_path, print_entry=False)
        return
    return response['result']['result']['uidnumber']


def make_homedir(username, uid):
    new_home_dir = '/home/students/{0}'.format(username)
    # if dir exists, do nothing
    if os.path.exists(new_home_dir):
        log('Homedir for user {0} not created, "{1}" already exists, skipping'.format(username, new_home_dir),
            file=error_log_file_path)
        return

    # else, copy /etc/skel to /home/students/<username>
    shutil.copytree('/etc/skel', new_home_dir)
    # chown <username>:students /home/students/<username>
    call(['chown', '-R', uid + ':' + str(linux_groupid), new_home_dir])
    # chmod 700 /home/students/<username>
    os.chmod(path=new_home_dir, mode=0o700)


def add_all_users():
    # file to store email-addresses to add to mailinglists to
    mailliste_path = '/tmp/maillisteopptak{0}.txt'.format(time.time())
    mailliste_file = open(mailliste_path, 'a')

    # Connection to the database
    mreg_db = pymysql.connect(host="tihlde.org",
                              user="medlemsregister",
                              password=open("/home/staff/drift/passord/db-medlemsregister").readline().rstrip('\n'),
                              database="medlemsregister",
                              charset='utf8')
    mreg_cursor = mreg_db.cursor()

    apache_db = pymysql.connect(host="localhost",
                                user="apache",
                                password=open("/home/staff/drift/passord/db-apache").readline().replace('\n', ''),
                                database="apache",
                                charset='utf8')
    apache_cursor = apache_db.cursor()

    api = ipa("ipa1.tihlde.org", sslverify=True)
    # username, password(second line of ipa-admin password-file)
    api.login('admin', open("/home/staff/drift/passord/ipa-admin").readlines()[1].replace('\n', '').strip())

    log('Fetching users from database "medlemsregister"...')

    date_from = '2016-08-01'
    date_to = '2016-10-16'
    mreg_cursor.execute(
        "SELECT fornavn, etternavn, linje, histbruker, epost FROM members "
        "WHERE timestamp BETWEEN '{0}' AND '{1}' AND aktivert = '1' AND eula = '1'".format(date_from, date_to))

    # loop to add every user pulled from the database to FreeIPA and
    # send them a mail with login information
    mreg_users = mreg_cursor.fetchall()

    response = str(input(str(len(mreg_users)) + " users to add. Continue? [y/n]"))
    if response.replace('\n', '').strip() != 'y':
        log('User called exit before adding users')
        return

    for row in mreg_users:
        # Extract data from row. order: fornavn, etternavn, linje, histbruker, epost
        username = str(row[3]).strip().lower()
        firstname = str(row[0]).strip()
        lastname = str(row[1]).strip()
        course = str(row[2]).strip()
        email = str(row[4]).strip().lower()
        generatedpw = generate_password()

        log('Adding user "' + username + '" with full name "' + str(firstname) + ' ' + str(lastname) + '"')
        uid = add_single_user(api, username, firstname, lastname, course, email, generatedpw)  # add user
        if not uid:
            log('Skipped sending emails, creating homedir and adding to mailinglist for user {0}'.format(username))
            continue

        make_homedir(username, uid)

        send_email(email, external_email_body.format(username, generatedpw))  # send email to external email
        send_email(username + '@tihlde.org', tihlde_email_body.format(username))  # send email to tihlde-email

        mailliste_file.write(username + "@tihlde.org\n")
        try:
            apache_cursor.execute(
                "INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) "
                "VALUES (NULL, '{0}', '{1}', 'false', 'false', 'false', '');".format(username, str(sql_groupid)))
        except mysql.connector.Error as err:
            log("Something went wrong: {}".format(err))

    # close mailliste_file
    mailliste_file.close()
    # close databases
    mreg_db.close()
    apache_db.close()

    call(["python", "/var/lib/mailman/bin/add_members", "-r", mailliste_path, "-w", "n", "colusers"])
    call(["python", "/var/lib/mailman/bin/add_members", "-r", mailliste_path, "-w", "n", "tihlde-info"])


def main():
    euid = os.geteuid()
    if euid != 0:
        print('Needs to be run as root. Re-run with sudo')
    else:
        script_run_entry = '\nNew run of the script at {0}'.format(datetime.datetime.now())
        log(script_run_entry)
        log(script_run_entry, file=ipa_log_file_path, print_entry=False)
        log(script_run_entry, file=error_log_file_path, print_entry=False)
        add_all_users()


main()
