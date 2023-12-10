from src import explore_service
import src.pyvis_display as pyvis_display
import configparser
from src.client import MetadataParserClient

with open("conf/conf.env", "r") as f:
# Reading conf.env configuration file
    config_string = "[DEFAULT]\n" + f.read()
config = configparser.ConfigParser()
config.read_string(config_string)

myclient = MetadataParserClient(config["DEFAULT"]["BASE_URL"], request_timeout=1)
myclient.auth_token = config["DEFAULT"]["TOKEN"]

# Creating empty nodes and edges lists
nodes = []
edges = []

# The service order helps analysis first "standalone" services and then connection services, this might be useful to parse first services which can be either source or sink of other services (e.g. Kafka connect might use a PG table as a source)

services_order = {}
services_order["opensearch"] = 1
services_order["elasticsearch"] = 1
services_order["pg"] = 1
services_order["redis"] = 1
services_order["mysql"] = 1
services_order["clickhouse"] = 1
services_order["cassandra"] = 1
services_order["redis"] = 1
services_order["m3db"] = 1
services_order["m3aggregator"] = 1
services_order["m3coordinator"] = 1

services_order["influxdb"] = 1
services_order["kafka"] = 2
services_order["kafka_connect"] = 3
services_order["kafka_mirrormaker"] = 3
services_order["flink"] = 3
services_order["grafana"] = 3


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
