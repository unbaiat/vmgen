#!/bin/bash

passwd=$1
echo "passwd: $passwd"
touch /etc/fstab

# mount proc sys and /dev/pts
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devpts none /dev/pts

# Update - imports the gpg key
yum -y update

# Install additional applications
yum -y reinstall glibc-common
yum -y install openssh-clients nano vim
#yum install httpd php-mysql mysql-server nano openssh-clients vim

# Generate a few needed files / directories :
ln -sf /proc/mounts /etc/mtab
# TODO: remove
#touch /lxc/rootfs.fedora/var/run/syslogd.pid
#mkdir -p /lxc/rootfs.fedora/var/run/{httpd,mysqld}
#touch /lxc/rootfs.fedora/var/run/mysqld/mysqld.pid
#mkdir -p /lxc/rootfs.fedora/var/lock/subsys
#touch /lxc/rootfs.fedora/var/lock/subsys/{atd,ip6tables,iptables,local,network,rsyslogd,sshd}

# unmount proc sys and /dev/pts
umount /dev/pts
umount /proc
umount /sys

# Set a root password
echo "root:$passwd" | chpasswd
