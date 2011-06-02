#!/bin/bash

passwd=$1
version=$2
hostname=$3
ip=$4

echo "deb http://security.debian.org/ $version/updates main" \
	>> /etc/apt/sources.list

# mount proc sys and /dev/pts
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devpts none /dev/pts

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y apt-utils

# set locales
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
apt-get -y --force-yes install locales

apt-get install -y whiptail dialog

# Add a few applications, including openssh-server
apt-get install -y adduser iproute netbase nano openssh-blacklist openssh-blacklist-extra openssh-server sudo iputils-ping iptables vim dhcp-client

# Configure the hostname of the container and /etc/hosts
# Change "host_name" to your desired host name
# Change "192.168.0.60" to the ip address you wish to assign to the container
echo "$hostname" > /etc/hostname
echo "127.0.0.1 localhost $hostname" > /etc/hosts
#echo "$ip $hostname" >> /etc/hosts

# .Fix. mtab
rm /etc/mtab
ln -sf /proc/mounts /etc/fstab

#Set a root passwd
echo "root:$passwd" | chpasswd

# As an alternate to setting a root password, you may of course add a new user and configure sudo.

# unmount proc sys and /dev/pts
umount /dev/pts
umount /proc
umount /sys

#exit chroot
exit
