"""Parsing Apache Kafka® services"""

import re
from aiven_metadata_parser import kafka_connect


def explore_kafka(self, service, service_name, project, service_map):
    """Explores an Apache Kafka service"""
    nodes = []
    edges = []
    host = service["service_uri_params"]["host"]
    kafka = self.get_service(project=project, service=service_name)

    new_nodes, new_edges, topic_list = explore_kafka_topics(
        self, service_name, project
    )

    nodes = nodes + new_nodes
    edges = edges + new_edges

    new_nodes, new_edges = explore_kafka_users(self, service_name, project)

    nodes = nodes + new_nodes
    edges = edges + new_edges

    new_nodes, new_edges = explore_kafka_acls(
        self, service_name, project, topic_list
    )

    nodes = nodes + new_nodes
    edges = edges + new_edges

    # tbd parse schemas

    # If the service has Kafka connect, we can explore it as well
    if kafka["user_config"]["kafka_connect"] is True:
        (
            _,
            _,
            new_nodes,
            new_edges,
            service_map,
        ) = kafka_connect.explore_kafka_connect(
            self, None, service_name, project, service_map
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

    return host, service, nodes, edges, service_map


def explore_kafka_topics(self, service_name, project):
    """get Kafka topics"""
    nodes = []
    edges = []
    topic_list = []

    topics = self.list_service_topics(service=service_name, project=project)

    # Exploring Topics
    for topic in topics:

        topic_infos = self.get_service_topic(
            project=project, service=service_name, topic=topic["topic_name"]
        )

        nodes.append(
            {
                "id": "kafka~"
                + service_name
                + "~topic~"
                + topic["topic_name"],
                "service_type": "kafka",
                "type": "topic",
                "cleanup_policy": topic["cleanup_policy"],
                "label": topic["topic_name"],
                "partitions": topic_infos.get("partitions"),
                "min_insync_replicas": topic_infos.get("min_insync_replicas"),
                "replication": topic_infos.get("replication"),
                "retention_bytes": topic_infos.get("retention_bytes"),
                "retention_hours": topic_infos.get("retention_hours"),
                "state": topic_infos.get("state"),
                "config": topic_infos.get("config"),
            }
        )
        edges.append(
            {
                "from": "kafka~"
                + service_name
                + "~topic~"
                + topic["topic_name"],
                "to": service_name,
                "label": "topic",
            }
        )
        topic_list.append(topic["topic_name"])

        new_nodes, new_edges = explore_kafka_topic_partitions(
            service_name, topic["topic_name"], topic_infos["partitions"]
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges

        for tag in topic["tags"]:
            nodes.append(
                {
                    "id": "tag~id~" + tag["key"] + "~value~" + tag["value"],
                    "service_type": "tag",
                    "type": "tag",
                    "label": tag["key"] + "=" + tag["value"],
                }
            )
            edges.append(
                {
                    "from": "kafka~"
                    + service_name
                    + "~topic~"
                    + topic["topic_name"],
                    "to": "tag~id~" + tag["key"] + "~value~" + tag["value"],
                    "label": "tag",
                }
            )
    return nodes, edges, topic_list


def explore_kafka_users(self, service_name, project):
    """Get Kafka users"""
    nodes = []
    edges = []
    kafka = self.get_service(project=project, service=service_name)

    # Exploring Users
    for user in kafka["users"]:

        nodes.append(
            {
                "id": "kafka~" + service_name + "~user~" + user["username"],
                "service_type": "kafka",
                "type": "user",
                "user_type": user["type"],
                "label": user["username"],
            }
        )
        edges.append(
            {
                "from": "kafka~" + service_name + "~user~" + user["username"],
                "to": service_name,
                "label": "user",
            }
        )
    return nodes, edges


def explore_kafka_acls(self, service_name, project, topic_list):
    """Getting Kafka ACLs"""
    nodes = []
    edges = []
    kafka = self.get_service(project=project, service=service_name)

    # Exploring ACLs
    for acl in kafka["acl"]:
        # Create node for ACL
        nodes.append(
            {
                "id": "kafka~" + service_name + "~acl~" + acl["id"],
                "service_type": "kafka",
                "type": "topic-acl",
                "permission": acl["permission"],
                "label": acl["id"],
                "topic": acl["topic"],
                "username": acl["username"],
            }
        )
        # Create edge between ACL and username
        edges.append(
            {
                "from": "kafka~" + service_name + "~user~" + acl["username"],
                "to": "kafka~" + service_name + "~acl~" + acl["id"],
                "label": "user",
            }
        )
        # Map topics that an ACL shows
        for topic in topic_list:
            strtomatch = acl["topic"]
            if strtomatch == "*":
                strtomatch = ".*"
            # Checking if the ACL string matches a topic
            # ACL strings are defined with Java RegExp
            # and we're parsing them with Python,
            # maybe something to improve here?
            if re.match(strtomatch, topic):
                edges.append(
                    {
                        "from": "kafka~" + service_name + "~acl~" + acl["id"],
                        "to": "kafka~" + service_name + "~topic~" + topic,
                        "label": "topic-acl",
                    }
                )
    return nodes, edges


def explore_kafka_topic_partitions(service_name, topic_name, partitions):
    """Getting Kafka topic partitions"""
    nodes = []
    edges = []

    # Exploring partitions
    for partition in partitions:
        # Create node for partition

        nodes.append(
            {
                "id": "kafka~"
                + service_name
                + "~topic~"
                + topic_name
                + "~partition~"
                + str(partition["partition"]),
                "service_type": "kafka",
                "type": "partition",
                "earliest_offset": partition["earliest_offset"],
                "isr": partition["isr"],
                "latest_offset": partition["latest_offset"],
                "size": partition["size"],
                "label": "Partition " + str(partition["partition"]),
            }
        )

        # Create edge between partition and topic
        edges.append(
            {
                "from": "kafka~"
                + service_name
                + "~topic~"
                + topic_name
                + "~partition~"
                + str(partition["partition"]),
                "to": "kafka~" + service_name + "~topic~" + topic_name,
                "label": "partition",
            }
        )

        new_nodes, new_edges = explore_kafka_topic_partitions_consumer_groups(
            service_name,
            topic_name,
            partition["partition"],
            partition["consumer_groups"],
        )
        nodes = nodes + new_nodes
        edges = edges + new_edges
    return nodes, edges


def explore_kafka_topic_partitions_consumer_groups(
    service_name, topic_name, partition, consumers
):
    """Getting Kafka topic partitions consumer group info"""
    nodes = []
    edges = []

    # Exploring partitions
    for consumer in consumers:
        # Create node for partition
        nodes.append(
            {
                "id": "kafka~"
                + service_name
                + "~topic~"
                + topic_name
                + "~partition~"
                + str(partition)
                + "~consumer_group~"
                + consumer["group_name"],
                "offset": consumer["offset"],
                "label": consumer["group_name"],
                "type": "consumer_group",
                "service_type": "kafka",
            }
        )
        # Create edge between partition and username
        edges.append(
            {
                "from": "kafka~"
                + service_name
                + "~topic~"
                + topic_name
                + "~partition~"
                + str(partition)
                + "~consumer_group~"
                + consumer["group_name"],
                "to": "kafka~"
                + service_name
                + "~topic~"
                + topic_name
                + "~partition~"
                + str(partition),
                "label": "Consumer group:" + consumer["group_name"],
            }
        )
    return nodes, edges
