# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "hashicorp/precise32"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080
    config.vm.network "forwarded_port", guest: 80, host: 80
  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
  #   vb.memory = "1024"
  # end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
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
         wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
         tar -xvf Python-3.4.3.tgz
         cd Python-3.4.3/
         ./configure
         make
         make test
         sudo make install
         sudo pip3.4 install -r /vagrant/requirements.txt
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
         cd /vagrant
         python3 ./create_database.py
         cd
     }

     function start_web_service(){
	    cd /vagrant
	    sudo service nginx restart
        uwsgi --http-socket 127.0.0.1:9000 --wsgi-file ./service.py --callable app --logto /vagrant/uwsgilog.log
     }

     setup_web_server
     setup_python
     setup_security
     setup_git
     setup_database
     start_web_service
  SHELL
end
