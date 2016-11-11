# coding: utf-8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
