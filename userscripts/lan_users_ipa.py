# coding: utf-8
import sys
import time

import os

import tihldelib.user_ipa as ipalib

__author__ = 'Harald Floor Wilhelmsen'


def get_useramount():
    formatstring = 'Format: python lan_users.py useramount user_start_id'

    # Checking if there are sufficient arguments, if not exit
    if len(sys.argv) != 3:
        sys.exit('Invaild number of arguments. ' + formatstring)

    user_amount = sys.argv[1].strip()
    user_start_id = sys.argv[2].strip()

    if not user_amount.isdigit() or not user_start_id.isdigit():
        sys.exit('Wrong number-format. ' + formatstring)
    return int(user_amount), int(user_start_id)


def create_lan_users():
    user_amount, start_id = get_useramount()

    response = str(input(str(user_amount) + ' users to add. Continue? [y/N]'))
    if response.replace('\n', '').strip() != 'y':
        return 'User called exit before adding users. No changes pushed to ipa.'

    api = ipalib.get_ipa_api()
    username_format = 'lan-{}'

    credentials_file_path = '/root/lan_users{}.txt'.format(time.time())

    with open(credentials_file_path, 'a') as credentials_file:
        for i in range(start_id, start_id + user_amount):
            username = username_format.format(i)
            user_info = ipalib.add_user_ipa(username=username, firstname='Lan', lastname='Lanesen', groupid=1002,
                                         homedir_base='/home/lan/', api=api)
            credentials_file.write('Brukernavn: {0}\nPassord: {1}\n\n'.format(username, user_info[1]))

    return 'created {0} users. Credentials can be found in {1}'.format(user_amount, credentials_file_path)


def main():
    euid = os.geteuid()
    if euid != 0:
        print('Needs to be run as root. Re-run with sudo')
        return
    msg = create_lan_users()
    if msg:
        print(msg)


if __name__ == '__main__':
    main()
