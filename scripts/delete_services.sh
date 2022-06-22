PROJECT_NAME=$1
. conf/conf.env


avn --auth-token $TOKEN project switch $PROJECT_NAME


avn --auth-token $TOKEN service terminate demo-kafka --force
avn --auth-token $TOKEN service terminate demo-flink --force
avn --auth-token $TOKEN service terminate demo-pg --force
avn --auth-token $TOKEN service terminate demo-mysql --force
avn --auth-token $TOKEN service terminate demo-opensearch --force
avn --auth-token $TOKEN service terminate demo-grafana --force
avn --auth-token $TOKEN service terminate demo-kafka-connect --force
avn --auth-token $TOKEN service terminate demo-redis --force
