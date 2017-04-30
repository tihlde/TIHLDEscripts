# coding: utf-8
import math
import time

import tihldelib.expiry as expirylib
import tihldelib.user_email as maillib
import tihldelib.user_ipa as ipalib
from tihldelib.user_email import read_email_resource

__author__ = 'Harald Floor Wilhelmsen'

expired_shell = '/home/staff/drift/bin/expired_shell.bash'


def set_expired_shell_of_user(username, api):
    ipalib.set_loginshell(username, expired_shell, api=api)


def check_expire_single_user(user, api):
    expiry_field = user['shadowexpire']

    if not expiry_field:
        return

    expiry_int = int(expiry_field)
    formatted_date_of_expiry = expirylib.epochdays_to_datetime(expiry_int)

    # date of expiry - today
    days_until_expiry = expiry_int - math.floor(time.time() / expirylib.SECONDS_PER_DAY)
    # sjekk shadow-expire
    # har brukeren gaatt ut: Er expired shell ikke satt, sett expired shell
    if days_until_expiry == 0:
        # user expires today. Do nothing?
        return
    elif days_until_expiry < 0:
        # user expired before today
        if user['loginshell'] != expired_shell:
            # check if expiry-actions have been doneif not, do them and send an email
            set_expired_shell_of_user(username=user['uid'], api=api)
            email = maillib.read_email_resource('user_has_expired.txt')
            for mail in user['mail']:
                maillib.send_email(mail, email.subject, email.body.format('stuff'))
    else:
        if days_until_expiry in [7, 14, 30]:
            # det er 7, 14 eller 30 dager til brukeren går ut
            # send mail om det til brukeren
            mail_future_expiry = read_email_resource('user_future_expiry.txt')
            maillib.send_emails(external_emails=user['mail'],
                                subject=mail_future_expiry.subject.format(days_until_expiry),
                                body=mail_future_expiry.body.format(days_until_expiry,
                                                                    formatted_date_of_expiry.strftime('%Y.%m.%d')))


def check_user_expiry_all():
    ipa_api = ipalib.get_ipa_api()
    # liste over alle brukere i IPA
    all_users = ipalib.get_all_users(ipa_api)
    for user in all_users:
        check_expire_single_user(user, ipa_api)


if __name__ == '__main__':
    check_user_expiry_all()
