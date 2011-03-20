#!/bin/bash

passwd=$1

# mount /proc /sys and /dev/pts
mount -t devpts devpts /dev/pts
mount -t proc proc /proc
mount -t sysfs sysfs /sys

apt-get install --force-yes -y gpgv
apt-get update

# set locales
apt-get install -y language-pack-en
update-locale LANG=.en_US.UTF-8. LANGUAGE=.en_US.UTF-8. LC_ALL=.en_US.UTF-8.

# Add to the installed applications
apt-get install -y adduser apt-utils iproute netbase nano openssh-blacklist openssh-blacklist-extra openssh-server console-setup sudo ping

#Remove udev
apt-get remove --purge udev # two . - in front of .--purge.
rm -rf /etc/udev /lib/udev
apt-get autoremove

#Remove a few upstart scripts
cd /etc/init
rm mountall* upstart*

#Set a root passwd
echo "root:$passwd" | chpasswd

#unmount /proc /sys and /dev/pts
umount /dev/pts
umount /proc
umount /sys

#exit chroot
exit
