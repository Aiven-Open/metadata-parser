"""Parsing service tags"""


def explore_tags(self, service_name, service_type, project):
    """Parsing service tags"""

    nodes = []
    edges = []

    tags = self.list_service_tags(service=service_name, project=project)

    for key, value in tags["tags"].items():
        nodes.append(
            {
                "id": "tag~id~" + key + "~value~" + value,
                "service_type": "tag",
                "type": "tag",
                "label": key + "=" + value,
            }
        )
        edges.append(
            {
                "from": service_name,
                "to": "tag~id~" + key + "~value~" + value,
                "label": "tag",
            }
        )
    return nodes, edges
