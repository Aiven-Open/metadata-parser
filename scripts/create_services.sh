PROJECT_NAME=$1
. conf/conf.env


avn --auth-token $TOKEN project switch $PROJECT_NAME

avn --auth-token $TOKEN service create demo-kafka               \
    --service-type kafka                    \
    --cloud google-europe-west3             \
    --plan business-4                       \
    -c kafka_connect=true                   \
    -c schema_registry=true                 \
    -c kafka.auto_create_topics_enable=true                                          

avn --auth-token $TOKEN service create demo-pg                  \
    --service-type pg                       \
    --cloud google-europe-west3             \
    --plan business-4     

avn --auth-token $TOKEN service create demo-grafana             \
    --service-type grafana                  \
    --cloud google-europe-west3             \
    --plan startup-4                              

avn --auth-token $TOKEN service create demo-opensearch          \
    --service-type opensearch               \
    --cloud google-europe-west3             \
    --plan business-4

avn --auth-token $TOKEN service integration-create      \
    -t datasource                   \
    -d demo-pg                      \
    -s demo-grafana

avn --auth-token $TOKEN service integration-create      \
    -t datasource                   \
    -d demo-opensearch              \
    -s demo-grafana

avn --auth-token $TOKEN service wait demo-kafka 

avn --auth-token $TOKEN service wait demo-pg

avn --auth-token $TOKEN service cli demo-pg << EOF
\i scripts/create_pg_tbl.sql
EOF

PG_PWD=$(avn --auth-token $TOKEN service user-get demo-pg --format '{password}' --username avnadmin)
PG_HOSTNAME=$(avn --auth-token $TOKEN service get demo-pg --json | jq -r '.connection_info.pg_params[0].host')
PG_PORT=$(avn --auth-token $TOKEN service get demo-pg --json | jq -r '.connection_info.pg_params[0].port')
KAFKA_SCHEMA_REGISTRY_URL=$(avn --auth-token $TOKEN service get demo-kafka --json | jq -r '.connection_info.schema_registry_uri' | sed -e 's/avnadmin\:[0-9a-zA-Z]*\@//g')
KAFKA_SCHEMA_REGISTRY_PWD=$(avn --auth-token $TOKEN service user-get demo-kafka --username avnadmin --format '{password}')

avn --auth-token $TOKEN service connector create demo-kafka '''
{
    "name": "cdc-source-pg",
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "'$PG_HOSTNAME'",
    "database.port": "'$PG_PORT'",
    "database.user": "avnadmin",
    "database.password": "'$PG_PWD'",
    "database.dbname": "defaultdb",
    "database.sslmode": "require",
    "plugin.name": "wal2json",
    "slot.name": "test_slot",
    "publication.name": "test_pub",
    "database.server.name": "my_pg_source",
    "table.include.list": "public.dogs",
    "tombstones.on.delete": "true",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "'$KAFKA_SCHEMA_REGISTRY_URL'",
    "key.converter.basic.auth.credentials.source": "USER_INFO",
    "key.converter.schema.registry.basic.auth.user.info": "avnadmin:'$KAFKA_SCHEMA_REGISTRY_PWD'",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "'$KAFKA_SCHEMA_REGISTRY_URL'",
    "value.converter.basic.auth.credentials.source": "USER_INFO",
    "value.converter.schema.registry.basic.auth.user.info": "avnadmin:'$KAFKA_SCHEMA_REGISTRY_PWD'"
}'''

OS_PWD=$(avn --auth-token $TOKEN service user-get demo-opensearch --format '{password}' --username avnadmin)
OS_HOST=$(avn --auth-token $TOKEN service get demo-opensearch  --json | jq -r '.service_uri_params.host')
OS_PORT=$(avn --auth-token $TOKEN service get demo-opensearch  --json | jq -r '.service_uri_params.port')

avn --auth-token $TOKEN service wait demo-opensearch

avn --auth-token $TOKEN service connector create demo-kafka '''
{
    "name":"sink_opensearch",
    "connector.class": "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
    "topics": "my_pg_source.public.dogs",
    "connection.url": "https://'$OS_HOST':'$OS_PORT'",
    "connection.username": "avnadmin",
    "connection.password": "'$OS_PWD'",
    "type.name": "myname",
    "tasks.max":"1",
    "key.ignore": "true",
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "'$KAFKA_SCHEMA_REGISTRY_URL'",
    "key.converter.basic.auth.credentials.source": "USER_INFO",
    "key.converter.schema.registry.basic.auth.user.info": "avnadmin:'$KAFKA_SCHEMA_REGISTRY_PWD'",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "'$KAFKA_SCHEMA_REGISTRY_URL'",
    "value.converter.basic.auth.credentials.source": "USER_INFO",
    "value.converter.schema.registry.basic.auth.user.info": "avnadmin:'$KAFKA_SCHEMA_REGISTRY_PWD'"
}'''


avn --auth-token $TOKEN service wait demo-grafana

GRAFANA_PWD=$(avn --auth-token $TOKEN service get demo-grafana --json | jq -r '.users[0]["password"]')
GRAFANA_URL=$(avn --auth-token $TOKEN service get demo-grafana --json | jq -r '.service_uri')

curl --location --request GET "$GRAFANA_URL/api/datasources" \
    --header "Authorization: Basic $GRAFANA_PWD"

# Add a grafana dashboard
avn --auth-token $TOKEN service wait demo-grafana
python src/add_grafana_dashboard.py $PROJECT_NAME
