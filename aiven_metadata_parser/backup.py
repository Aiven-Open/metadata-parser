"""Parsing service backups"""


def explore_backups(self, service_name, service_type, project):
    """Parsing service backups"""

    nodes = []
    edges = []

    backups = self.get_service_backups(service=service_name, project=project)
    for backup in backups:
        nodes.append(
            {
                "id": "service_type~"
                + service_type
                + "~service_name~"
                + service_name
                + "~backup~"
                + backup["backup_name"],
                "label": "backup-" + backup["backup_time"],
                "type": "backup",
                "service_type": service_type,
                **backup,
            }
        )
        edges.append(
            {
                "from": service_name,
                "label": "backup",
                "to": "service_type~"
                + service_type
                + "~service_name~"
                + service_name
                + "~backup~"
                + backup["backup_name"],
            }
        )
    return nodes, edges
