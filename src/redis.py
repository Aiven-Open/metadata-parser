"""Parsing Redis service"""


def explore_redis(self, service, service_name, project, service_map):
    """Explores an Redis service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    port = service["service_uri_params"]["port"]

    # Exploring Users and ACL
    for user in service["users"]:

        user_node_id = f"redis~{service_name}~user~{user['username']}"

        nodes.append(
            {
                "id": user_node_id,
                "service_type": "redis",
                "type": "user",
                "user_type": user["type"],
                "label": user["username"],
            }
        )
        edges.append(
            {"from": user_node_id, "to": service_name, "label": "user"}
        )

        user_acl_info = user["access_control"]
        acl_node_id = f"redis~user-acl~id~{user['username']}"

        nodes.append(
            {
                "id": acl_node_id,
                "service_type": "user-acl",
                "type": "acl",
                "label": user["username"] + "-user-acl",
                "access_control": user_acl_info,
            }
        )
        edges.append({"from": user_node_id, "to": acl_node_id, "label": "acl"})

    # need to finish Could query redis and add more parsed data from that
    return host, port, nodes, edges, service_map
