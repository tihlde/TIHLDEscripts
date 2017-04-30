# coding: utf-8
import sys

import tihldelib.user_linux as userlinux
import tihldelib.user_ipa as useripa

__author__ = 'Harald Floor Wilhelmsen'


# rootsjekk
# sjekk om bruker eksisterer
# ligger brukeren i driftsgruppen
# drep alle prosesser tilhoerende brukeren. killall --user <brukernavn> --signal 15/9 (se python os-modul)
#    15 foerst. Delay paa 1 sekund. Saa 9.
# endre hjemmemappe i IPA
# flytt hjemmemappa til /home/xdrift/
# endre gruppetilhoerlighet paa alle filer i hjemmemappa med gruppe 'drift' og mappa selv
# unsubscribe fra drift@tihlde.org
# legg til brukeren til i xdrift-alias
# option paa om de skal ut av aktive@tihlde.org mailingliste
# oppdater mysql-db med ny gruppe
# update vhosts

def user_add_to_group(username, groupid):
    pass


def change_homedir_ipa(username, new_home):
    pass


def move_homedir(source, dest):
    pass


def change_group_owner(basedir, new_group_id):
    pass


def unsubscribe(username, mailinglist_name):
    pass


def user_add_to_alias(username, alias_name):
    pass


def main():
    # rootsjekk
    if not userlinux.is_root():
        print('Must be run as root. Re-run with \'sudo !!\'. Exiting...')
        return

    username = sys.argv[0]

    # sjekk om bruker eksisterer
    if not userlinux.user_exists(username):
        print('User', username, 'does not exist. Exiting...')
        return

    # ligger brukeren i driftsgruppen

    # drep alle prosesser tilhoerende brukeren. killall --user <brukernavn> --signal 15/9 (se python os-modul)
    #    15 foerst. Delay paa 1 sekund. Saa 9.
    userlinux.kill_user_processes(username)

    # endre hjemmemappe i IPA
    # flytt hjemmemappa til /home/xdrift/
    useripa.set_homedirectory(username, '/home/xdrift/{}'.format(username))

    # endre gruppetilhoerlighet paa alle filer i hjemmemappa med gruppe 'drift' og mappa selv
    # unsubscribe fra drift@tihlde.org
    # legg til brukeren til i xdrift-alias
    # option paa om de skal ut av aktive@tihlde.org mailingliste
    # oppdater mysql-db med ny gruppe
    # update vhosts


main()
