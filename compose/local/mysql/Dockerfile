FROM mysql:5.7

WORKDIR /mysql

ENV AUTO_RUN_DIR /docker-entrypoint-initdb.d
ENV FILE_0 init_database.sql

COPY ./compose/local/mysql/${FILE_0} ./
COPY ./compose/local/mysql/sql_start.sh ${AUTO_RUN_DIR}/

RUN chmod a+x ${AUTO_RUN_DIR}/sql_start.sh