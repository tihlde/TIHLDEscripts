# coding: utf-8
__author__ = 'Harald Floor Wilhelmsen'

# rootsjekk
# sjekk om bruker eksisterer
# ligger brukeren i hsgruppen
# drep alle prosesser tilhoerende brukeren. killall --user <brukernavn> --signal 15/9 (se python os-modul)
#    15 foerst. Delay paa 1 sekund. Saa 9.
# endre hjemmemappe i IPA
# flytt hjemmemappa til /home/xhs/
# endre gruppetilhoerlighet paa alle filer i hjemmemappa med gruppe 'hs' og mappa selv
# fjern fra alias hs@tihlde.org
# oppdater mysql-db med ny gruppe
# update vhosts