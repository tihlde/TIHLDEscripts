# coding: utf-8
# import tihldelib.user_email as maillib
import tihldelib.user_ipa as ipalib
from expiry import expiry_all


def check_password_expiry(user):
    pass


def check_password_expiry_all():
    api = ipalib.get_ipa_api()
    for user in expiry_all.get_all_users(api):
        check_password_expiry(user)


if __name__ == '__main__':
    check_password_expiry_all()

# password expire
#       send mail om det er 0, 7 eller 14 dager til
