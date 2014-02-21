# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import readline

# send_mail
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.header import Header
from email import Charset
from email.generator import Generator
from cStringIO import StringIO
import smtplib
import re


def read_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


# Changes unicode chars to actual characters
def norify(name):
    name = re.sub(r'\xc3,', 'ø', name)
    name = re.sub(r'\xc3\x98', 'Ø', name)
    name = re.sub(r'\xc3\xa6', 'æ', name)
    name = re.sub(r'\xc3\xa5', 'å', name)
    name = re.sub(r'\xc3\x85', 'Å', name)
    return name


# Changes æøå to non-special characters
def denorify(name):
    name = re.sub('ø', 'oe', name)
    name = re.sub('å', 'aa', name)
    name = re.sub('Æ', 'AE', name)
    name = re.sub('Ø', 'OE', name)
    name = re.sub('Å', 'AA', name)
    return name


# Send mail
def send_mail(sender, recipient, subject, body):
    # Default encoding mode set to Quoted Printable. Acts globally!
    Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')

    msg = MIMEMultipart()
    msg['Subject'] = "%s" % Header(subject, 'utf-8')
    # Only descriptive part of recipient and sender shall be encoded,
    # not the email address
    msg['From'] = "\"%s\" <%s>" % (Header(sender[0], 'utf-8'), sender[1])
    msg['To'] = "\"%s\" <%s>" % (Header(recipient[0], 'utf-8'), recipient[1])

    msg.attach(MIMEText(body, 'plain', 'UTF-8'))

    str_io = StringIO()
    g = Generator(str_io, False)
    g.flatten(msg)

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail('', recipient[1], str_io.getvalue())
    except smtplib.SMTPException, e:
        print e
