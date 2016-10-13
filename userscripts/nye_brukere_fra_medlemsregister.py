# -*- coding: utf-8 -*-
__author__ = 'Harald Floor Wilhelmsen'

import MySQLdb
import random
import string
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import subprocess

# ipa user-add <username> --homedir=/home/students --random --gidnumber=1007 --shell=/bin/bash --first=<firname> --last=<lastname>

def generate_password():
    pwlen = 12
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    nums = string.digits
    pw = []
    for i in range(pwlen):
        lower_index = random.randint(0, len(lower) - 1)
        pw.append(lower[lower_index])

    for i in range(int(pwlen/2)):
        upper_index = random.randint(0, len(upper) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = upper[upper_index]

    for i in range(int(pwlen/4)):
        num_index = random.randint(0, len(nums) - 1)
        pwindex = random.randint(0, pwlen - 1)
        pw[pwindex] = nums[num_index]
    return ''.join(pw)


pwmreg = open("/home/staff/drift/passord/db-medlemsregister").readline().replace('\n', '')

# Connection to the database
db = MySQLdb.connect(host="tihlde.org",
                     user="medlemsregister",
                     passwd=pwmreg,
                     db="medlemsregister")

apache = MySQLdb.connect(host="localhost",
                         user="apache",
                         passwd="b4rx5qFbDbFzYrWH",
                         db="apache")
apachecursor = apache.cursor()

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
        print 'Successfully sent email to "' + recipient + '"'
    except smtplib.SMTPException:
        print 'Error: unable to send email to "' + recipient + '"'

def get_password(input):
    for line in input.split('\n'):
        index = line.find('Random password:')
        if index != -1:
            return line[index + len('Random password:'):].strip()
    return ''

# Edit this to match the year of who you want to put in FreeIPA
year = "2016"

cur = db.cursor()
cur.execute(
    "SELECT fornavn, etternavn, linje, histbruker, epost FROM members WHERE timestamp BETWEEN '" + year + "-08-01' AND '" + year + "-10-01' AND aktivert = '1' AND eula = '1'")

# loop to add every user pulled from the database to FreeIPA and
# send them a mail with login information
all = cur.fetchall()
for row in all:
    # order: fornavn, etternavn, linje, histbruker, epost
    firstname = str(row[0]).strip()
    lastname = str(row[1]).strip()
    course = str(row[2]).strip()
    username = str(row[3]).strip()
    email = str(row[4]).strip().lower()
    gecos = str(firstname) + ' ' + str(lastname) + ',' + str(email) + ',' + str(course)
    cmd = 'ipa stageuser-add %s --homedir=/home/students --random --gidnumber=1007 --shell=/bin/bash ' \
          '--first="%s" --last="%s" --gecos="%s"' % (username, firstname, lastname, gecos)
    print 'Adding user "' + username + '" with full name "' + str(firstname) + ' ' + str(lastname) + '"'
    output = subprocess.check_output(cmd.decode('utf-8').encode('utf-8'), shell=True)
    generatedpw = get_password(output)

    body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: http://tihlde.org/lover/brukerreglement.htm \n\nHer har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + username + ".tihlde.org og masse annet snacks. For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\nDu kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\nBrukernavn: " + username + " \nPassord: " + generatedpw + " \n\nDu vil bli bedt om å skifte passord ved første innlogging, det kan endres senere med kommando 'passwd'. Dette passordet blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på http://tihlde.org/ . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\nMvh\ndrift@tihlde.org"
    send_email(email, body)

    body = "Hei og velkommen til Tihlde! \n\nDu har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + username + ".tihlde.org og masse annet snacks.\n\nOm du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"
    send_email(username + '@tihlde.org', body)

    # apachecursor.execute("INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) VALUES (NULL, '"+ histuser +"', '7', 'false', 'false', 'false', '');")

db.close()
