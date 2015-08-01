#!/bin/bash
#
# Script som oppretter virtualhosts ala "bruker.tihlde.org" for samtlige
# brukere, både i apache og bind.
#
# Hvis scriptet kalles med opsjonen '--apache' vil kun
# vhostene for apache2 oppdateres. Dette brukes hovedsaklig av scriptet
# open_user.sh.
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
#

if (( $UID != 0 )); then
	echo "*!* Fatal: Must be run by root!"
	exit 1
fi

# location of ldap_valid script
LDAP_VALID="/home/staff/drift/bin/ldap_utils/ldap_valid.bash"

# final destination
APACHE_BASE="/etc/apache2/sites-available"
BIND_BASE="/etc/bind/vhosts.d"

# argument flags
GO_BIND=0
if [ "$1" == "--apache" ]; then
	GO_BIND=-1
fi
VERBOSE=0

# make a temp direcory which we can put files in
TEMP=/tmp/update_vhosts_$$
mkdir $TEMP
if (( $? != 0 )); then
	echo "*!* Fatal: Unable to create $TEMP"
	exit 1
fi

PROCESSED="$TEMP/processed"
touch $PROCESSED

# loop through /home/*
for GROUP in staff xdrift students guests org ansatt hs xhs forever
do
	# remember all the directories in /home/*/*
	ls /home/$GROUP > $TEMP/temp

	# temp storage
	BIND_FILE="$TEMP/tihlde.org-$GROUP"
	APACHE_FILE="$TEMP/brukere.tihlde.org-$GROUP"

	# loop through /home/*/*
	while read USER
	do
		# true if user exists and has *not* expired
		if (( $($LDAP_VALID $USER) == 0 )); then

			# bind will crash with duplicates
			if grep -q "_${USER}_" $PROCESSED; then
				echo "** Warning: '$USER' has been processed more than once. Duplicate user?"
				continue
			else
				echo "_${USER}_" >> $PROCESSED
			fi
			# public_html has to exist
			if [ -d "/home/$GROUP/$USER/public_html" ]; then

## dump these mofo's in the temp file
echo -e "<VirtualHost 158.38.48.10:80>
	ServerName $USER.tihlde.org
	ServerAdmin $USER@tihlde.org
	DocumentRoot /home/$GROUP/$USER/public_html
	ScriptAlias /cgi-bin/ /home/$GROUP/$USER/public_html/cgi-bin/
	ErrorLog /var/log/apache2/error-vhosts-$GROUP.log
	TransferLog /var/log/apache2/transfer-vhosts-$GROUP.log
	<Directory /home/$GROUP/$USER/public_html>
		AllowOverride All
	</Directory>
</VirtualHost>
<VirtualHost 158.38.48.10:443>
	ServerName $USER.tihlde.org
	ServerAdmin $USER@tihlde.org
	DocumentRoot /home/$GROUP/$USER/public_html
	ScriptAlias /cgi-bin/ /home/$GROUP/$USER/public_html/cgi-bin/
	ErrorLog /var/log/apache2/error-vhosts-$GROUP.log
	TransferLog /var/log/apache2/transfer-vhosts-$GROUP.log

	SSLEngine on
	SSLCertificateFile /etc/ssl/certs/tihlde.org.pem

	<Directory /home/$GROUP/$USER/public_html>
		AllowOverride All
	</Directory>

	<Directory /home/$GROUP/$USER/public_html/webdav>
		DAV On
		AuthType Digest
		AuthName \"WebDAV\"
		AuthUserFile  /home/$GROUP/$USER/.webdav-passwd
		Require valid-user
	</Directory>
</VirtualHost>\n" >> $APACHE_FILE
# we were ----------------------| here ;D
			fi

			# do bind or...?
			if (( $GO_BIND != 0 )); then
				continue
			fi
			# do bind then
			echo -e "$USER\tIN\tCNAME\tcolargol" >> $BIND_FILE

		fi

	done < "$TEMP/temp"
done


# custom vhosts

#temp
cat "/home/staff/drift/data/vhost_custom/ixan.no" >> $TEMP/brukere.tihlde.org-xdrift


# copy files to /etc
for GROUP in students guests org ansatt hs staff xhs xdrift forever
do
	if [ -f $TEMP/brukere.tihlde.org-$GROUP ]; then
		cp $TEMP/brukere.tihlde.org* $APACHE_BASE
	fi
	if (( $GO_BIND == 0 )) && [ -f $TEMP/tihlde.org-$GROUP ]; then
		cp $TEMP/tihlde.org-$GROUP $BIND_BASE
	fi
done

if [ -d $TEMP ]; then
	rm -rf $TEMP
fi

