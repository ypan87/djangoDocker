#!/bin/bash
echo '开始初始化数据库'

mysql -uroot -p$MYSQL_ROOT_PASSWORD <<EOF
source /mysql/$FILE_0