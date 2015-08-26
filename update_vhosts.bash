#!/usr/bin/env bash
#
# Script som oppretter virtualhosts ala "bruker.tihlde.org" for samtlige
# brukere..
#
# Generer filene fra scratch for ordens skyld
#
#
# HISTORY
# - Opprinnelig 'oppdater-vhosts.pl' skrevet av Håvard Tautra Knutsen (2004)
# - Støtte --apache opsjonen og utgåtte brukere av Magne Rodem (2004)
# - Oppdatert til apache2 og mod_jk av Håvard Barkhall (2006)
# - Oppdatert bugs/regex Roy Sindre Norangshol (2007)
# - Oversatt til bash + støtte for LDAP + støtte for WebDAV av joachimn (2009)
# - Fullstendig rewrite. Henter nå data fra MySQL. - Dennis Eriksen (dennisse), 2015-08-01
#
# please clean me

# Starter med litt standard gull. «unofficial bash strict mode»
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'


# Så kan vi sette noen variabler
# camelCase ftw?

mysqlHost='localhost'
mysqlUser='apache'
mysqlPass=$(cat /home/staff/drift/passord/db-apache)
mysqlDB='apache'

mysqlQuery="SELECT brukere.id, brukere.brukernavn AS 'bruker', grupper.navn AS 'gruppe', brukere.webdav AS 'ifwebdav' FROM brukere INNER JOIN grupper ON (brukere.gruppe = grupper.id) WHERE brukere.expired = 'false' AND brukere.deaktivert = 'false' ORDER BY 'brukere.gruppe' DESC;"

apacheFolder='/etc/apache2/'
vhostAFolder='sites-available/brukere.tihlde.org'
vhostEFolder='sites-enabled/brukere.tihlde.org'

# En tempdir er fint å ha.
tmpDir=$(mktemp -d /tmp/update_vhosts.XXXXXXXXX) || { echo "Failed to create temp dir"; exit 1; }

# Det er viktig å huske å fjerne temp-ting.
function cleanUp {
  if [ -d $tmpDir ]; then rm -rf $tmpDir; fi
}


########################


#mysql -u$mysqlUser -p$mysqlPass $mysqlDB -e "$mysqlQuery" 
mysql -u$mysqlUser -p$mysqlPass $mysqlDB -e "$mysqlQuery" | while read id bruker gruppe ifwebdav; do

  # På første eller siste tur settes variablene til variabelnavnet.. Den droppper vi
  if [[ $bruker == 'bruker' ]] && [[ $gruppe == 'gruppe' ]]; then continue; fi

  if [ $ifwebdav == 'true' ]; then
    webdav="        Alias /webdav /home/${gruppe}/${bruker}/webdav/public/
        <Directory /home/${gruppe}/${bruker}/webdav/public/>
                Options -FollowSymLinks
                AllowOverride None
        </Directory>"
  else webdav=''
  fi

# må fikses.
  serveralias=''
#  mysql -u$mysqlUser -p$mysqlPass $mysqlDB -e "SELECT alias.alias FROM alias WHERE alias.bruker = $id" | while read alias; do
#    if [[ "$alias" != "alias" ]]; then
#      serveralias=${serveralias}"        ServerAlias ${alias}\n"
#    fi
#  done


  cat > ${tmpDir}/${bruker}.tihlde.org.conf <<-EOM
<VirtualHost *:80>
        ServerName ${bruker}.tihlde.org
        ServerAdmin ${bruker}@tihlde.org

        $serveralias

        AssignUserID ${bruker} ${gruppe}
        MaxClientsVHost 10

        DocumentRoot /home/${gruppe}/${bruker}/public_html/
        ScriptAlias /cgi-bin/ /home/${gruppe}/${bruker}/public_html/cgi-bin/

        ErrorLog /var/log/apache2/error-brukere.tihlde.org.log
        CustomLog /var/log/apache2/access-brukere.tihlde.org.log combined

        <Directory />
                Options Indexes
        </Directory>

        ${webdav}
</VirtualHost>

<VirtualHost *:443>
        ServerName ${bruker}.tihlde.org
        ServerAdmin ${bruker}@tihlde.org

        $serveralias

        AssignUserID ${bruker} ${gruppe}
        MaxClientsVHost 10

        DocumentRoot /home/${gruppe}/${bruker}/public_html/
        ScriptAlias /cgi-bin/ /home/${gruppe}/${bruker}/public_html/cgi-bin/

        ErrorLog /var/log/apache2/error-brukere.tihlde.org.log
        CustomLog /var/log/apache2/access-brukere.tihlde.org.log combined

        SSLEngine on

        <Directory />
                Options Indexes
        </Directory>

	${webdav}
</VirtualHost>

EOM
done

echo "Made all files"


# Hvis scriptet gir veldig få choster er noe galt
if [ $(ls -la $tmpDir | wc -l) -lt 10 ]; then
  echo "Scriptet ga færre enn ti vhosts.. Noe er nok galt." >&2
  exit 1
fi


# Hvis de er endret, så bytter vi de gamle ut med de nye.
if [ -n "$(diff <(find ${apacheFolder}${vhostAFolder} -type f -exec md5sum {} \; | cut -f 1 -d ' ' | sort) <(find $tmpDir -type f -exec md5sum {} \; | cut -f 1 -d ' ' | sort))" ]; then
  echo "Fant endringer! Bytter ut gammel apache-conf med ny."
  logger "update_vhosts.bash: Fant endringer! Bytter ut gammel apache-conf med ny."
  rm -rf ${apacheFolder}${vhostAFolder}
  mv $tmpDir ${apacheFolder}${vhostAFolder}
else
   echo "Fant ingen endringer. Avslutter (og rydder)."
   logger "update_vhosts.bash: Fant ingen endringer. Avslutter (og rydder)."
fi

#######################

trap cleanUp EXIT
