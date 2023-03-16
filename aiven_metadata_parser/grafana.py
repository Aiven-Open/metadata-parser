"""Parsing Grafana service"""

import json
import requests


def explore_grafana(service, service_name, service_map):
    """Parsing Grafana service"""

    nodes = []
    edges = []

    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]

    avnadmin_password = "fake"

    # Parse the users

    new_nodes, new_edges, avnadmin_password = explore_grafana_users(
        service, service_name
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    # Define the base URL
    base_url = "https://" + service["service_uri_params"]["host"] + ":443"
    auth = ("avnadmin", avnadmin_password)

    # Get datasources

    (
        new_nodes,
        new_edges,
        service_map,
        datasources_map,
    ) = explore_grafana_datasources(service_name, base_url, auth, service_map)
    nodes = nodes + new_nodes
    edges = edges + new_edges

    # getting dashboards

    new_nodes, new_edges = explore_grafana_dashboards(
        service_name, base_url, auth, avnadmin_password, datasources_map
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    return host, port, nodes, edges, service_map


def explore_grafana_users(service, service_name):
    """Parsing Grafana users"""

    nodes = []
    edges = []
    users = service["users"]

    for user in users:
        # Create node per user
        nodes.append(
            {
                "id": "grafana~" + service_name + "~user~" + user["username"],
                "user-type": user["type"],
                "service_type": "grafana",
                "type": "user",
                "label": user["username"],
            }
        )
        # Create edge between user and service
        edges.append(
            {
                "from": "grafana~"
                + service_name
                + "~user~"
                + user["username"],
                "to": service_name,
                "label": "user",
            }
        )

        # Take theavnadmin_password of the avnadmin user for further ispection
        if user["username"] == "avnadmin":
            avnadmin_password = user["password"]

    return nodes, edges, avnadmin_password


def explore_grafana_datasources(service_name, base_url, auth, service_map):
    """Parsing Grafana dashboards"""

    nodes = []
    edges = []

    datasources_map = {}
    datasources = requests.get(base_url + "/api/datasources", auth=auth)

    for datasource in json.loads(datasources.text):
        # Create a map of the datasources id -> name
        datasources_map[datasource["uid"]] = datasource["name"]
        # Create node per datasource
        nodes.append(
            {
                "id": "grafana~"
                + service_name
                + "~datasource~"
                + datasource["name"],
                "datasource-type": datasource["type"],
                "service_type": "grafana",
                "type": "datasource",
                "label": datasource["name"],
                "tgt_url": datasource["url"],
            }
        )
        # Create edge between datasource and service
        edges.append(
            {
                "from": "grafana~"
                + service_name
                + "~datasource~"
                + datasource["name"],
                "to": service_name,
                "label": "datasource",
            }
        )

        # Look for target host
        target_host = (
            datasource["url"]
            .replace("http://", "")
            .replace("https://", "")
            .split(":")[0]
        )

        # Check if the host in the list of target hosts already
        dest_service = service_map.get(target_host)
        # If host doesn't exist yet
        if dest_service is None:
            # Create new node for external service host
            nodes.append(
                {
                    "id": "ext-src-" + target_host,
                    "service_type": "ext-service",
                    "type": "external-service",
                    "label": target_host,
                }
            )
            service_map[target_host] = target_host
            # Create new edge between external service host and datasource
            edges.append(
                {
                    "from": "grafana~"
                    + service_name
                    + "~datasource~"
                    + datasource["name"],
                    "to": "ext-src-" + target_host,
                    "label": "datasource",
                }
            )
        else:
            # Create new edge between existing service host and datasource
            edges.append(
                {
                    "from": "grafana~"
                    + service_name
                    + "~datasource~"
                    + datasource["name"],
                    "to": dest_service,
                    "label": "datasource",
                }
            )

        # In case is PG
        if datasource["type"] == "postgres":
            if dest_service is None:
                # Creates a database node in the external service
                nodes.append(
                    {
                        "id": "ext-src-"
                        + dest_service
                        + "~db~"
                        + datasource["database"],
                        "service_type": "ext-pg",
                        "type": "database",
                        "label": datasource["database"],
                    }
                )
                # Creates an edge between the database and the datasource
                edges.append(
                    {
                        "from": "grafana~"
                        + service_name
                        + "~datasource~"
                        + datasource["name"],
                        "to": "ext-src-"
                        + dest_service
                        + "~db~"
                        + datasource["database"],
                        "label": "datasource",
                    }
                )
            else:
                # Creates an edge between the database and the datasource
                edges.append(
                    {
                        "from": "grafana~"
                        + service_name
                        + "~datasource~"
                        + datasource["name"],
                        "to": "pg~"
                        + dest_service
                        + "~database~"
                        + datasource["database"],
                        "label": "datasource",
                    }
                )
    return nodes, edges, service_map, datasources_map


def explore_grafana_dashboards(
    service_name, base_url, auth, avnadmin_password, datasources_map
):
    """Parsing Grafana dashboards"""

    nodes = []
    edges = []

    dashboards = requests.get(
        base_url + "/api/search?dash-folder",
        auth=auth,
    )

    for dashboard in json.loads(dashboards.text):
        # Creates a node for the dashboard
        nodes.append(
            {
                "id": "grafana~"
                + service_name
                + "~dashboard~"
                + dashboard["title"],
                "service_type": "grafana",
                "type": "dashboard",
                "label": dashboard["title"],
            }
        )
        # Creates an edge between service name and dashboard
        edges.append(
            {
                "from": "grafana~"
                + service_name
                + "~dashboard~"
                + dashboard["title"],
                "to": service_name,
                "label": "dashboard",
            }
        )
        # gets the dashboard details

        dashboard_details = requests.get(
            base_url + "/api/dashboards/uid/" + dashboard["uid"],
            auth=("avnadmin", avnadmin_password),
        )

        dash_details = json.loads(dashboard_details.text)
        # Adds edge between dashboard and creator
        edges.append(
            {
                "from": "grafana~"
                + service_name
                + "~dashboard~"
                + dashboard["title"],
                "to": "grafana~"
                + service_name
                + "~user~"
                + dash_details["meta"]["createdBy"],
                "type": "dashboard-creator",
                "label": "dashboard-creator",
            }
        )

        # A dashboard can have rows defined or not
        if dash_details["dashboard"].get("rows") is not None:
            for row in dash_details["dashboard"]["rows"]:
                # Looks for panels in the dashboard
                for panel in row["panels"]:

                    if isinstance(panel["datasource"], str):
                        datasource = panel["datasource"]
                        # Creates an edge between the dashboard and datasource
                        edges.append(
                            {
                                "from": "grafana~"
                                + service_name
                                + "~dashboard~"
                                + dashboard["title"],
                                "to": "grafana~"
                                + service_name
                                + "~datasource~"
                                + datasource,
                                "label": "dashboard datasource",
                            }
                        )
                    else:
                        datasource = panel["datasource"]["uid"]
                        # Creates an edge between the dashboard and datasource
                        edges.append(
                            {
                                "from": "grafana~"
                                + service_name
                                + "~dashboard~"
                                + dashboard["title"],
                                "to": "grafana~"
                                + service_name
                                + "~datasource~"
                                + datasources_map[datasource],
                                "label": "dashboard datasource",
                            }
                        )
                    # tobedone explore all columns in a dashboard panel
        else:
            for panel in dash_details["dashboard"]["panels"]:
                if isinstance(panel["datasource"], str):
                    datasource = panel["datasource"]
                    # Creates an edge between the dashboard and datasource
                    edges.append(
                        {
                            "from": "grafana~"
                            + service_name
                            + "~dashboard~"
                            + dashboard["title"],
                            "to": "grafana~"
                            + service_name
                            + "~datasource~"
                            + datasource,
                            "label": "dashboard datasource",
                        }
                    )
                elif isinstance(panel["datasource"], dict):
                    datasource = panel["datasource"]["uid"]
                    # Creates an edge between the dashboard and datasource
                    edges.append(
                        {
                            "from": "grafana~"
                            + service_name
                            + "~dashboard~"
                            + dashboard["title"],
                            "to": "grafana~"
                            + service_name
                            + "~datasource~"
                            + datasources_map[datasource],
                            "label": "dashboard datasource",
                        }
                    )
    return nodes, edges
