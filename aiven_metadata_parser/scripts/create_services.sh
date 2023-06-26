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

avn --auth-token $TOKEN service create demo-flink               \
    --service-type flink                    \
    --cloud google-europe-west3             \
    --plan business-4                                            

avn --auth-token $TOKEN service create demo-pg                  \
    --service-type pg                       \
    --cloud google-europe-west3             \
    --plan business-4                                   

avn --auth-token $TOKEN service create demo-mysql               \
    --service-type mysql                    \
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

avn --auth-token $TOKEN service create demo-kafka-connect       \
    --service-type kafka_connect            \
    --cloud google-europe-west3             \
    --plan business-4

avn --auth-token $TOKEN service create demo-redis       \
    --service-type redis            \
    --cloud google-europe-west3     \
    --plan business-4

avn --auth-token $TOKEN service integration-create      \
    -t kafka_connect                \
    -s demo-kafka                   \
    -d demo-kafka-connect

avn --auth-token $TOKEN service integration-create      \
    -t datasource                   \
    -d demo-pg                      \
    -s demo-grafana

avn --auth-token $TOKEN service integration-create      \
    -t datasource                   \
    -d demo-opensearch              \
    -s demo-grafana

avn --auth-token $TOKEN service integration-create      \
    -t flink                        \
    -s demo-kafka                   \
    -d demo-flink

avn --auth-token $TOKEN service integration-create      \
    -t flink                        \
    -s demo-pg                      \
    -d demo-flink

avn --auth-token $TOKEN service wait demo-kafka 

avn --auth-token $TOKEN service topic-create demo-kafka inventory_items \
    --partitions 4              \
    --replication 3             \
    --tag bu=sales              \
    --tag scope=sales-inventory

avn --auth-token $TOKEN service topic-create demo-kafka ssh_logins \
    --partitions 4              \
    --replication 3             \
    --tag bu=security           \
    --tag scope=security-screening

avn --auth-token $TOKEN service schema create demo-kafka \
    --subject=click-record-schema    \
    --schema '''
    {"type": "record",
    "name": "ClickRecord",
    "namespace": "io.aiven.avro.example",
    "fields": [
        {"name": "session_id", "type": "string"},
        {"name": "browser", "type": ["string", "null"]},
        {"name": "campaign", "type": ["string", "null"]},
        {"name": "channel", "type": "string"},
        {"name": "referrer", "type": ["string", "null"], "default": "None"},
        {"name": "ip", "type": ["string", "null"]}
    ]
    }'''

avn --auth-token $TOKEN service wait demo-pg

avn --auth-token $TOKEN service cli demo-pg << EOF
\i aiven_metadata_parser/scripts/create_pg_tbl.sql
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
    "table.include.list": "public.pasta",
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
avn --auth-token $TOKEN service wait demo-kafka-connect

avn --auth-token $TOKEN service connector create demo-kafka-connect '''
{
    "name": "cdc-source-pg-kafka-cc",
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "'$PG_HOSTNAME'",
    "database.port": "'$PG_PORT'",
    "database.user": "avnadmin",
    "database.password": "'$PG_PWD'",
    "database.dbname": "defaultdb",
    "database.sslmode": "require",
    "plugin.name": "wal2json",
    "slot.name": "test_slot_cc",
    "publication.name": "test_pub_cc",
    "database.server.name": "my_pg_source_cc",
    "table.include.list": "public.pasta",
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

avn --auth-token $TOKEN service connector create demo-kafka-connect '''
{
    "name":"sink_opensearch",
    "connector.class": "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector",
    "topics": "my_pg_source.public.pasta",
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


# Connect to Kafka to create Data
avn --auth-token $TOKEN service user-creds-download demo-kafka --username avnadmin -d certs

KAFKA_SERVICE_URI=$(avn --auth-token $TOKEN service get  demo-kafka --format '{service_uri}')

echo '''
bootstrap.servers='$KAFKA_SERVICE_URI'
security.protocol=ssl
ssl.key.location=certs/service.key
ssl.certificate.location=certs/service.cert
ssl.ca.location=certs/ca.pem
''' > kcat.config 


echo '{"ip":"192.178.0.10","time":'$(date '+%s')',"status":"ok"}' | kcat -F kcat.config -P -t ssh_logins
echo '{"ip":"192.168.0.123","time":'$(date '+%s')',"status":"ko"}' | kcat -F kcat.config -P -t ssh_logins
echo '{"ip":"192.168.0.123","time":'$(date '+%s')',"status":"ko"}' | kcat -F kcat.config -P -t ssh_logins
echo '{"ip":"192.168.0.123","time":'$(date '+%s')',"status":"ko"}' | kcat -F kcat.config -P -t ssh_logins
echo '{"ip":"192.168.0.123","time":'$(date '+%s')',"status":"ko"}' | kcat -F kcat.config -P -t ssh_logins

# Connect to mysql

avn --auth-token $TOKEN service wait demo-mysql
MYSQL_HOST=$(avn --auth-token $TOKEN service get demo-mysql --json | jq -r '.service_uri_params.host')
MYSQL_PORT=$(avn --auth-token $TOKEN service get demo-mysql --json | jq -r '.service_uri_params.port')
MYSQL_PWD=$(avn --auth-token $TOKEN service get demo-mysql --json | jq -r '.service_uri_params.password')
mysql -u avnadmin -P $MYSQL_PORT -h $MYSQL_HOST -D defaultdb -p$MYSQL_PWD < aiven_metadata_parser/scripts/create_mysql_tbl.sql


KAFKA_FLINK_SI=$(avn --auth-token $TOKEN service integration-list --format '{source_service} {service_integration_id}' demo-flink | grep demo-kafka | awk -F ' ' '{print $2}')


avn --auth-token $TOKEN service wait demo-flink

avn --auth-token $TOKEN service flink create-application demo-flink  \
    --project $PROJECT_NAME                                     \
  "{\"name\":\"Alert_Pipeline\"}"

FLINK_APP_ID=$(avn --auth-token $TOKEN service flink list-applications demo-flink       \
                   --project $PROJECT_NAME                                     \
                    | jq -r '.applications[] | select(.name == "Alert_Pipeline") | .id')

avn --auth-token $TOKEN service flink create-application-version demo-flink           \
  --project $PROJECT_NAME                                     \
  --application-id $FLINK_APP_ID                                  \
  """{
    \"sources\": [
        {
        \"create_table\":
            \"CREATE TABLE ssh_in (ip VARCHAR, \`time\` BIGINT, status VARCHAR, time_ltz AS TO_TIMESTAMP_LTZ(\`time\`, 3), WATERMARK FOR time_ltz AS time_ltz - INTERVAL '10' seconds)\n\
            WITH (\n\
                'connector' = 'kafka',\n\
                'properties.bootstrap.servers' = '',\n\
                'scan.startup.mode' = 'earliest-offset',\n\
                'value.fields-include' = 'ALL',\n\
                'topic' = 'ssh_logins',\n\
                'value.format' = 'json'\n\
            )\",
            \"integration_id\": \"$KAFKA_FLINK_SI\"
        } ],
    \"sinks\": [
        {
        \"create_table\":
            \"CREATE TABLE ssh_alert (ip VARCHAR, time_ltz TIMESTAMP(3), status VARCHAR)\n\
            WITH (\n\
                'connector' = 'kafka',\n\
                'properties.bootstrap.servers' = '',\n\
                'scan.startup.mode' = 'earliest-offset',\n\
                'topic' = 'ssh_alert_logins',\n\
                'value.format' = 'json'\n\
            )\",
            \"integration_id\": \"$KAFKA_FLINK_SI\"
        }
        ],
    \"statement\":
        \"insert into ssh_alert select ip, time_ltz, status from ssh_in where status = 'ko'\"
    }"""

FLINK_APP_VERSION_ID=$(avn --auth-token $TOKEN service flink get-application demo-flink \
    --project $PROJECT_NAME                                     \
    --application-id $FLINK_APP_ID                                  \
    | jq -r '.application_versions[] | select(.version == 1) | .id')

avn --auth-token $TOKEN service flink create-application-deployment demo-flink      \
  --project $PROJECT_NAME                                   \
  --application-id $FLINK_APP_ID                                \
  "{\"parallelism\": 1,\"restart_enabled\": true,  \"version_id\": \"$FLINK_APP_VERSION_ID\"}"

avn --auth-token $TOKEN service wait demo-grafana

GRAFANA_PWD=$(avn --auth-token $TOKEN service get demo-grafana --json | jq -r '.users[0]["password"]')
GRAFANA_URL=$(avn --auth-token $TOKEN service get demo-grafana --json | jq -r '.service_uri')

curl --location --request GET "$GRAFANA_URL/api/datasources" \
    --header "Authorization: Basic $GRAFANA_PWD"

# Add a grafana dashboard
avn --auth-token $TOKEN service wait demo-grafana
python aiven_metadata_parser/src/add_grafana_dashboard.py $PROJECT_NAME

# Add redis user and ACL
avn --auth-token $TOKEN service wait demo-redis
avn --auth-token $TOKEN service user-create --project $PROJECT_NAME --username test demo-redis
avn --auth-token $TOKEN service user-set-access-control --project $PROJECT_NAME --username test --redis-acl-keys '~app2:*' demo-redis

mysql -u avnadmin -P $MYSQL_PORT -h $MYSQL_HOST -D defaultdb -p$MYSQL_PWD < aiven_metadata_parser/scripts/create_mysql_usr.sql
