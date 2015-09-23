Read Me
=========
The contents of this setup folder can be used to set up most of what is needed in a target server.
This can be done by simply running provision.sh as root.
However, provision.sh doesn't do everything.

Steps that still need manual intervention.

Before Running Provision.sh
============================
1.) Changing the root password BEFORE running provision.sh.  This password will show up three times in the setup_database function.
2.) Copy the setup folder to the root of the server you want to provision to.

Important Manual Security Steps After Running Provision.sh
===========================================================
1.)  Run "ufw enable" to enable the firewall.
2.)  Use the MySQL admin tool of your choice to connect to the MySQL server.  You'll want to create a SELECT only account and password for this user.
3.)  Once you've created this new database user, update the user and password in the /etc/magicws/ directory.
4.)  Restart the Magic WS service: "service magicws restart"
