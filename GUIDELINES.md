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

