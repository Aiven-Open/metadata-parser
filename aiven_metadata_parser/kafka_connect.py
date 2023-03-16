"""Parsing Kafka Connect services"""

import urllib


def find_kafka_service_from_connect(self, service_name, service_type, project):
    """
    Finds a Kafka service from its connect endpoint
    """
    serv_type = service_type
    serv_name = service_name
    if serv_type == "kafka_connect":
        serv_type = "kafka"
        integrations = self.get_service_integrations(
            service=service_name, project=project
        )
        for integration in integrations:
            if (
                integration["enabled"] is True
                and integration["integration_type"] == "kafka_connect"
            ):
                serv_name = integration["source_service"]
    return serv_name, serv_type


def explore_kafka_connect(
    self, service_det, service_name, project, service_map
):
    """Explore a Kafka Connect service.

    Note that `service` will be None if we're called from explore_kafka
    """
    nodes = []
    edges = []
    service = {}
    if service_det is None:
        service["service_type"] = "kafka"
        service["host"] = None
        service["port"] = None
    else:
        service["service_type"] = "kafka_connect"
        service["host"] = service_det["service_uri_params"]["host"]
        service["port"] = service_det["service_uri_params"]["port"]

    service["project"] = project
    service["service_name"] = service_name
    service["service_map"] = service_map
    # The service map allows to indetify if the source/target
    # of a connector is within aiven or external

    connectors = self.list_kafka_connectors(
        service=service_name, project=project
    )

    # Getting connectors
    for connector in connectors["connectors"]:
        # Checking connector properties
        properties = {
            "id": service["service_type"]
            + "~"
            + service_name
            + "~connect~"
            + connector["config"]["name"],
            "service_type": service["service_type"],
            "type": "kafka-connect",
            "label": connector["config"]["name"],
            "class": connector["config"]["connector.class"],
        }

        ##########################################
        # Debezium PostgreSQL conector           #
        ##########################################
        if (
            connector["config"]["connector.class"]
            == "io.debezium.connector.postgresql.PostgresConnector"
        ):
            new_nodes, new_edges, service_map = explore_debezium_pg_source(
                self, connector, service, service_map
            )

        #####################
        # Opensearch sink   #
        #####################
        if (
            connector["config"]["connector.class"]
            == "io.aiven.kafka.connect.opensearch.OpensearchSinkConnector"
        ):
            new_nodes, new_edges, service_map = explore_opensearch_sink(
                self, connector, service, service_map
            )

        nodes = nodes + new_nodes
        edges = edges + new_edges

        nodes.append(properties)

    return service["host"], service["port"], nodes, edges, service_map


def explore_debezium_pg_source(self, connector, service, service_map):
    """Parsing Debezium PG source"""

    nodes = []
    edges = []

    target_host = connector["config"]["database.hostname"]
    target_service = service_map.get(target_host)
    # Looks for the target service to be in Aiven,
    # if None, creates a new node for the target service
    if target_service is None:
        target_service = "ext-pg-" + target_host
        # Create node for New service
        nodes.append(
            {
                "id": "ext-pg-" + target_host,
                "service_type": "ext-pg",
                "type": "external-postgresql",
                "label": "ext-pg-" + target_host,
            }
        )
        tables = connector["config"]["table.include.list"].split(",")
        for table in tables:
            # schema is the first part of the table
            schema = table.split(".")[0]
            # table_name is the second part of the table
            table_name = table.split(".")[1]
            # Create node for the schema
            nodes.append(
                {
                    "id": "ext-pg-" + target_host + "~schema~" + schema,
                    "service_type": "ext-pg-schema",
                    "type": "external-postgresql-schema",
                    "label": schema,
                }
            )
            # Create node for the table
            nodes.append(
                {
                    "id": "ext-pg-"
                    + target_host
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + table_name,
                    "service_type": "ext-pg-table",
                    "type": "external-postgresql-table",
                    "label": table_name,
                }
            )
            # Create edge from schema to table
            edges.append(
                {
                    "from": "ext-pg-" + target_host + "~schema~" + schema,
                    "to": "ext-pg-"
                    + target_host
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + table_name,
                }
            )
            # Create edge from host to schema
            edges.append(
                {
                    "from": "ext-pg-" + target_host,
                    "to": "ext-pg-" + target_host + "~schema~" + schema,
                }
            )
            # Create edge from connector to source table
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": "ext-pg-"
                    + target_host
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + table_name,
                }
            )
            # Find the kafka instance that the connector
            # is pushing/taking data from
            (serv_name, serv_type) = find_kafka_service_from_connect(
                self,
                service["service_name"],
                service["service_type"],
                service["project"],
            )
            # Create edge from connector to target topic
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": serv_type
                    + "~"
                    + serv_name
                    + "~topic~"
                    + connector["config"]["database.server.name"]
                    + "."
                    + table,
                    "label": "kafka-connect-connector",
                }
            )
        service_map[target_host] = "ext-pg-" + target_host
    # Looks for the target is in Aiven, connecting it
    else:
        tables = connector["config"]["table.include.list"].split(",")
        for table in tables:
            # schema is the first part of the table
            schema = table.split(".")[0]
            # table_name is the second part of the table
            table_name = table.split(".")[1]
            # Create an edge betwen the connector and the pg table
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": "pg~"
                    + target_service
                    + "~schema~"
                    + schema
                    + "~table_view~"
                    + table_name,
                    "label": "table",
                }
            )
            # Create an edge betwen the connector
            # and the kafka connect service
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": service["service_name"],
                    "label": "kafka-connect-connector",
                }
            )
            # Find the kafka instance that
            # the connector is pushing/taking data from
            (serv_name, serv_type) = find_kafka_service_from_connect(
                self,
                service["service_name"],
                service["service_type"],
                service["project"],
            )
            # Create an edge betwen
            # the connector and the source kafka topic
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": serv_type
                    + "~"
                    + serv_name
                    + "~topic~"
                    + connector["config"]["database.server.name"]
                    + "."
                    + table,
                    "label": "kafka-connect-connector",
                }
            )
    return nodes, edges, service_map


def explore_opensearch_sink(self, connector, service, service_map):
    """Parsing OpenSearch sink connector"""

    nodes = []
    edges = []

    target_host = urllib.parse.urlparse(
        connector["config"]["connection.url"]
    ).hostname

    target_service = service_map.get(target_host)

    # Looks for the target service to be in Aiven,
    # if None, creates a new node for the target service
    if target_service is None:
        print("NOT FOUUUUND!!!!!!!!!!!!!!!" + target_host)
        # tobedone What should we create in case
        # we don't find the target Opensearch?
    else:
        # Add edge to source service
        edges.append(
            {
                "from": service["service_type"]
                + "~"
                + service["service_name"]
                + "~connect~"
                + connector["config"]["name"],
                "to": service["service_name"],
                "label": "kafka-connect-connector",
            }
        )
        for topic in connector["config"]["topics"].split(","):
            # Find the kafka instance that
            # the connector is pushing/taking data from
            (serv_name, serv_type) = find_kafka_service_from_connect(
                self,
                service["service_name"],
                service["service_type"],
                service["project"],
            )
            # Add edge to source topic
            edges.append(
                {
                    "from": serv_type + "~" + serv_name + "~topic~" + topic,
                    "to": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "label": "kafka-connect-connector",
                }
            )
            # Add edge to destination opensearch index
            edges.append(
                {
                    "from": service["service_type"]
                    + "~"
                    + service["service_name"]
                    + "~connect~"
                    + connector["config"]["name"],
                    "to": "opensearch~" + target_service + "~index~" + topic,
                    "label": "kafka-connect-connector",
                }
            )
    return nodes, edges, service_map
