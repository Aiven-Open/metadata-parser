PROJECT_NAME=$1
echo $PROJECT_NAME

avn project switch $PROJECT_NAME


avn service terminate demo-kafka --force
avn service terminate demo-flink --force
avn service terminate demo-pg --force
avn service terminate demo-mysql --force
avn service terminate demo-opensearch --force
avn service terminate demo-grafana --force
avn service terminate demo-kafka-connect --force
