#!/bin/bash

#echo -n "Container path: "; read path
#echo -n "Container name: "; read name
#echo -n "Fedora version: "; read version
#echo -n "IP address: "; read ip

path=/lxc
name=fedora2
version=14
ip=192.168.1.42
gateway=192.168.1.1
dns=192.168.1.1
passwd=root

# set needed variables
vmpath=$path/$name
rootfs=$vmpath/rootfs.$name
fstab=$vmpath/fstab.$name
config=$vmpath/config.$name

# create folders
#mkdir $vmpath
##cd $vmpath

# download the minimal OS
echo "====== download os ========"
#rm -rf $rootfs
#cp -r $rootfs.bak $rootfs
febootstrap "fedora-$version" $rootfs

# configure the container devices
echo "======= lxc-config.sh ====="
./lxc-config.sh $rootfs

echo "======= chroot ====="
# TODO: resolv.conf
# chroot into the container
cp container-prepare.sh $rootfs/usr/local/bin/
chroot $rootfs /bin/bash -c "container-prepare.sh $passwd"

echo "======= edit config file ====="
# edit config files
sed -i 's|\(ACTIVE_CONSOLES=/dev/tty\)\[1-6\]|\1[1-4]|g' \
	$rootfs/etc/sysconfig/init

sed -i 's|/sbin/start_udev|# &|g' $rootfs/etc/rc.sysinit

cat << EOF >> $rootfs/etc/sysconfig/network
NETWORKING=yes
HOSTNAME=$name
EOF


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
lxc.network.ipv4 = $ip
lxc.rootfs = $rootfs
lxc.mount = $fstab
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

echo "======= generate fstab ====="
#generate fstab file
cat << EOF > $fstab
none $rootfs/dev/pts devpts defaults 0 0
none $rootfs/proc proc defaults 0 0
none $rootfs/sys sysfs defaults 0 0
#none $rootfs/var/lock tmpfs defaults 0 0
#none $rootfs/var/run tmpfs defaults 0 0
#/etc/resolv.conf $rootfs/etc/resolv.conf none bind 0 0
EOF

echo "======= cleanup init scripts ====="
# cleanup the init scripts
find $rootfs/etc/init \
	-type f \
	-not -name "rc.conf" \
	-not -name "start-ttys.conf" \
	-not -name "tty.conf" \
	-print0 | xargs -0 /bin/rm

sed -i "s/^start.*/start on startup/" $rootfs/etc/init/start-ttys.conf
sed -i "s/^start.*/start on startup/" $rootfs/etc/init/rc.conf
sed -i "s|^\(exec /etc/rc.d/\).*|\1rc.$name|" $rootfs/etc/init/rc.conf

cat << EOF > $rootfs/etc/rc.d/rc.$name
#!/bin/bash
# Whatever is needed to clear out old daemon/service pids from your container
find /var/run -name '*pid' -print0 | xargs -0 /bin/rm

route add default gw $gateway
echo > /etc/resolv.conf nameserver $dns

/etc/init.d/rsyslog start &
/etc/init.d/iptables start &
/etc/init.d/sshd start &
EOF

chmod a+x $rootfs/etc/rc.d/rc.$name

find -H $rootfs/etc/init.d \
	-type f \
	-not -name "iptables" \
	-not -name "rsyslog" \
	-not -name "sshd" \
	-print0 | xargs -0 /bin/rm
