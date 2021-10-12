
Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |v|
      v.memory = 4096
      v.cpus = 2
  end

  config.vm.network "public_network", use_dhcp_assigned_default_route: true#, bridge: "wlan0"

end
