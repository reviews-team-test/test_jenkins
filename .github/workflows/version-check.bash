#!/bin/bash
repository="dde-daemon"
result=$(echo ${repository} | grep "/")
project_tmp=${repository}
if [[ "$result" != "" ]]; then
    project_tmp=$(echo ${repository} | awk -F'/' '{print $2}') 
fi
version_str=$(dpkg-parsechangelog -l debian/changelog -n 2|grep ${project_tmp}|awk -F'[()]' '{print $2}'|grep -v '^$\|^Task\|^Bug\|^Influence'|tr '\n' ' ')
version_num=$(echo $version_str|awk '{print NF}')
echo "version_str is ${version_str}"
echo "version_num is ${version_num}"
if [[ "$version_num" == "2" ]]; then
    version0=$(echo $version_str|awk '{print $1}')
    version1=$(echo $version_str|awk '{print $2}')
    echo $version0
    echo $version1
    check_result=$(dpkg --compare-versions ${version0} gt ${version1})
    if [[ "$check_result" == "1" ]];then
        echo $version_str
        exit 1
    fi
fi