# coding: utf-8
import sys

import tihldelib.user_ipa as user_ipa
import tihldelib.user_linux as user_linux
import tihldelib.user_sql as user_sql

from tihldelib.user_linux import check_root


__author__ = 'Harald Floor Wilhelmsen'


def parse_args():
    """
    :return: A string-array containing the arguments.
    Order: [username, groupname, email, course, year, first_name, last_name]
    """
    args = sys.argv
    if len(args) == 8:
        return args[1:]
    if len(args) == 2 and args[1] == 'help':
        help_msg = 'Adds a single user to ipa and apache.\n\n' \
                   'Usage:\npython3 add_user.py <username> <group-id linux> <group-id sql> <quota in GB> ' \
                   '<external email> <course> <year> <first name> <surname>\n\n' \
                   'username: login username for the new user\n' \
                   'groupname: name of the group to add the user to' \
                   'external email: gmail of whatever email address that is NOT @tihlde.org.\n' \
                   'course: what course the user attends e. g. "ING", "BABED", "MASTER" or "BADR"\n' \
                   'year: year of admission into TIHLDE\n' \
                   'first name: the new user\'s first name in quotes. E. g. "Harald Floor"\n' \
                   'surname: the new user\'s surname'

        print(help_msg)
        sys.exit(0)
    else:
        print('Incorrect number of arguments given. For usage:\npython3 add_user.py help')
        sys.exit(0)


def main():
    check_root()
    args = parse_args()

    username = args[0]
    group_name = args[1]
    email = args[2]
    course = args[3]
#    year = args[4]
    first_name = args[5]
    surname = args[6]

    group_info = user_linux.get_group_info(group_name)
    gid_lx = group_info['gid_lx']
    gid_sql = group_info['gid_sql']
    homedir_base = group_info['homedir_base']
    quota = group_info['quota']

    api = user_ipa.get_ipa_api()
    ipa_return = user_ipa.add_user_ipa(username=username,
                                       firstname=first_name,
                                       lastname=surname,
                                       groupid=gid_lx,
                                       homedir_base=homedir_base,
                                       course=course,
                                       email=email,
                                       api=api)

    uid = ipa_return[0]
#    generated_pw = ipa_return[1]

    user_sql.add_user_apache(username=username,
                             groupid=gid_sql)

    user_linux.set_quota(uid, quota)

    # add to mailing-lists


main()
