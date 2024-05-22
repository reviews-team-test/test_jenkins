#!/bin/bash

for file in $(git diff-tree --no-commit-id --name-only -r HEAD); do
  if [[ $file == 'debian/changelog' ]]; then
    version_str=$(dpkg-parsechangelog -l debian/changelog -n 2 | awk -F'[()]' '{print $2}'|grep -v '^$\|^Task\|^Bug\|^Influence'|awk -F'-' '{print $1}'|tr '\n' ' ')
    IFS=' ' read -r -a version_arr <<< "$version_str"
    if [[ ${#version_arr[*]} == 2 ]]; then
      version0=${version_arr[0]}
      version1=${version_arr[1]}
      version_flag=$(dpkg --compare-versions ${version0} gt ${version1} && echo true || echo false)
      if [[ $version_flag == true ]]; then
        echo "[PASS]: 版本检查通过:${version0}|${version1}"
      else
        echo "[FAIL]: 版本检查不通过:${version0}|${version1}"
        exit 1
      fi
    else
      if [[ ${#version_arr[*]} != 1 ]]; then
          echo "[ERR]: 版本检查异常:${version_str}"
      else
          echo "[PASS]: 版本检查通过:${version_str}"
      fi
    fi
    break
  else
    echo "无版本检查"
  fi
done