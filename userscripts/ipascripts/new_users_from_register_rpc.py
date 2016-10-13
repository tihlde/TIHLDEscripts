# -*- coding: utf-8 -*-
import random
import string
import MySQLdb
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from ipahttp import ipa

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


def send_email(recipient, body):
    recipient = "harald_fw@live.no"
    sender = 'drift@tihlde.org'
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Brukerkonto på Colargol"
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, recipient, text)
        print('Successfully sent email to "' + recipient + '"')
    except smtplib.SMTPException:
        print('Error: unable to send email to "' + recipient + '"')


def add_single_user(api, username, firstname, lastname, course, email, password):
    gecos = str(firstname) + ' ' + str(lastname) + ',' + str(email) + ',' + str(course)

    info = \
        {
            "givenname": firstname,
            "sn": lastname,
            "userpassword": password,
            "gecos": gecos,
            "gidnumber": "1007",
            "homedirrectory": "/home/students/" + username
        }
    print(api.stageuser_add(username, info))



def main():
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
    api.login('admin', 'd5rqv8HCnwxYuB')

    date_from = '2016-08-01'
    date_to = '2016-10-01'

    mreg_cursor.execute(
        "SELECT fornavn, etternavn, linje, histbruker, epost FROM members WHERE timestamp BETWEEN '" + date_from + "' AND '" + date_to + "' AND aktivert = '1' AND eula = '1'")

    # loop to add every user pulled from the database to FreeIPA and
    # send them a mail with login information
    all = mreg_cursor.fetchall()
    for row in all:
        # Extract data from row. order: fornavn, etternavn, linje, histbruker, epost
        firstname = str(row[0]).strip()
        lastname = str(row[1]).strip()
        course = str(row[2]).strip()
        username = str(row[3]).strip().lower()
        email = str(row[4]).strip().lower()
        gecos = str(firstname) + ' ' + str(lastname) + ',' + str(email) + ',' + str(course)
        generatedpw = generate_password()

        print('Adding user "' + username + '" with full name "' + str(firstname) + ' ' + str(lastname) + '"')
        # add user
        add_single_user(api, username, firstname, lastname, course, email, generatedpw)

        body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: http://tihlde.org/lover/brukerreglement.htm \n\nHer har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + username + ".tihlde.org og masse annet snacks. For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\nDu kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\nBrukernavn: " + username + " \nPassord: " + generatedpw + " \n\nDu vil bli bedt om å skifte passord ved første innlogging, det kan endres senere med kommando 'passwd'. Dette passordet blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på http://tihlde.org/ . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\nMvh\ndrift@tihlde.org"
        send_email(email, body)

        body = "Hei og velkommen til Tihlde! \n\nDu har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + username + ".tihlde.org og masse annet snacks.\n\nOm du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"
        send_email(username + '@tihlde.org', body)

        # apachecursor.execute("INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) VALUES (NULL, '"+ username +"', '7', 'false', 'false', 'false', '');")

    mreg_db.close()
    apache_db.close()


main()
