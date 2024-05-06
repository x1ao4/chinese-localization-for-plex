#!/bin/sh

# 如果宿主机的目录中没有这两个文件，就从镜像中复制
if [ ! -f /app/config/config.ini ]; then
    cp /app/template/config.ini /app/config/config.ini
fi

if [ ! -f /app/config/tags.json ]; then
    cp /app/template/tags.json /app/config/tags.json
fi

# 运行 Python 脚本
exec "$@"
