"""Parsing service integration"""


def explore_integrations(self, service_name, service_type, project):
    """Parsing service intergration"""

    nodes = []
    edges = []

    integrations = self.get_service_integrations(
        service=service_name, project=project
    )
    for integration in integrations:
        if integration["enabled"] is True:

            edges.append(
                {
                    "from": integration["source_service"],
                    "to": integration["dest_service"],
                    "main_type": "integration",
                    "integration_type": integration["integration_type"],
                    "label": integration["integration_type"],
                    "integration_id": integration["service_integration_id"],
                }
            )

    return nodes, edges
