#!/bin/bash

#echo -n "Container path: "; read path
#echo -n "Container name: "; read name
#echo -n "Fedora version: "; read version
#echo -n "IP address: "; read ip

path=/lxc
name=ubuntu
version=karmic
arch=amd64
ip=192.168.1.42
netmask=255.255.255.0
gateway=192.168.1.1
broadcast=192.168.1.255
dns=192.168.1.1
passwd=root

# set needed variables
vmpath=$path/$name
rootfs=$vmpath/rootfs.$name
fstab=$vmpath/fstab.$name
config=$vmpath/config.$name

# create folders
mkdir -p $rootfs
##cd $vmpath

# download the minimal OS
echo "====== download os ========"
#rm -rf $rootfs
#cp -r $rootfs.bak $rootfs
debootstrap --variant=minbase --arch $arch $version $rootfs

# configure the container devices
echo "======= lxc-config.sh ====="
./lxc-config.sh $rootfs

echo "======= chroot ====="
# chroot into the container
cp container-prepare.sh $rootfs/usr/local/bin/
chroot $rootfs /bin/bash -c "container-prepare.sh $passwd"

echo "======= generate config file ====="
# generate config file
cat << EOF > $config
lxc.utsname = $name
lxc.tty = 4
lxc.network.type = veth
lxc.network.flags = up
lxc.network.link = br0
lxc.network.name = eth0
lxc.network.mtu = 1500
lxc.network.ipv4 = $ip/24
lxc.rootfs = $rootfs
lxc.cgroup.devices.deny = a
# /dev/null and zero
lxc.cgroup.devices.allow = c 1:3 rwm
lxc.cgroup.devices.allow = c 1:5 rwm
# consoles
lxc.cgroup.devices.allow = c 5:1 rwm
lxc.cgroup.devices.allow = c 5:0 rwm
lxc.cgroup.devices.allow = c 4:0 rwm
lxc.cgroup.devices.allow = c 4:1 rwm
# /dev/{,u}random
lxc.cgroup.devices.allow = c 1:9 rwm
lxc.cgroup.devices.allow = c 1:8 rwm
# /dev/pts/* - pts namespaces are "coming soon"
lxc.cgroup.devices.allow = c 136:* rwm
lxc.cgroup.devices.allow = c 5:2 rwm
# rtc
lxc.cgroup.devices.allow = c 254:0 rwm
EOF

echo << EOF > $rootfs/etc/network/interfaces
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
address $ip
netmask $netmask
broadcast $broadcast
gateway $gateway
EOF

rm $rootfs/etc/init/tty{5,6}.conf

mkdir -p $rootfs/var/run/network
touch $rootfs/var/run/network/ifstate

# add upstart script
echo << EOF > $rootfs/etc/init/lxc.conf
# LXC . Fix init sequence to have LXC working with upstart

# description .Fix LXC container - Karmic.

start on startup

task
pre-start script
mount -t proc proc /proc
mount -t devpts devpts /dev/pts
mount -t sysfs sys /sys
mount -t tmpfs varrun /var/run
mount -t tmpfs varlock /var/lock
mkdir -p /var/run/network
touch /var/run/utmp
chmod 664 /var/run/utmp
chown root.utmp /var/run/utmp
if [ '$(' 'find /etc/network/ -name upstart -type f)' ]; then
chmod -x /etc/network/*/upstart || true
fi
end script

script
start networking
initctl emit filesystem --no-wait
initctl emit local-filesystems --no-wait
initctl emit virtual-filesystems --no-wait
init 2
end script
EOF
