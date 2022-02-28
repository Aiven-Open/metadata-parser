# How to Parse services

This doc explains how the Aiven metadata parser currently parses the services:

## Apache Kafka®

* **topics**: Aiven Client `list_service_topics`
* **users**: Aiven Client `get_service`
* **acl**: Aiven Client `get_service`

## Apache Kafka Connect®

* **connectors**: Aiven Client `list_kafka_connectors`
* **connector**: Parsing JSON of each connector separately

## MirrorMaker2®

To be done

## Apache Flink®

* **tables**: Aiven Client `list_flink_tables`
* **jobs**: Aiven Client `list_flink_jobs`

## OpenSearch®

* **indexes**: Aiven Client `get_service_indexes`

## ElasticSearch®

To be done (phasing out product)

## InfluxDB®

To be done 

## Grafana®

* **users**: Aiven Client `get_service`
* **datasources**: REST API `/api/datasources` endpoint
* **dashboards**: REST API `/api/search?dash-folder` endpoint

## Cassandra

To be done

## Redis

To be done

## M3DB, M3 Aggregator, M3coordinator

To be done

## MySQL

To be done

## PostgreSQL

Using psycopg2 

* **databases**: query `SELECT datname FROM pg_database;`
* **namespaces**: query `select catalog_name, schema_name, schema_owner from information_schema.schemata;`
* **tables**: query `SELECT schemaname, tablename, tableowner FROM pg_tables where tableowner <> 'postgres';`
* **users**: query `SELECT * FROM pg_user;`
* **role_table_grants**: query `SELECT grantee, table_schema, table_name, privilege_type,is_grantable FROM information_schema.role_table_grants;`
* **table columns**: query `select table_catalog, table_schema, table_name, column_name, data_type, is_nullable from information_schema.columns where table_schema not in ('information_schema', 'pg_catalog');`

## External Endpoints

Currenty listing the external endpoints only using Aiven Client `get_service_integration_endpoints`


Apache, Apache Kafka, Kafka, Apache Flink, Flink, Apache Cassandra, and Cassandra are either registered trademarks or trademarks of the Apache Software Foundation in the United States and/or other countries. ClickHouse is a registered trademark of ClickHouse, Inc. https://clickhouse.com. M3, M3 Aggregator, M3 Coordinator, OpenSearch, PostgreSQL, MySQL, InfluxDB, Grafana, Terraform, and Kubernetes are trademarks and property of their respective owners. *Redis is a trademark of Redis Ltd. and the Redis box logo is a mark of Redis Ltd. Any rights therein are reserved to Redis Ltd. Any use by Aiven is for referential purposes only and does not indicate any sponsorship, endorsement or affiliation between Redis and Aiven.  All product and service names used in this website are for identification purposes only and do not imply endorsement.