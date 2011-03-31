#!/bin/bash
#Script for creating openvz containers

create()
{
	vzctl create $cid --ostemplate $vztmp 1> /dev/null 2> vzgen.log
	
	if [ $? -ne 0 ]
	then
		echo "Invalid parameters: the container will not be created"
		echo "Please consult the log vzgen.log for more details"
		exit 1
	fi
}

create_param_console()
{
	read -p "Please enter container id (example 101): " cid ;
	read -p "Please enter openvz template (example centos-5.2-default): " vztmp;
	echo "Creating container ..."
	#create $cid $vztmp
	#echo "The container has been succesfully created"
	#echo "Please be patient while the script creates the virtual server"
}

create_param_file()
{
	# TODO: read creation parameters (cid, ostemplate) from file
	type=`head -n 1 $1`
	if [ "$type" != "[openvz]" ]
	then
		echo "Wrong configuration file"
		exit 2
	fi
	cid=`cat $1 | grep 'id=' | cut -d '=' -f 2`
	vztmp=`cat $1 | grep 'template=' | cut -d '=' -f 2`
	echo "read creation parameters from file"
}

cfg_param_console()
{
	echo "Please enter configuration parameters:"
	#read -p "Do you wish the container to start on boot [default no]? [yes/no]: " onboot ;
	read -p "Enter hostname: " vzhst ;
	read -p "Enter ip address: " ip ;
	read -p "Enter first resolver [Press Enter for none]: " ns1 ;
	if [ -n "$ns1" ]
	then
		read -p "Enter seccond resolver [Press Enter for none]: " ns2 ;
		if [ -n "$ns2" ]
		then
			read -p "Enter third resolver [Press Enter for none]: " ns3 ;
		fi
	fi
	echo -n "Enter virtual root password: "
	stty -echo
	read password
	stty echo
	echo ""
	read -p "Enter disk space to be used example 10G : " hdd ;
}

cfg_param_file()
{
	# TODO: read config parameters from file
	echo "read config parameters from file"
	ip=`cat $1 | grep 'ip=' | cut -d '=' -f 2`
	ns1=`cat $1 | grep 'ns1=' | cut -d '=' -f 2`
	ns1=`cat $1 | grep 'ns2=' | cut -d '=' -f 2`
	ns1=`cat $1 | grep 'ns3=' | cut -d '=' -f 2`
	rootpass=`cat $1 | grep 'rootpass=' | cut -d '=' -f 2`
	vzhst=`cat $1 | grep 'hostname=' | cut -d '=' -f 2`
	hdd=`cat $1 | grep 'hdd=' | cut -d '=' -f 2`
	#onboot=`cat $1 | grep 'onboot=' | cut -d '=' -f 2`
}

config()
{
	vzctl set ${cid} --ipadd ${ip} --save 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --nameserver ${ns1} --save 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --nameserver ${ns2} --save 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --nameserver ${ns3} --save 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --userpasswd root:${rootpass} 1> /dev/null 2> vzgen.log
	#vzctl set ${cid} --onboot ${onboot} --save 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --diskspace ${hdd}:${hdd} 1> /dev/null 2> vzgen.log
	vzctl set ${cid} --hostname ${vzhst} --save 1> /dev/null 2> vzgen.log
	vzctl start ${cid} 1> /dev/null 2> vzgen.log
	vzlist
}

usage()
{
	cat <<EOF
$1 -h|--help -f|--file=<path>
EOF
	return 0
}

options=$(getopt -o hf:n -l help,file:,name -- "$@")
if [ $? -ne 0 ]; then
    usage $(basename $0)
    exit 1
fi
eval set -- "$options"

while true
do
    case "$1" in
	-h|--help)      usage $0 && exit 0;;
	-f|--file)      create_param_file $2; create; cfg_param_file $2; config; break;;
	--)             create_param_console; create; cfg_param_console; config; break ;;
        *)              break ;;
    esac
done
