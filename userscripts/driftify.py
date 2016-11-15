# coding: utf-8
__author__ = 'Harald Floor Wilhelmsen'

import sys
import argparse

from tihldelib.user_linux import is_root, kill_user_processes
from tihldelib.user_ipa import user_exists, user_get_group



# rootsjekk OK
# sjekk om bruker eksisterer OK
# ligger brukeren allerede i gruppe drift OK
#    exit
# drep alle prosesser tilhoerende brukeren. killall --user <brukernavn> --signal [15,9] (se python os-modul)
#    15 foerst. Delay paa 1 sekund. Saa 9.
# endre hjemmemappe i IPA
# flytt hjemmemappa til /home/staff/
# endre gruppetilhoerlighet paa alle filer i hjemmemappa med gruppe 'students' og mappa selv
# legg til i mailinglister drift@tihlde.org og aktive@tihlde.org
# oppdater mysql-db med ny gruppe
# fjern shadow_expire
# fjern ~kerberos principal expire
# update vhosts


def main(args):
    username = args.username
    if user_exists(username):
        if 'drift' not in user_get_group(username):
            #kill_user_processes(username)
            print("t")
        else:
            print('{} is already a member of staff.'.format(username))
    else:
        print('{} doesnt exist.'.format(username))


if __name__ == "__main__":
    if not is_root:
        print('du er ikke root')
        sys.exit(1)

    parse = argparse.ArgumentParser(description='Script to convert user to staff user.')
    parse.add_argument('username', type=str, help='The user to convert to staff user.')

    args = parse.parse_args()

    main(args)
