"""Explores a service"""

from aiven_metadata_parser import (
    backup,
    kafka,
    tag,
    integration,
    flink,
)
from aiven_metadata_parser import pg
from aiven_metadata_parser import opensearch, kafka_connect, mysql, grafana, redis

SERVICE_MAP = {}
EXPLORER_METHODS = {}


def add_explorer(service_type):
    """Register an explorer method for the given service_type"""

    def adder(method):
        global EXPLORER_METHODS
        EXPLORER_METHODS[service_type] = method
        return method

    return adder


# This method parses all services to indentify internal IPs or hostnames


def populate_service_map(self, service_type, service_name, project):
    """Populates the service map"""
    global SERVICE_MAP

    service = self.get_service(project=project, service=service_name)
    if service["state"] != "RUNNING":
        return

    try:
        if service_type == "kafka":
            SERVICE_MAP[service["service_uri_params"]["host"]] = service_name
            for url in service["connection_info"]["kafka"]:
                host = url.split(":")[0]
                SERVICE_MAP[host] = service_name
        elif service_type == "flink":
            SERVICE_MAP[service["service_uri_params"]["host"]] = service_name
            for url in service["connection_info"]["flink"]:
                host = url.split(":")[0]
                SERVICE_MAP[host] = service_name
        elif service_type == "pg":
            SERVICE_MAP[
                service["connection_info"]["pg_params"][0]["host"]
            ] = service_name
            for component in service["components"]:
                if component["component"] == "pg":
                    SERVICE_MAP[component["host"]] = service_name
        elif service_type == "mysql":
            SERVICE_MAP[
                service["connection_info"]["mysql_params"][0]["host"]
            ] = service_name
        elif service_type in [
            "grafana",
            "opensearch",
            "elasticsearch",
            "kafka_connect",
            "mirrormaker",
            "clickhouse",
            "cassandra",
            "redis",
            "m3db",
            "m3aggregator",
            "m3coordinator",
            "influxdb",
        ]:
            host = service["service_uri_params"]["host"]
            SERVICE_MAP[host] = service_name
            print(host)
        else:
            print(
                f"Ignoring RUNNING {service_type} service {service_name}"
                f"with unrecognised type {service_type}"
            )
    except KeyError as err:
        print(
            f"Error looking up host for RUNNING {service_type}"
            f"service {service_name}: {err}"
        )


def explore(self, service_type, service_name, project):
    """Explores a service"""
    edges = []
    nodes = []
    global SERVICE_MAP
    host = "no-host"
    service = self.get_service(project=project, service=service_name)
    if service["state"] != "RUNNING":
        return nodes, edges

    try:
        explorer_fn = EXPLORER_METHODS[service_type]
    except KeyError:
        print(
            f"Don't know how to explore RUNNING {service_type}"
            f"service {service_name}"
        )

        return nodes, edges

    try:
        cloud = service["cloud_name"]
        plan = service["plan"]
        host, port, new_nodes, new_edges, SERVICE_MAP = explorer_fn(
            self, service, service_name, project
        )

        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Setting the node for the service
        nodes.append(
            {
                "id": service_name,
                "host": host,
                "port": port,
                "cloud": cloud,
                "plan": plan,
                "service_type": service_type,
                "type": "service",
                "label": service_name,
            }
        )

        # Getting components

        (new_nodes, new_edges) = explore_components(
            service_name, service_type, service["components"]
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Getting integrations

        (new_nodes, new_edges) = integration.explore_integrations(
            self, service_name, service_type, project
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

        # Looking for service tags

        new_nodes, new_edges = tag.explore_tags(
            self, service_name, service_type, project
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

        new_nodes, new_edges = backup.explore_backups(
            self, service_name, service_type, project
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

    except Exception as err:
        print(
            f"Error looking up data for RUNNING {service_type}"
            f" service {service_name}:"
            f" {err.__class__.__name__} {err}"
        )

    return nodes, edges


@add_explorer("influxdb")
def explore_influxdb(self, service, service_name, project):
    """Explores an InfluxDB service"""
    print(str(self) + service_name + project)
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("elasticsearch")
def explore_elasticsearch(self, service, service_name, project):
    """Explores an ElasticSearch service"""
    print(str(self) + service_name + project)
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("m3aggregator")
def explore_m3aggregator(self, service, service_name, project):
    """Explores an M3 aggregator service"""
    print(str(self) + service_name + project)
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("m3coordinator")
def explore_m3coordinator(self, service, service_name, project):
    """Explores an M3Coordinator service"""
    print(str(self) + service_name + project)
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("clickhouse")
def explore_clickhouse(self, service, service_name, project):
    """Explores an Clickhouse service"""
    print(str(self) + service_name + project)
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("kafka_mirrormaker")
def explore_mirrormaker(self, service, service_name, project):
    """Explores an MM2 service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = 443
    print(str(self) + service_name + project)
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("m3db")
def explore_m3db(self, service, service_name, project):
    """Explores an M3DB service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    print(str(self) + service_name + project)
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("redis")
def explore_redis_fun(self, service, service_name, project):
    """Explores an Redis service"""
    return redis.explore_redis(
        self, service, service_name, project, SERVICE_MAP
    )


@add_explorer("cassandra")
def explore_cassandra_fun(self, service, service_name, project):
    """Explores an InfluxDB service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]
    print(str(self) + service_name + project)
    # need to finish
    return host, port, nodes, edges, SERVICE_MAP


@add_explorer("grafana")
def explore_grafana_fun(self, service, service_name, project):
    """Explores an Grafana service"""
    return grafana.explore_grafana(service, service_name, SERVICE_MAP)


@add_explorer("opensearch")
def explore_opensearch_fun(self, service, service_name, project):
    """Explores an OpenSearch service"""
    return opensearch.explore_opensearch(
        self, service, service_name, project, SERVICE_MAP
    )


@add_explorer("flink")
def explore_flink_fun(self, service, service_name, project):
    """Explores an Apache Flink service"""
    return flink.explore_flink(
        self, service, service_name, project, SERVICE_MAP
    )


# Exploring Kafka Services


@add_explorer("kafka")
def explore_kafka_fun(self, service, service_name, project):
    """Explores an Apache Kafka service"""
    return kafka.explore_kafka(
        self, service, service_name, project, SERVICE_MAP
    )


# Exploring Kafka Services


@add_explorer("kafka_connect")
def explore_kafka_connect_fun(self, service, service_name, project):
    """Explore a Kafka Connect service.

    Note that `service` will be None if we're called from explore_kafka
    """
    return kafka_connect.explore_kafka_connect(
        self, service, service_name, project, SERVICE_MAP
    )


@add_explorer("mysql")
def explore_mysql_fun(self, service, service_name, project):
    """Explores an MySQL service"""
    return mysql.explore_mysql(service, service_name, SERVICE_MAP)


@add_explorer("pg")
def explore_pg_fun(self, service, service_name, project):
    """Explores an PG service"""
    return pg.explore_pg(self, service, service_name, project, SERVICE_MAP)


def explore_ext_endpoints(self, project):
    """Explores an Endpoint"""
    nodes = []
    edges = []
    ext_endpoints = self.get_service_integration_endpoints(project=project)

    for ext_endpoint in ext_endpoints:
        nodes.append(
            {
                "id": "ext" + ext_endpoint["endpoint_name"],
                "service_type": ext_endpoint["endpoint_type"],
                "type": "external_endpoint",
                "label": ext_endpoint["endpoint_name"],
            }
        )

    return nodes, edges


def explore_components(service_name, service_type, components):
    nodes = []
    edges = []

    global SERVICE_MAP

    for component in components:
        nodes.append(
            {
                "id": service_type
                + "~"
                + service_name
                + "~node~"
                + component.get("host"),
                "host": component.get("host"),
                "port": component.get("port"),
                "privatelink_connection_id": component.get(
                    "privatelink_connection_id"
                ),
                "route": component.get("route"),
                "usage": component.get("usage"),
                "type": "service_node",
                "service_type": service_type,
                "label": component.get("host"),
            }
        )
        edges.append(
            {
                "from": service_type
                + "~"
                + service_name
                + "~node~"
                + component.get("host"),
                "to": service_name,
                "label": "partition",
            }
        )
        SERVICE_MAP[component.get("host")] = service_name
    return nodes, edges
