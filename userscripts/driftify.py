# coding: utf-8
__author__ = 'Joel Kaaberg'

import os
import argparse

from tihldelib.user_linux import check_root, kill_user_processes, move_home_dir, set_permissions, get_group_info
from tihldelib.user_ipa import user_exists, user_get_group, set_homedirectory
from tihldelib.user_general import color


# legg til i mailinglister drift@tihlde.org og aktive@tihlde.org
# oppdater mysql-db med ny gruppe
# fjern shadow_expire
# fjern ~kerberos principal expire
# update vhostss


def main(args):
    username = args.username
    if user_exists(username):
        if 'drift' not in user_get_group(username):
            info = get_group_info('drift')
            org_home_path = os.path.join('/home/students', username)
            new_home_path = os.path.join('/home/staff', username)

            if kill_user_processes(username):
                print('{0} Successfully killed all processes for {1}'.format(color('OK', 'green'),
                                                                             username))
            else:
                print('{0} Failed to kill all processes for {1}'.format(color('FAIL', 'red'),
                                                                        username))

            if set_homedirectory(username, new_home_path):
                print('{0} Successfully changed home path in FreeIPA to {1} for {2}'.format(color('OK', 'green'),
                                                                                            new_home_path,
                                                                                            username))
            else:
                print('{0} Failed to change home path in FreeIPA to {1} for {2}'.format(color('FAIL', 'red'),
                                                                                        new_home_path,
                                                                                        username))

            if move_home_dir(org_home_path, new_home_path):
                print('{0} Successfully moved home folder to {1} for {2}'.format(color('OK', 'green'),
                                                                                 new_home_path,
                                                                                 username))
            else:
                print('{0} Failed to move home folder to {1} for {2}'.format(color('FAIL', 'red'),
                                                                             new_home_path,
                                                                             username))

            if set_permissions(new_home_path, uid=-1, gid=info['gid_lx']):
                print('{0} Successfully changed permissions to {1} for {2}'.format(color('OK', 'green'),
                                                                                   info['gid_lx'],
                                                                                   username))
            else:
                print('{0} Failed to change permissions to {1} for {2}'.format(color('FAIL', 'red'),
                                                                               info['gid_lx'],
                                                                               username))

        else:
            print('{0} is already a member of staff.'.format(username))
    else:
        print('{0} doesnt exist.'.format(username))


if __name__ == "__main__":
    check_root()

    parse = argparse.ArgumentParser(description='Script to convert user to staff user.')
    parse.add_argument('username', type=str, help='The user to convert to staff user.')

    args = parse.parse_args()

    main(args)
