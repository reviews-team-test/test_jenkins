#! /bin/bash

prefix="debian/"
NoNeedDebianFiles="debian/changelog, debian/copyright, debian/compat, debian/source/format"
changeFile=$(git diff-tree --no-commit-id --name-only -r HEAD)

num=0
for file in $(git diff-tree --no-commit-id --name-only -r HEAD); do
  if [[ $file =~ ^$prefix ]]; then
    if echo "$NoNeedDebianFiles" | grep -q "$file"; then
      continue
    else
      num=$((num+1))
    fi
  fi
done
if [ $num -eq 0 ]; then
  echo "[PASS]: debian前缀检查通过"
  exit 0
else
  echo "[FAIL]: debian前缀检查不通过'"
  echo "$changeFile"
  exit 1
fi