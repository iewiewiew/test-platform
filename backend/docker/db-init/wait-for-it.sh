#!/bin/sh
# 官方脚本修改版：https://github.com/vishnubob/wait-for-it

TIMEOUT=15
QUIET=0

while getopts "t:q" option; do
  case "$option" in
    t) TIMEOUT=$OPTARG ;;
    q) QUIET=1 ;;
  esac
done

shift $((OPTIND-1))
hostport=$1
shift
cmd="$@"

until mysqladmin ping -h "${hostport%:*}" -P "${hostport#*:}" --silent;
do
  echo "等待 MySQL 在 ${hostport} 就绪..."
  sleep 1
  TIMEOUT=$((TIMEOUT - 1))

  if [ $TIMEOUT -eq 0 ]; then
    echo "超时：MySQL 未在指定时间内启动" >&2
    exit 1
  fi
done

echo "MySQL 已就绪，执行命令: $cmd"
exec $cmd