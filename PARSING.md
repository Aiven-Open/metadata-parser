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