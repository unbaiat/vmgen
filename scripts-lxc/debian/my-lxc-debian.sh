#!/bin/bash

# ./my-lxc-debian.sh path name version arch passwd ip gw dns
# ./my-lxc-debian.sh /lxc lxc-lenny lenny amd64 root 192.168.1.10

path=/lxc
name=lenny
version=lenny
arch=amd64
ip=192.168.1.42/24
gateway=192.168.1.1
dns=192.168.1.1
passwd=root

path=$1
name=$2
version=$3
arch=$4
passwd=$5
#ip=$6
#gateway=$6
#dns=$7

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


echo "======= chroot ====="
# chroot into the container
cp container-prepare.sh $rootfs/usr/local/bin/
chroot $rootfs /bin/bash -c "container-prepare.sh \
	$passwd $version $name $ip"

echo "======= edit config file ====="
# edit config files
sed -i "s|si::sysinit:/etc/init.d/rcS|&.$name" \
	$rootfs/etc/inittab
sed -i 's|5:23:respawn:/sbin/getty 38400 tty5|# &|g' $rootfs/etc/inittab
sed -i 's|6:23:respawn:/sbin/getty 38400 tty6|# &|g' $rootfs/etc/inittab

# configure the container devices
echo "======= lxc-config.sh ====="
./lxc-config.sh $rootfs

echo "======= generate config file ====="
# generate config file
cat << EOF > $config
lxc.utsname = $name
lxc.tty = 4
lxc.rootfs = rootfs.$name
lxc.mount = fstab.$name
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

cat eth.tmp >> $config

echo "======= generate fstab ====="
#generate fstab file
cat << EOF > $fstab
none rootfs.$name/dev/pts devpts defaults 0 0
none rootfs.$name/proc proc defaults 0 0
none rootfs.$name/sys sysfs defaults 0 0
none rootfs.$name/var/lock tmpfs defaults 0 0
none rootfs.$name/var/run tmpfs defaults 0 0
/etc/resolv.conf rootfs.$name/etc/resolv.conf none bind 0 0
EOF

echo "======= cleanup init scripts ====="
# cleanup the init scripts

cat << EOF > $rootfs/etc/init.d/rcS.$name
#!/bin/bash
# Whatever is needed to clean out old daemon/service pids from your container
find /var/run -name '*pid' -print0 | xargs -0 /bin/rm
rm -f /var/lock/subsys/*
# you could use a dhcp client here
# or you could get your system network scripts to work
# (Which I.ve ran into troubles with in containers)
# (Edit gateway address, domain, and nameserver as need be)

route add default gw $gateway
echo > /etc/resolv.conf nameserver $dns

/etc/init.d/rsyslog start &
#/etc/init.d/iptables start &
#/etc/init.d/sshd start &
EOF

chmod a+x $rootfs/etc/init.d/rcS.$name

find -H $rootfs/etc/init.d \
	-type f \
	-not -name "rsyslog" \
	-not -name "ssh" \
	-not -name "rcS.$name" \
	-not -name "sudo" \
	-not -name "rc" \
	-not -name "urandom" \
	-print0 | xargs -0 /bin/rm
