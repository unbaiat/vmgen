#!/bin/bash

check_cache()
{
	pack=$1.tar.gz
	cache_path="/vz/template/cache/"

	# check if the openvz cache already contains the template
	if [ -e $cache_path$pack ]; then
		exit 0
	fi
}

get_template()
{
	pack=$1.tar.gz

	# possible download paths
	precreated="http://download.openvz.org/template/precreated/"
	beta=$precreated"beta/"
	contrib=$precreated"contrib/"
	unsupported=$precreated"unsupported/"

	# wget: set quite mode && output directory
	flags="-q -P /vz/template/cache"

	for link in $precreated $beta $contrib $unsupported
	do
		echo " * try $link$pack"
		wget $flags $link$pack
		if [ $? -eq 0 ]; then
			exit 0
		fi
	done
	echo "template not found"
	exit 1
}

usage()
{
	cat <<EOF
$1 -h|--help -t|--template=<name>
EOF
	return 0
}

options=$(getopt -o ht:n -l help,template:,name -- "$@")
if [ $? -ne 0 ]; then
    usage $(basename $0)
    exit 1
fi
eval set -- "$options"

while true
do
    case "$1" in
	-h|--help)      usage $0 && exit 0;;
	-t|--template)  check_cache $2;  get_template $2;  break;;
	--)             usage $0 && exit 0 ;;
        *)              break ;;
    esac
done
