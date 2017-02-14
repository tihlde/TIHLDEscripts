# coding: utf-8
__author__ = 'Harald Floor Wilhelmsen'

# rootsjekk
# sjekk om bruker eksisterer
# ligger brukeren allerede i gruppe hs eller drift
#    exit
# drep alle prosesser tilhoerende brukeren. killall --user <brukernavn> --signal 15/9 (se python os-modul)
#    15 foerst. Delay paa 1 sekund. Saa 9.
# endre hjemmemappe i IPA
# flytt hjemmemappa til /home/hs/
# endre gruppetilhoerlighet paa alle filer i hjemmemappa med gruppe 'students' og mappa selv
# legg til i alias hs@tihlde.org og mailingsliste
# oppdater mysql-db med ny gruppe
# fjern shadow_expire
# fjern ~kerberos principal expire
# update vhosts