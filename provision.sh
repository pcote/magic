#!/bin/bash

function setup_web_server(){
     sudo apt-get update
     sudo apt-get install -y nginx
     sudo mkdir /var/log/magicws
     sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.old
     sudo cp /var/webapps/magicws/nginx.conf /etc/nginx/nginx.conf
     sudo apt-get install -y build-essential
     sudo apt-get install -y python3-dev
     sudo apt-get install -y libssl-dev
     sudo apt-get install -y openssl
 }

 function setup_python(){
     sudo apt-get install -y python3-pip
     sudo pip3 install -r /var/webapps/magicws/requirements.txt
 }

 function setup_security(){
     sudo apt-get install -y fail2ban
     sudo cp /var/webapps/magicws/jail.local /etc/fail2ban/jail.local
     # note: for now, ufw will need to be enabled manually.
     sudo ufw allow 80
     sudo ufw allow 3306
     sudo ufw allow 22
 }

 function setup_git(){
    sudo apt-get install -y git
 }

 function setup_database(){
     sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password temporary_password'
     sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password temporary_password'
     sudo apt-get install -y mysql-server
     mysql --user=root --password=temporary_password < /var/webapps/magicws/db_setup.sql
 }

function start_web_service(){
   cd /var/webapps/magicws
   sudo service nginx restart
   uwsgi --http-socket 127.0.0.1:9000 --module service:app --wsgi-file service.py  --logto ./uwsgilog.log &
}

setup_web_server
setup_python
setup_security
setup_git
setup_database
start_web_service
