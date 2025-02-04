#!/bin/bash

function setup_web_server(){
     sudo apt-get update
     sudo apt-get install -y nginx
     sudo mkdir /var/log/magicws
     sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.old
     sudo cp /setup/nginx.conf /etc/nginx/nginx.conf
     sudo apt-get install -y build-essential
     sudo apt-get install -y python3-dev
     sudo apt-get install -y libssl-dev
     sudo apt-get install -y openssl
 }

 function setup_python(){
     sudo apt-get install -y python3-pip
     sudo pip3 install -r /setup/requirements.txt
 }

 function setup_security(){
     sudo apt-get install -y fail2ban
     sudo cp /setup/jail.local /etc/fail2ban/jail.local
     # note: for now, ufw will need to be enabled manually.
     sudo ufw allow 80
     sudo ufw allow 22
     sudo ufw --force enable
 }

 function setup_git(){
    sudo apt-get install -y git
 }

 function setup_database(){
     sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password temporary_password'
     sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password temporary_password'
     sudo apt-get install -y mysql-server
     mysql --user=root --password=temporary_password < /setup/db_setup.sql
 }

function start_web_service(){
   sudo cp /setup/magicws.conf /etc/init/magicws.conf

   sudo mkdir /etc/magicws
   sudo cp /setup/creds.ini /etc/magicws/

   sudo mkdir /var/webapps/
   sudo mkdir /var/webapps/magicws
   sudo cp /setup/service.py /var/webapps/magicws/service.py
   sudo cp /setup/tabledefs.py /var/webapps/magicws/tabledefs.py

   sudo service nginx restart
   sudo service magicws restart
}

setup_web_server
setup_python
setup_security
setup_git
setup_database
start_web_service
