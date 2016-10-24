# -*- coding: utf-8 -*-
import datetime
import os
import random
import shutil
import smtplib
import string
import time

import MySQLdb
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from ipahttp import ipa

external_email_body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: http://tihlde.org/lover/brukerreglement.htm \n\nHer har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://%s.tihlde.org og masse annet snacks. For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\nDu kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\nBrukernavn: %s\nPassord: %s\n\nDu vil bli bedt om å skifte passord ved første innlogging, det kan endres senere med kommando 'passwd'. Dette passordet blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på http://tihlde.org/ . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\nMvh\ndrift@tihlde.org"

tihlde_email_body = "Hei og velkommen til Tihlde! \n\nDu har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://%s.tihlde.org og masse annet snacks.\n\nOm du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"

home_dir_mode = 700
groupid = 7
log_file_path = '/var/log/brukerscript.log'


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


def log(entry):
    print(entry)
    with open(log_file_path, 'a') as log_file:
        log_file.write('\n' + entry)


def send_email(recipient, body):
    # TODO remove when user_add is used
    recipient = "harald_fw@live.no"

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
    except smtplib.SMTPException:
        log('Error: unable to send email to "' + recipient + '"')


def add_single_user(api, username, firstname, lastname, course, email, password):
    gecos = str(firstname) + ' ' + str(lastname) + ' ,' + str(email) + ' ,' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": "1007",
            "homedirectory": "/home/students/" + username
        }
    # TODO change to user_add when script is done
    response = api.stageuser_add(username, info)
    if response['error']:
        log('An error occured when calling IPA, continuing with next user')
        return
    return response['result']['result']['uidnumber']


def make_homedir(username, uid):
    new_home_dir = '/home/students/%s' % username
    # if dir exists, do nothing
    if os.path.exists(new_home_dir):
        log('Homedir for user %s not created, "%s" already exists, continuing with next user' % (username, new_home_dir))
        return

    # else, copy /etc/skel to /home/students/<username>
    shutil.copytree('/etc/skel', new_home_dir)
    # chown <username>:students /home/students/<username>
    os.chown(path=new_home_dir, uid=uid, gid=groupid)
    # chmod 700 /home/students/<username>
    os.chmod(path=new_home_dir, mode=home_dir_mode)


def add_all_users():
    # Connection to the database
    mreg_db = MySQLdb.connect(host="tihlde.org",
                              user="medlemsregister",
                              passwd=open("/home/staff/drift/passord/db-medlemsregister").readline().replace('\n', ''),
                              db="medlemsregister")
    mreg_cursor = mreg_db.cursor()

    apache_db = MySQLdb.connect(host="localhost",
                                user="apache",
                                passwd=open("/home/staff/drift/passord/db-apache").readline().replace('\n', ''),
                                db="apache")
    apache_cursor = apache_db.cursor()

    api = ipa("ipa1.tihlde.org", sslverify=True)
    # username, password(second line of ipa-admin password-file)
    api.login('admin', open("/home/staff/drift/passord/ipa-admin").readlines()[1].replace('\n', '').strip())

    date_from = '2016-08-01'
    date_to = '2016-10-16'

    mreg_cursor.execute(
        "SELECT fornavn, etternavn, linje, histbruker, epost FROM members "
        "WHERE timestamp BETWEEN %s AND %s AND aktivert = '1' AND eula = '1'" % (date_from, date_to))

    mailliste_path = '/tmp/maillisteopptak%s.txt' % time.time()
    mailliste_file = open('/tmp/%s' % mailliste_path, 'a')

    # loop to add every user pulled from the database to FreeIPA and
    # send them a mail with login information
    all = mreg_cursor.fetchall()

    response = str(input(str(len(all)) + " users to add. Continue? [y/n]"))
    if response.replace('\n', '').strip() != 'y':
        log('User called exit before adding users')
        return

    for row in all:
        # Extract data from row. order: fornavn, etternavn, linje, histbruker, epost
        firstname = str(row[0]).strip()
        lastname = str(row[1]).strip()
        course = str(row[2]).strip()
        username = str(row[3]).strip().lower()
        email = str(row[4]).strip().lower()
        generatedpw = generate_password()

        log('Adding user "' + username + '" with full name "' + str(firstname) + ' ' + str(lastname) + '"')
        uid = add_single_user(api, username, firstname, lastname, course, email, generatedpw)  # add user
        if not uid:
            log('Skipped sending emails, creating homedir and adding to mailinglist for user %s' % username)
            continue

        send_email(email, external_email_body % (username, username, generatedpw))  # send email to external email
        send_email(username + '@tihlde.org', external_email_body % (username))  # send email to tihlde-email

        mailliste_file.write(username + "@tihlde.org\n")

        apache_cursor.execute(
            "INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) "
            "VALUES (NULL, %s, %s, 'false', 'false', 'false', '');" % (username, str(groupid)))
        # TODO uncomment when run with user_add and not stageuser_add
        # make_homedir(username, uid)

    # close mailliste_file
    mailliste_file.close()
    # close databases
    mreg_db.close()
    apache_db.close()
    # TODO uncomment when run with user_add and not stageuser_add
    # call(["python", "/var/lib/mailman/bin/add_members", "-r", mailliste_path, "-w", "n", "colusers"])
    # call(["python", "/var/lib/mailman/bin/add_members", "-r", mailliste_path, "-w", "n", "tihlde-info"])


def main():
    log('\nNew run of the script at %s' % datetime.datetime.now())
    euid = os.geteuid()
    if euid != 0:
        log('Exit because by script was run without root access')
    else:
        add_all_users()


main()
