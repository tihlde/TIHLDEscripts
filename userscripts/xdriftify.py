# coding: utf-8

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

def user_exists(username):
    pass


def kill_processes(username, signal):
    pass


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
    pass


main()
