# coding: utf-8
# import tihldelib.user_email as maillib
import tihldelib.user_ipa as ipalib


def check_password_expiry(all_users):
    pass


if __name__ == '__main__':
    api = ipalib.get_ipa_api()
    check_password_expiry(api.user_find())

# password expire
#       send mail om det er 0, 7 eller 14 dager til
