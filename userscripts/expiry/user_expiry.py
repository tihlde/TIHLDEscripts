# coding: utf-8
import math
import time
from time import strftime

import tihldelib.user_email as maillib
import tihldelib.user_ipa as ipalib

__author__ = 'Harald Floor Wilhelmsen'
SECONDS_PER_DAY = 86400

expired_shell = '/home/staff/drift/bin/expired_shell.bash'

mail_future_expiry_subject = 'Colargol-brukeren din går ut om {0} dager'

mail_future_expiry_body = \
    'Hei.' \
    '\n' \
    '\nColargol-brukeren din får ut om {0} dager.' \
    '\nBrukeren går ut på dato: {1}' \
    '\n' \
    '\nOm du vil beholde brukeren din blabla' \
    '\n' \
    '\nMed vennlig hilsen' \
    '\ndrift@TIHLDE'

mail_has_expired_subject = 'Colargol-brukeren har gått ut'

mail_has_expired_body = \
    'Hei.' \
    '\n' \
    '\nColargol-brukeren din har gått ut' \
    '\n' \
    '\nOm du vil beholde brukeren din må du betale osv...' \
    '\n' \
    '\nMed vennlig hilsen' \
    '\ndrift@TIHLDE'


def format_expiry_days(days_epoch):
    """
    Returns a string of format YY.mm.dd of the given days since epoch
    :param days_epoch: Days since epoch
    :return: A string of format YY.mm.dd
    """
    return strftime('%Y.%m.%d').format(days_epoch * SECONDS_PER_DAY)


def set_expired_shell_of_user(username, api):
    ipalib.set_loginshell(username, expired_shell, api=api)


def send_emails(username, external_emails, body, subject):
    maillib.send_email(
        recipient='{}@tihlde.org'.format(username),
        subject=subject,
        body=body)
    for mail in external_emails:
        maillib.send_email(
            recipient=mail,
            subject=subject,
            body=body)


def check_expire_single_user(user, api):
    expiry_field = user['shadowexpire']

    if not expiry_field:
        return

    expiry_int = int(expiry_field)
    formatted_date_of_expiry = format_expiry_days(expiry_int)

    # date of expiry - today
    days_until_expiry = expiry_int - math.floor(time.time() / SECONDS_PER_DAY)
    # sjekk shadow-expire
    # har brukeren gaatt ut: Er expired shell ikke satt, sett expired shell
    if days_until_expiry == 0:
        # user expires today. Do nothing?
        return
    elif days_until_expiry < 0:
        # user expired before today
        # check if expiry-actions have been done, if not, do them and send an email
        if user['loginshell'] != expired_shell:
            set_expired_shell_of_user(username=user['uid'], api=api)
    else:
        if [7, 14, 30].index(days_until_expiry) == -1:
            # expire er mellom(inklusiv) 1 og 30 men er ikke 7, 14, eller 30
            # do nothing?
            return
        else:
            # det er 7, 14 eller 30 dager til brukeren går ut
            # send mail om det til brukeren
            send_emails(
                username=user['uid'],
                external_emails=user['mail'],
                subject=mail_future_expiry_subject.format(days_until_expiry),
                body=mail_future_expiry_body.format(days_until_expiry, formatted_date_of_expiry))


def check_user_expiry(all_users, api):
    for user in all_users['result']['result']:
        check_expire_single_user(user, api)


if __name__ == '__main__':
    ipa_api = ipalib.get_ipa_api()
    # liste over alle brukere i IPA
    check_user_expiry(ipa_api.user_find(), ipa_api)
