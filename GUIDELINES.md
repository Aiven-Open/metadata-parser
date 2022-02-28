# Network guidelines

For any service the metadata parser is analysing, it should extract the maximum detail of metadata.

For any entity you can find, create a node. Entities can be:

* Indexes
* Table
* namespaces
* topics
* ACLs

For anything that links two entities create an edge, like
* topic to Apache Kafka® service
* table to index
* index to user

# Node Id Naming Rules

The standard naming for the node `id` used so far is:

```
<SERVICE_TYPE>~<SERVICE_NAME>~<ENTITY_TYPE>~<ENTITY_NAME>
```

e.g. a user `franco` belonging to the Kafka instance `demo-kfk` will generate a node with `id`

```
kafka~demo-kfk~user~franco
```

In case there can be multiple objects with the same name (think a PG table in multiple schemas), we need to prefix the node `id` with all the identifiers making it unique. e.g.

```
pg~<SERVICE_NAME>~schema~<SCHEMA_NAME>~table~<TABLE_NAME>
```

You can add as many properties to the node as you want, the required ones are:

* `service_type`: allows an easier filtering of nodes by belonging service type
* `type`: defines the type of node 
* `label`: defines what is shown in the graph


Apache, Apache Kafka, Kafka, Apache Flink, Flink, Apache Cassandra, and Cassandra are either registered trademarks or trademarks of the Apache Software Foundation in the United States and/or other countries. ClickHouse is a registered trademark of ClickHouse, Inc. https://clickhouse.com. M3, M3 Aggregator, M3 Coordinator, OpenSearch, PostgreSQL, MySQL, InfluxDB, Grafana, Terraform, and Kubernetes are trademarks and property of their respective owners. *Redis is a trademark of Redis Ltd. and the Redis box logo is a mark of Redis Ltd. Any rights therein are reserved to Redis Ltd. Any use by Aiven is for referential purposes only and does not indicate any sponsorship, endorsement or affiliation between Redis and Aiven.  All product and service names used in this website are for identification purposes only and do not imply endorsement.