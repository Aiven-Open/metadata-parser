"""Parsing OpenSearch service"""


def explore_opensearch(self, service, service_name, project, service_map):
    """Explores an OpenSearch service"""
    nodes = []
    edges = []

    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]

    # Exploring Users

    new_nodes, new_edges, users = explore_opensearch_users(
        self, service_name, project
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    # Getting indexes

    new_nodes, new_edges, indexes = explore_opensearch_indexes(
        self, service_name, project
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    # tobedone parse more stuff
    # Getting ACLs

    new_nodes, new_edges = explore_opensearch_acls(
        self, service_name, project, users, indexes
    )
    nodes = nodes + new_nodes
    edges = edges + new_edges

    # tobedone: check how to parse everything when ACLs are set
    return host, port, nodes, edges, service_map


def explore_opensearch_users(self, service_name, project):
    """Explores an OpenSearch users"""
    nodes = []
    edges = []

    opensearch = self.get_service(project=project, service=service_name)

    # Exploring Users
    for user in opensearch["users"]:

        nodes.append(
            {
                "id": "opensearch~"
                + service_name
                + "~user~"
                + user["username"],
                "service_type": "opensearch",
                "type": "user",
                "user_type": user["type"],
                "label": user["username"],
            }
        )
        edges.append(
            {
                "from": "opensearch~"
                + service_name
                + "~user~"
                + user["username"],
                "to": service_name,
                "label": "user",
            }
        )
    return nodes, edges, opensearch["users"]


def explore_opensearch_indexes(self, service_name, project):
    """Explores an OpenSearch indexes"""
    nodes = []
    edges = []

    indexes = self.get_service_indexes(project=project, service=service_name)
    for index in indexes:

        # CReating node for index
        nodes.append(
            {
                "id": "opensearch~"
                + service_name
                + "~index~"
                + index["index_name"],
                "service_type": "opensearch",
                "type": "index",
                "label": index["index_name"],
                "health": index["health"],
                "replicas": index["number_of_replicas"],
                "shards": index["number_of_shards"],
            }
        )
        # Creating edge between index and service
        edges.append(
            {
                "from": "opensearch~"
                + service_name
                + "~index~"
                + index["index_name"],
                "to": service_name,
                "label": "index",
            }
        )
    return nodes, edges, indexes


def explore_opensearch_acls(self, service_name, project, users, indexes):
    """Explores an OpenSearch ACLs"""
    nodes = []
    edges = []

    acls = self.list_service_elasticsearch_acl_config(
        project=project, service=service_name
    )

    # If ACLs are not enabled create an edge between each user and each index
    if not acls["elasticsearch_acl_config"]["enabled"]:
        for user in users:
            for index in indexes:
                edges.append(
                    {
                        "from": "opensearch~"
                        + service_name
                        + "~index~"
                        + index["index_name"],
                        "to": "opensearch~"
                        + service_name
                        + "~user~"
                        + user["username"],
                        "label": "visibility_index",
                    }
                )
    return nodes, edges
