# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 80

  # config.vm.synced_folder "../data", "/vagrant_data"

  config.vm.provision "shell", inline: <<-SHELL
     function setup_web_server(){
         sudo apt-get update
         sudo apt-get install -y nginx
         sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.old
         sudo cp /vagrant/nginx.conf /etc/nginx/nginx.conf
         sudo apt-get install -y build-essential
         sudo apt-get install -y python3-dev
         sudo apt-get install -y libssl-dev
         sudo apt-get install -y openssl
     }

     function setup_python(){
         sudo apt-get install -y python3-pip
         sudo pip3 install -r /vagrant/requirements.txt
     }

     function setup_security(){
         sudo apt-get install -y fail2ban
         sudo cp /vagrant/jail.local /etc/fail2ban/jail.local
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
         mysql --user=root --password=temporary_password < /vagrant/db_setup.sql
     }

     function start_web_service(){
	    cd /vagrant
	    sudo service nginx restart
        uwsgi --http-socket 127.0.0.1:9000 --module service:app --logto ./uwsgilog.log
     }

     setup_web_server
     setup_python
     setup_security
     setup_git
     setup_database
     start_web_service
  SHELL
end
