#!/bin/bash
# Script that retrieves a list of all the precreated templates available
# fron http://download.openvz.org/template/precreated/
# The output file also contains the download link for eeach entry

base_url=http://download.openvz.org/template/precreated/
list_file=distro_list.out

function crawl {
	wget -q -O distro_list.html $1
	cat distro_list.html | ./extract_url.sed > distro_list

	cat distro_list | grep 'gz$' | while read file;
	do
		distro_name=`echo $file | sed 's/.tar.gz//g'`
		echo "$distro_name $1$file" >> $list_file
	done

	cat distro_list | grep '/' | while read file;
	do
		crawl $1$file
	done
}
rm -f $list_file distro_list distro_list.html
crawl $base_url
rm -f distro_list distro_list.html

