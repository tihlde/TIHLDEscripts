#!/usr/bin/python
# vim: set fileencoding=UTF-8 :
import time
import ldap
import ldap.modlist as modlist
import MySQLdb
import re
import base64, getpass, hashlib, os
import string
import random
import smtplib
import pprint
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from subprocess import call


# Generates random password with digits, uppercase characters and lowercase characters
def pw_generator(size=12, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))

# Salts and encrypts the password with SSHA for use in ldap
def ldappassword(rawpass):
    salt = os.urandom(26) # edit the length as you see fit
    return '{SSHA}' + base64.b64encode(hashlib.sha1(rawpass + salt).digest() + salt)


# Connection to the database
db = MySQLdb.connect(host="localhost",
                     user="medlemsregister",
                     passwd="DQ3kd#44",
                     db="medlemsregister")

apache = MySQLdb.connect(host="localhost",
                         user="apache",
                         passwd="b4rx5qFbDbFzYrWH",
                         db="apache")
apachecursor = apache.cursor()

# Connection to ldap
username = "cn=admin,dc=tihlde,dc=org"
f = open("/home/staff/drift/passord/ldap.pw", "r") # opens the ldap-password file
password = f.next().strip() # reads the password from the file and strips whitespaces
lcon = ldap.initialize("ldaps://127.0.0.1")
lcon.simple_bind_s(username, password)
baseDN = "ou=Brukere,ou=Colargol,dc=tihlde,dc=org"
searchScope = ldap.SCOPE_SUBTREE
retrieveAttributes = None
uidNumber = 0
i = 0
# Loop for getting the highest possible uidNumber in use
while True:
    try:
        retriveAttributes = ['uidNumber']
        searchFilter = "uidNumber=*"
        ldap_result_id = lcon.search(baseDN, searchScope, searchFilter, retriveAttributes)
        result_set = []
        while 1:
            result_type, result_data = lcon.result(ldap_result_id,0)
            if (result_data == []):
                break
            elif (result_type == ldap.RES_SEARCH_ENTRY):
                result_set.append(result_data)
        while (i < len(result_set)):
            tmpuid = str(result_set[i][0][1])[16: -2].replace("'","")
            i+=1
            if (int(tmpuid) > uidNumber):
                uidNumber = int(tmpuid)
    except ldap.LDAPError, e:
        print e
        break
    break
uidNumber += 1 # adds one to the uidNumber so it starts with a number which is not in use

cur = db.cursor()
print uidNumber
sender = 'drift@tihlde.org'

# Edit this to match the year of who you want to put in LDAP
year = "2015"

f = open('maillisteopptak.txt', 'w')

cur.execute("SELECT fornavn, etternavn, linje, histbruker, epost FROM members WHERE timestamp BETWEEN '" + year +"-08-01' AND '" + year + "-10-01' AND aktivert = '1' AND eula = '1'")
# loop to add every user pulled from the database to LDAP and
# send them a mail with login information
u = 0
all = cur.fetchall()
for row in all:
    u+=1
    try:
        first_name = row[0]
        # æøå is not pulled out correctly so need to sub them with regex
        first_name = re.sub(r'\xc3,', 'ø', first_name)
        first_name = re.sub(r'\xc3\x98', 'Ø', first_name)
        first_name = re.sub(r'\xc3\xa6', 'æ', first_name)
        first_name = re.sub(r'\xc3\xa5', 'å', first_name)
        first_name = re.sub(r'\xc3\x85', 'Å', first_name)
        #       first_name = re.sub(r'', 'Æ', first_name)
        last_name = row[1]
        last_name = re.sub(r'\xc3,', 'ø', last_name)
        last_name = re.sub(r'\xc3\x98', 'Ø', last_name)
        last_name = re.sub(r'\xc3\xa6', 'æ', last_name)
        last_name = re.sub(r'\xc3\xa5', 'å', last_name)
        last_name = re.sub(r'\xc3\x85', 'Å', last_name)
        linje = row[2]
        histuser = row[3].lower()
        epost = row[4].lower()
        shadow = int(time.time() / 3600 / 24)
        expire = shadow + 365*3
        rawpw = pw_generator()
        ldappw = ldappassword(rawpw)
        dn = "uid=" + histuser + ",ou=Brukere,ou=Colargol,dc=tihlde,dc=org"
        attrs = {}
        attrs['objectclass'] = ['top', 'person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount', 'shadowAccount']
        attrs['cn'] = first_name +" " + last_name
        attrs['givenName'] = first_name
        attrs['sn'] = last_name
        attrs['mail'] = histuser + "@tihlde.org", epost
        attrs['uidNumber'] = str(uidNumber)
        attrs['gidNumber'] = '1007'
        attrs['homeDirectory'] = '/home/students/' + histuser
        attrs['loginshell'] = '/bin/bash'
        # gecos doesn't support æøå so we sub them to other things
        first_name = re.sub('ø', 'oe', first_name)
        first_name = re.sub('å', 'aa', first_name)
        first_name = re.sub('Æ', 'AE', first_name)
        first_name = re.sub('Ø', 'OE', first_name)
        first_name = re.sub('Å', 'AA', first_name)
        last_name = re.sub('æ','ae', last_name)
        last_name = re.sub('ø', 'oe', last_name)
        last_name = re.sub('å', 'aa', last_name)
        last_name = re.sub('Æ', 'AE', last_name)
        last_name = re.sub('Ø', 'OE', last_name)
        last_name = re.sub('Å', 'AA', last_name)
        attrs['gecos'] = first_name + " " + last_name + " | " + linje
        attrs['shadowLastChange'] = str(shadow)
        attrs['shadowMax'] = '365'
        attrs['shadowWarning'] = '7'
        attrs['shadowExpire'] =  str(expire)
        attrs['userPassword'] = ldappw
        # this actually adds the user with all the above information and then
        # adds +1 to uidNumber for the next entry
        #        pprint.pprint(modlist.addModlist(attrs))
        ldif = modlist.addModlist(attrs)
        lcon.add_s(dn,ldif)
        uidNumber += 1
        # adds the user to apache
        apachecursor.execute("INSERT INTO `apache`.`brukere` (`id`, `brukernavn`, `gruppe`, `expired`, `deaktivert`, `webdav`, `kommentar`) VALUES (NULL, '"+ histuser +"', '7', 'false', 'false', 'false', '');")
        apache.commit()
        # logs user in to create folders (to avoid mailspam)
        call(["sudo", "su", histuser, "-c", "exit"])
        # adds users mail to textfile
        f.write(histuser + "@tihlde.org\n")
        # mail being sent with the username and password
        reciever = histuser + "@student.hist.no"
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = reciever
        msg['Subject'] = "Brukerkonto på Colargol"
        body = "Brukeren din på TIHLDE-serveren Colargol har blitt opprettet. Dette fordi du signerte på brukerreglementet ved innmeldingsfesten. Reglementet er også beskrevet her: http://tihlde.org/lover/brukerreglement.htm \n\nHer har du nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + histuser + ".tihlde.org og masse annet snacks. For å se alt vi tilbyr kan du sjekke https://tihlde.org/tjenester/. \n\nDu kan logge inn med SSH (Last ned putty om du bruker windows) på hostnavn: tihlde.org\nBrukernavn: "+histuser+" \nPassord: "+rawpw +" \n\nLogg inn for å bytt passord med kommando 'passwd'. Dette passord blir syncet med andre tjenster vi tilbyr i TIHLDE. Teknisk hjelp finnes på http://tihlde.org . Andre tekniske henvendelser kan sendes på mail til support@tihlde.org\n\nMvh\ndrift@tihlde.org"
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, reciever, text)
            print "Successfully sent email"
        except smtplib.SMTPException:
            print "Error: unable to send email"
        msg2 = MIMEMultipart()
        msg2['From'] = sender
        msg2['To'] = epost
        msg2['Subject'] = "Velkommen til Tihlde"
        body2 = "Hei og velkommen til Tihlde! \n\nDu har nå fått tildelt en shellkonto med 10GB lagringsplass, TIHLDE-epost, samt webhotell for adressen din http://" + histuser + ".tihlde.org og masse annet snacks.\n\nOm du skulle få noen problemer med de digitale tjenestene som Tihlde tilbyr til sine medlemmer så er det bare å ta kontakt på support@tihlde.org\n\nMvh\ndrift@tihlde.org"
        msg2.attach(MIMEText(body2, 'plain'))
        text2 = msg2.as_string()
        reciever2 = histuser + "@tihlde.org"
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, reciever2, text2)
            print "Successfully sent email"
        except smtplib.SMTPException:
            print "Error: unable to send email"
    except ldap.LDAPError, e:
        print e
f.close()

call(["sudo", "python", "/var/lib/mailman/bin/add_members", "-r", "maillisteopptak.txt", "-w", "n", "colusers"])
print "Lagt inn ", u, " brukere"
print "Success"
lcon.unbind_s()
apache.close()
db.close()