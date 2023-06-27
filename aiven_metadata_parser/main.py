from aiven.client import client
import explore_service
import pyvis_display as pyvis_display
import configparser


def main():
    # Reading conf.env configuration file
    with open("aiven_metadata_parser/conf/conf.env", "r") as f:
        config_string = "[DEFAULT]\n" + f.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)

    # Creating Aiven client instance
    myclient = client.AivenClient(base_url=config["DEFAULT"]["BASE_URL"])

    # Authenticating and storing the token
    # result = myclient.authenticate_user(email=config['DEFAULT']['USERNAME'], password=config['DEFAULT']['PASSWORD'])
    myclient.auth_token = config["DEFAULT"]["TOKEN"]

    # Creating empty nodes and edges lists
    nodes = []
    edges = []

    # The service order helps analysis first "standalone" services and then connection services, this might be useful
    # to parse first services which can be either source or sink of other services (e.g. Kafka connect might use a PG
    # table as a source)

    services_order = {
        "opensearch": 1,
        "elasticsearch": 1,
        "pg": 1,
        "redis": 1,
        "mysql": 1,
        "clickhouse": 1,
        "cassandra": 1,
        "m3db": 1,
        "m3aggregator": 1,
        "m3coordinator": 1,
        "influxdb": 1,
        "kafka": 2,
        "kafka_connect": 3,
        "kafka_mirrormaker": 3,
        "flink": 3,
        "grafana": 3,
    }

    # Listing the services
    services = myclient.get_services(project=config["DEFAULT"]["PROJECT"])

    # Ordering based on service_order
    services.sort(key=lambda x: services_order[x["service_type"]])

    # Initial loop to find all ip/hostname of existing services
    print("Locate IP/hostname of each service")
    for i, service in enumerate(services, start=1):
        # if service["service_name"]!='test':
        print(
            f"{i}/{len(services)} {service['service_name']} {service['service_type']}"
        )
        # if service["service_type"]=='grafana':
        explore_service.populate_service_map(
            myclient,
            service["service_type"],
            service["service_name"],
            project=config["DEFAULT"]["PROJECT"],
        )

    # Second loop to find details of each service
    print()
    print("Find details of each service")
    for i, service in enumerate(services, start=1):
        print(
            f"{i}/{len(services)} Query {service['service_name']} {service['service_type']}"
        )
        # if service["service_name"] != 'test':
        (newnodes, newedges) = explore_service.explore(
            myclient,
            service["service_type"],
            service["service_name"],
            project=config["DEFAULT"]["PROJECT"],
        )
        nodes = nodes + newnodes
        edges = edges + newedges

    (newnodes, newedges) = explore_service.explore_ext_endpoints(
        myclient, project=config["DEFAULT"]["PROJECT"]
    )
    nodes = nodes + newnodes
    edges = edges + newedges

    # Creating viz with pyviz
    pyvis_display.pyviz_graphy(nodes, edges)


if __name__ == "__main__":
    main()
