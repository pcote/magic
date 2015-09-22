# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 80, host: 80

    #config.vm.synced_folder ".", "/var/webapps/magicws"
    #config.vm.synced_folder "./etc", "/etc/magicws"
    config.vm.synced_folder "./setup", "/setup"

    config.vm.provision "shell", path: "provision.sh"
end

